import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import tempfile
from supabase import Client, create_client
from postgrest import SyncPostgrestClient

@st.cache_resource
def init_connection():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )

import httpx

http_client = httpx.Client(timeout=20.0)

st.set_page_config(
    page_title="Forensic Web Monitor | UCV",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 15% 20%, rgba(59,130,246,0.16), transparent 24%),
        radial-gradient(circle at 85% 15%, rgba(16,185,129,0.14), transparent 28%),
        radial-gradient(circle at 50% 80%, rgba(139,92,246,0.14), transparent 30%),
        linear-gradient(180deg, #F8FAFC 0%, #EEF4FF 100%);
    color: #0F172A;
}

[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(24px);
    border-right: 1px solid rgba(255,255,255,0.35);
    box-shadow: 6px 0 40px rgba(15,23,42,0.04);
}

[data-testid="stSidebar"] * {
    color: #0F172A !important;
}

.block-container {
    max-width: 1600px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 8px;
    padding-bottom: 28px;
}

fig_latencia.update_layout(
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor="rgba(255,255,255,0)",
)

.js-plotly-plot,
.plot-container,
svg.main-svg {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.brand-wrap {
    display: flex;
    align-items: center;
    gap: 14px;
}

.brand-logo {
    display: flex;
    align-items: center;
    justify-content: center;
}

.brand-logo svg {
    filter:
        drop-shadow(0 0 18px rgba(79,70,229,0.28))
        drop-shadow(0 0 32px rgba(6,182,212,0.16));
}

.brand-text {
    font-size: 2rem;
    font-weight: 950;
    letter-spacing: -0.07em;
    color: #0F172A;
}

.brand-badge {
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(79,70,229,0.08);
    color: #4F46E5;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: .08em;
}
.executive-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(180px, 1fr));
    gap: 18px;
    margin: 22px 0 30px 0;
}

.metric-card {
    position: relative;
    padding: 22px;
    border-radius: 22px;
    background: rgba(255,255,255,0.88);
    border: 1px solid rgba(15,23,42,0.07);
    box-shadow: 0 8px 24px rgba(15,23,42,0.045);
    transition: all .18s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 34px rgba(15,23,42,0.08);
}

.metric-icon {
    font-size: 1.45rem;
    margin-bottom: 12px;
}

.metric-label {
    font-size: .76rem;
    font-weight: 850;
    letter-spacing: .05em;
    color: #64748B;
    text-transform: uppercase;
}

.metric-value {
    margin-top: 8px;
    font-size: 2.15rem;
    font-weight: 950;
    letter-spacing: -0.06em;
    color: #0F172A;
}

.metric-note {
    margin-top: 9px;
    font-size: .82rem;
    color: #64748B;
    line-height: 1.35;
}

.section-title {
    margin-top: 26px;
    margin-bottom: 10px;
    font-size: 1.65rem;
    font-weight: 900;
    letter-spacing: -0.05em;
}

.section-subtitle {
    color: #64748B;
    font-size: 0.98rem;
    margin-bottom: 18px;
}

[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(15,23,42,0.06);
}

.stButton > button,
.stDownloadButton > button {
    width: 100%;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.25);
    background:
        linear-gradient(
            135deg,
            rgba(79,70,229,0.88),
            rgba(6,182,212,0.88)
        );
    color: white;
    font-weight: 700;
    letter-spacing: -.02em;
    padding: .9rem 1rem;
    box-shadow:
        0 10px 30px rgba(79,70,229,0.18),
        inset 0 1px 1px rgba(255,255,255,0.18);
    transition: all .18s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-2px);
    box-shadow:
        0 16px 38px rgba(79,70,229,0.28),
        inset 0 1px 1px rgba(255,255,255,0.22);
}

