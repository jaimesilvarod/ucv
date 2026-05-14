import os
import asyncio
import httpx
import time
import hashlib
import socket
import ssl
import json
from datetime import datetime, timezone
from playwright.async_api import async_playwright
from supabase import create_client

supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
os.makedirs("evidence", exist_ok=True)

ENDPOINTS = [
    "https://trilce.ucv.edu.pe",
    "https://campusalumno.azurewebsites.net/plan-estudio/",
    "https://ucvapi.azure-api.net/auth-trilceprincipal/pr/api/Principal/ObtenerPersona?showSpinner=false",
    "https://ucv.blackboard.com",
    "https://ucv.edu.pe"
]

def check_ssl(hostname):
    """Extrae la información del certificado SSL."""
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                return cert.get('notAfter'), str(cert.get('issuer'))
    except Exception:
        return None, None

async def check_site(url):
    start_time = time.perf_counter()
    hostname = httpx.URL(url).host
    
    # Recolección de datos base
    result = {
        "url": url,
        "http_code": None,
        "latency_ms": 0,
        "error_type": "OK",
        "content_hash": None,
        "ssl_expiry": None,
        "ssl_issuer": None,
        "headers_dump": {},
        "screenshot_url": None
    }
    
    # Check SSL
    result["ssl_expiry"], result["ssl_issuer"] = check_ssl(hostname)
    
    incident = False
    html_content = ""
    
    try:
        async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
            resp = await client.get(url, follow_redirects=True)
            result["http_code"] = resp.status_code
            result["latency_ms"] = int((time.perf_counter() - start_time) * 1000)
            result["headers_dump"] = dict(resp.headers)
            
            # Hash criptográfico del contenido
            content_bytes = resp.content
            result["content_hash"] = hashlib.sha256(content_bytes).hexdigest()
            html_content = resp.text
            
            if result["http_code"] >= 400 or result["latency_ms"] > 3000:
                incident = True
                result["error_type"] = f"HTTP {result['http_code']} o Latencia Alta"
                
    except Exception as e:
        incident = True
        result["error_type"] = str(e)
        
    if incident:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        safe_name = url.replace('https://', '').split('/')[0]
        shot_path = f"evidence/{ts}_{safe_name}.png"
        html_path = f"evidence/{ts}_{safe_name}.html"
        
        # Volcado del HTML para diffs posteriores
        if html_content:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        
        # Fotografía forense con Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                await page.goto(url, timeout=15000)
                await page.screenshot(path=shot_path, full_page=True)
                result["screenshot_url"] = shot_path
            except Exception:
                pass 
            finally:
                await browser.close()
                
    # Guardar todo en la bóveda
    supabase.table("incidentes").insert(result).execute()
    print(f"[{result['http_code']}] {url} - {result['latency_ms']}ms - {result['error_type']}")

async def main():
    await asyncio.gather(*(check_site(url) for url in ENDPOINTS))

if __name__ == "__main__":
    asyncio.run(main())
