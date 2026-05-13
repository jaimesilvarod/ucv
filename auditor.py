import os
import asyncio
import httpx
import time
from datetime import datetime, timezone
from playwright.async_api import async_playwright
from supabase import create_client

# Configuración de Supabase
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

# Crear carpeta de evidencia temporal
os.makedirs("evidence", exist_ok=True)

ENDPOINTS = [
    "https://trilce.ucv.edu.pe",
    "https://campusalumno.azurewebsites.net/plan-estudio/",
    "https://ucv.blackboard.com"
]

async def check_site(url):
    start_time = time.perf_counter()
    incident = False
    http_code = None
    error_msg = None
    
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            resp = await client.get(url, follow_redirects=True)
            http_code = resp.status_code
            latency = int((time.perf_counter() - start_time) * 1000)
            if http_code >= 400 or latency > 5000:
                incident = True
                error_msg = f"HTTP {http_code} o Latencia Alta"
    except Exception as e:
        incident = True
        latency = 0
        error_msg = str(e)
        
    if incident:
        # Tomar evidencia forense
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"evidence/{ts}_{url.replace('https://', '').split('/')[0]}.png"
            
            try:
                await page.goto(url, timeout=15000)
                await page.screenshot(path=filename, full_page=True)
            except Exception:
                pass # Si ni siquiera carga, falla silencioso la foto
            finally:
                await browser.close()
                
        # Guardar en base de datos
        supabase.table("incidentes").insert({
            "url": url,
            "http_code": http_code,
            "latency_ms": latency,
            "error_type": error_msg,
            "screenshot_url": filename # Aquí indicamos el nombre del archivo guardado en los artifacts de GitHub
        }).execute()
        print(f"INCIDENTE REGISTRADO: {url} - {error_msg}")
    else:
        print(f"OK: {url} - {latency}ms")

async def main():
    await asyncio.gather(*(check_site(url) for url in ENDPOINTS))

if __name__ == "__main__":
    asyncio.run(main())