.js-plotly-plot {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

html, body, [class*="css"] {
    font-family: Inter, ui-sans-serif, system-ui, sans-serif;
}

h1,h2,h3 {
    letter-spacing: -0.05em;
}

[data-testid="stDataFrame"] {
    border-radius: 20px;
    overflow: hidden;
    border: 1px solid rgba(15,23,42,0.08);
    box-shadow: 0 10px 28px rgba(15,23,42,0.045);
    background: rgba(255,255,255,0.72);
}

[data-testid="stDataFrame"] div {
    font-size: 0.92rem;
}

section[data-testid="stSidebar"] {
    min-width: 290px !important;
    width: 290px !important;
}

.main .block-container {
    max-width: 100% !important;
    padding-left: 3rem;
    padding-right: 3rem;
    transition: all .2s ease;
}

section[data-testid="stSidebar"][aria-expanded="false"] + div .block-container {
    padding-left: 2rem;
    max-width: 96%;
}

</style>
""", unsafe_allow_html=True)


class ReporteForensePDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "REPORTE DE AUDITORIA FORENSE DE INFRAESTRUCTURA", 0, 1, "C")
        self.set_font("Arial", "I", 10)
        self.cell(0, 10, f"Generado el: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", 0, 1, "C")
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, "C")


def generar_pdf_bytes(df_fallos, uptime, total_incidentes):
    pdf = ReporteForensePDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. RESUMEN EJECUTIVO", 0, 1)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        8,
        f"Durante el periodo analizado, la infraestructura presento un Uptime global del {uptime:.2f}%. "
        f"Se detectaron {total_incidentes} incidentes criticos.",
    )
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. BITACORA DE INCIDENTES CRITICOS", 0, 1)

    pdf.set_font("Arial", "B", 9)
    pdf.cell(45, 8, "Timestamp UTC", 1)
    pdf.cell(75, 8, "Endpoint", 1)
    pdf.cell(20, 8, "HTTP", 1)
    pdf.cell(50, 8, "Detalle", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 8)
    for _, row in df_fallos.head(50).iterrows():
        fecha_str = str(row.get("timestamp", "")).split(".")[0]
        url = str(row.get("url", "")).replace("https://", "")
        url_corta = url[:35] + "..." if len(url) > 35 else url
        http_code = str(int(row["http_code"])) if pd.notna(row.get("http_code")) else "DNS/TLS"
        error_type = str(row.get("error_type", ""))[:30]

        pdf.cell(45, 8, fecha_str, 1)
        pdf.cell(75, 8, url_corta, 1)
        pdf.cell(20, 8, http_code, 1)
        pdf.cell(50, 8, error_type, 1)
        pdf.ln()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            return f.read()


@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


@st.cache_data(ttl=300)
def load_data():
    try:
        response = (
            init_connection()
            .table("incidentes")
            .select("""
                timestamp,
                url,
                http_code,
                latency_ms,
                error_type,
                screenshot_url,
                content_hash,
                ssl_issuer,
                ssl_expiry
            """)
            .order("timestamp", desc=True)
            .limit(500)
            .execute()
        )

        df = pd.DataFrame(response.data)

        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df["latency_ms"] = pd.to_numeric(df["latency_ms"], errors="coerce").fillna(0)
            df["http_code"] = pd.to_numeric(df["http_code"], errors="coerce")

        return df

    except Exception as e:
        st.error("Aurora no pudo conectarse con la bóveda forense.")
        st.exception(e)
        return pd.DataFrame()


def short_url(url: str, max_len: int = 58) -> str:
    if not isinstance(url, str):
        return ""
    cleaned = url.replace("https://", "").replace("http://", "")
    return cleaned if len(cleaned) <= max_len else cleaned[:max_len] + "..."


def classify_latency(ms: float) -> str:
    if ms < 1000:
        return "Sana"
    if ms < 3000:
        return "Degradada"
    return "Crítica"


st.markdown("""
<div class="topbar">
  <div class="brand-wrap">
    <div class="brand-logo">
      <svg width="34" height="34" viewBox="0 0 64 64" fill="none">
        <defs>
          <linearGradient id="g" x1="8" y1="8" x2="56" y2="56">
            <stop offset="0%" stop-color="#4F46E5"/>
            <stop offset="55%" stop-color="#06B6D4"/>
            <stop offset="100%" stop-color="#10B981"/>
          </linearGradient>
        </defs>
        <rect x="6" y="6" width="52" height="52" rx="16" fill="url(#g)"/>
        <path d="M18 39C23 22 41 22 46 39" stroke="white" stroke-width="5" stroke-linecap="round"/>
        <circle cx="32" cy="32" r="5" fill="white"/>
      </svg>
    </div>
    <div class="brand-text">Aurora</div>
    <div class="brand-badge">LIVE MONITORING</div>
  </div>
</div>
""", unsafe_allow_html=True)


df = load_data()

if df.empty:
    st.warning("Aún no hay suficientes datos en la bóveda forense.")
    st.stop()

st.sidebar.header("Filtros de Auditoría")

endpoints_disponibles = sorted(df["url"].dropna().unique().tolist())
endpoint_seleccionado = st.sidebar.selectbox("Seleccionar Plataforma:", ["Todas"] + endpoints_disponibles)

if endpoint_seleccionado != "Todas":
    df_filtrado = df[df["url"] == endpoint_seleccionado].copy()
else:
    df_filtrado = df.copy()

section = st.sidebar.segmented_control(
    "Navegación",
    ["Resumen Ejecutivo", "Latencia", "Incidentes", "Evidencia Forense"],
)

df_filtrado["is_fail"] = (
    (df_filtrado["http_code"] >= 400)
    | (df_filtrado["http_code"].isna())
    | (df_filtrado["error_type"].fillna("OK") != "OK")
)

total_checks = len(df_filtrado)
df_fallos = df_filtrado[df_filtrado["is_fail"]].copy()
total_fallos = len(df_fallos)

uptime_porcentaje = 100.0 if total_checks == 0 else ((total_checks - total_fallos) / total_checks) * 100
latencia_promedio = df_filtrado["latency_ms"].mean() if total_checks else 0
ventana_inicio = df_filtrado["timestamp"].min()
ventana_fin = df_filtrado["timestamp"].max()

df_servicios = (
    df_filtrado.groupby("url")
    .agg(
        muestras=("url", "count"),
        fallos=("is_fail", "sum"),
        latencia_promedio=("latency_ms", "mean"),
        latencia_maxima=("latency_ms", "max"),
        evidencia=("screenshot_url", lambda x: x.notna().sum()),
    )
    .reset_index()
)

df_servicios["uptime"] = ((df_servicios["muestras"] - df_servicios["fallos"]) / df_servicios["muestras"]) * 100
df_servicios["health_score"] = (
    df_servicios["uptime"] * 0.7
    + (100 - (df_servicios["latencia_promedio"].clip(0, 5000) / 5000 * 100)) * 0.3
).clip(0, 100)

servicio_mas_caido = df_servicios.sort_values("uptime").iloc[0]
servicio_mas_lento = df_servicios.sort_values("latencia_promedio", ascending=False).iloc[0]
servicio_mas_saludable = df_servicios.sort_values("health_score", ascending=False).iloc[0]
servicio_mas_evidencia = df_servicios.sort_values("evidencia", ascending=False).iloc[0]

st.sidebar.markdown("---")
st.sidebar.subheader("Exportar Evidencia")

if not df_fallos.empty:
    pdf_bytes = generar_pdf_bytes(df_fallos, uptime_porcentaje, total_fallos)
    st.sidebar.download_button(
        label="📥 Descargar Reporte PDF",
        data=pdf_bytes,
        file_name=f"Auditoria_UCV_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
    )

if st.sidebar.button("🔄 Forzar Actualización de Datos"):
    load_data.clear()
    st.rerun()


if section == "Resumen Ejecutivo":
    st.markdown('<div class="section-title">Gobierno Ejecutivo de Disponibilidad</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Vista consolidada para entender disponibilidad, criticidad, evidencia y salud operativa.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"""
<div class="executive-grid">

<div class="metric-card" title="Porcentaje de verificaciones exitosas dentro del periodo analizado. Excluye errores HTTP, DNS, TLS y errores registrados.">
<div class="metric-icon">🟢</div>
<div class="metric-label">Disponibilidad</div>
<div class="metric-value">{uptime_porcentaje:.2f}%</div>
<div class="metric-note">Ventana: {ventana_inicio.strftime('%Y-%m-%d %H:%M')} → {ventana_fin.strftime('%Y-%m-%d %H:%M')} UTC</div>
</div>

<div class="metric-card" title="Eventos clasificados como error HTTP, DNS, TLS, timeout, caída o degradación funcional.">
<div class="metric-icon">🚨</div>
<div class="metric-label">Incidentes</div>
<div class="metric-value">{total_fallos}</div>
<div class="metric-note">Fallos sobre {total_checks} verificaciones registradas.</div>
</div>

<div class="metric-card" title="Tiempo promedio de respuesta de los endpoints monitoreados. Sobre 3000 ms indica degradación crítica.">
<div class="metric-icon">⚡</div>
<div class="metric-label">Latencia promedio</div>
<div class="metric-value">{latencia_promedio:.0f} ms</div>
<div class="metric-note">Estado: {classify_latency(latencia_promedio)}. &lt;1000 sano · 1000-3000 degradado · &gt;3000 crítico.</div>
</div>

<div class="metric-card" title="Número total de observaciones técnicas registradas. A mayor muestra, mayor fuerza temporal del análisis.">
<div class="metric-icon">📡</div>
<div class="metric-label">Muestras</div>
<div class="metric-value">{total_checks}</div>
<div class="metric-note">Registros acumulados en la bóveda técnica.</div>
</div>

</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Diagnóstico Operacional</div>', unsafe_allow_html=True)

    st.markdown(f"""
<div class="executive-grid">

<div class="metric-card" title="Servicio con menor disponibilidad registrada.">
<div class="metric-icon">🔴</div>
<div class="metric-label">Servicio más caído</div>
<div class="metric-value">{servicio_mas_caido['uptime']:.1f}%</div>
<div class="metric-note">{short_url(servicio_mas_caido['url'])}</div>
</div>

<div class="metric-card" title="Servicio con mayor latencia promedio. Indica degradación aunque responda HTTP 200.">
<div class="metric-icon">🐢</div>
<div class="metric-label">Servicio más lento</div>
<div class="metric-value">{servicio_mas_lento['latencia_promedio']:.0f} ms</div>
<div class="metric-note">{short_url(servicio_mas_lento['url'])}</div>
</div>

<div class="metric-card" title="Servicio con mejor combinación de disponibilidad y latencia.">
<div class="metric-icon">✅</div>
<div class="metric-label">Mejor salud</div>
<div class="metric-value">{servicio_mas_saludable['health_score']:.0f}/100</div>
<div class="metric-note">{short_url(servicio_mas_saludable['url'])}</div>
</div>

<div class="metric-card" title="Servicio con mayor volumen de evidencia forense asociada.">
<div class="metric-icon">🧾</div>
<div class="metric-label">Mayor evidencia</div>
<div class="metric-value">{int(servicio_mas_evidencia['evidencia'])}</div>
<div class="metric-note">{short_url(servicio_mas_evidencia['url'])}</div>
</div>

</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Salud por Servicio</div>', unsafe_allow_html=True)

    df_health = df_servicios.copy()
    df_health["uptime"] = df_health["uptime"].round(2)
    df_health["health_score"] = df_health["health_score"].round(1)
    df_health["latencia_promedio"] = df_health["latencia_promedio"].round(0)
    df_health["latencia_maxima"] = df_health["latencia_maxima"].round(0)

    st.markdown(df.to_html(
        df_health[
            [
                "url",
                "uptime",
                "health_score",
                "muestras",
                "fallos",
                "latencia_promedio",
                "latencia_maxima",
                "evidencia",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    ), unsafe_allow_html=True)

elif section == "Latencia":
    st.markdown('<div class="section-title">Evolución de Tiempos de Respuesta</div>', unsafe_allow_html=True)

    fig_latencia = px.line(
        df_filtrado.sort_values("timestamp"),
        x="timestamp",
        y="latency_ms",
        color="url",
        template="simple_white",
        markers=True,
    )
    
    fig_latencia.update_traces(
        line=dict(width=3.2),
        marker=dict(size=7, line=dict(width=1.5, color="white")),
    )
    
    fig_latencia.update_layout(
        height=560,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0F172A", size=13),
        hovermode="x unified",
        xaxis=dict(
            title="",
            showgrid=False,
            zeroline=False,
            tickfont=dict(color="#64748B"),
        ),
        yaxis=dict(
            title="Latencia (ms)",
            showgrid=True,
            gridcolor="rgba(100,116,139,0.18)",
            zeroline=False,
            tickfont=dict(color="#64748B"),
        ),
        legend=dict(
            title="",
            orientation="h",
            yanchor="bottom",
            y=1.08,
            xanchor="left",
            x=0,
            bgcolor="rgba(255,255,255,0)",
            font=dict(size=12, color="#334155"),
        ),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    fig_latencia.add_hline(
        y=3000,
        line_dash="dash",
        line_color="rgba(239,68,68,0.45)",
        annotation_text="Umbral crítico 3000 ms",
        annotation_position="top left",
    )
    st.plotly_chart(fig_latencia, use_container_width=True)

elif section == "Incidentes":
    st.markdown(
        '<div class="section-title">Bitácora de Fallos y Tiempos de Inactividad</div>',
        unsafe_allow_html=True
    )

    if df_fallos.empty:
        st.success("No se han registrado fallos para los filtros seleccionados.")
    else:
        df_fallos_view = (
            df_fallos[["timestamp", "url", "http_code", "latency_ms", "error_type"]]
            .sort_values(by="timestamp", ascending=False)
            .copy()
        )

        df_fallos_view["timestamp"] = df_fallos_view["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        df_fallos_view["url"] = df_fallos_view["url"].apply(lambda x: short_url(x, 70))
        df_fallos_view["http_code"] = df_fallos_view["http_code"].apply(
            lambda x: "DNS/TLS" if pd.isna(x) else str(int(x))
        )
        df_fallos_view["latency_ms"] = df_fallos_view["latency_ms"].astype(int).astype(str) + " ms"

        df_fallos_view = df_fallos_view.rename(columns={
            "timestamp": "Fecha",
            "url": "Servicio",
            "http_code": "Código",
            "latency_ms": "Latencia",
            "error_type": "Evento"
        })

        st.markdown(df.to_html(
            df_fallos_view,
            use_container_width=True,
            hide_index=True,
            height=520,
        ), unsafe_allow_html=True)

elif section == "Evidencia Forense":
    st.markdown(
        '<div class="section-title">Auditoría de Integridad y Certificados</div>',
        unsafe_allow_html=True
    )

    df_evidencia_view = (
        df_filtrado[["timestamp", "url", "content_hash", "ssl_issuer", "ssl_expiry", "screenshot_url"]]
        .sort_values(by="timestamp", ascending=False)
        .copy()
    )

    df_evidencia_view["timestamp"] = df_evidencia_view["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    df_evidencia_view["url"] = df_evidencia_view["url"].apply(lambda x: short_url(x, 70))
    df_evidencia_view["content_hash"] = df_evidencia_view["content_hash"].fillna("Sin hash").apply(
        lambda x: x[:18] + "..." if isinstance(x, str) and len(x) > 18 else x
    )
    df_evidencia_view["ssl_issuer"] = df_evidencia_view["ssl_issuer"].fillna("No disponible").apply(
        lambda x: x[:50] + "..." if isinstance(x, str) and len(x) > 50 else x
    )
    df_evidencia_view["ssl_expiry"] = df_evidencia_view["ssl_expiry"].fillna("No disponible")
    df_evidencia_view["screenshot_url"] = df_evidencia_view["screenshot_url"].fillna("Sin captura")

    df_evidencia_view = df_evidencia_view.rename(columns={
        "timestamp": "Fecha",
        "url": "Servicio",
        "content_hash": "Hash SHA256",
        "ssl_issuer": "Emisor SSL",
        "ssl_expiry": "Expira SSL",
        "screenshot_url": "Evidencia"
    })

    st.markdown(df.to_html(
        df_evidencia_view,
        use_container_width=True,
        hide_index=True,
        height=520,
    ), unsafe_allow_html=True)
