import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import tempfile

st.set_page_config(
    page_title="Aurora",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={}
)

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 15% 18%, rgba(59,130,246,.18), transparent 24%),
        radial-gradient(circle at 82% 10%, rgba(16,185,129,.16), transparent 28%),
        radial-gradient(circle at 55% 82%, rgba(139,92,246,.16), transparent 32%),
        linear-gradient(180deg, #F8FAFC 0%, #EEF4FF 100%);
    color: #0F172A;
}
section[data-testid="stSidebar"] { display:none !important; }
.block-container {
    max-width: 100% !important;
    padding: 2.2rem 4rem 5rem 4rem;
}
.topbar {
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin-bottom:2.2rem;
}
.brand-wrap {
    display:flex;
    align-items:center;
    gap:14px;
}
.brand-logo svg {
    filter: drop-shadow(0 0 18px rgba(79,70,229,.28))
            drop-shadow(0 0 32px rgba(6,182,212,.16));
}
.brand-text {
    font-size:2rem;
    font-weight:950;
    letter-spacing:-.07em;
    color:#0F172A;
}
.brand-badge {
    padding:7px 13px;
    border-radius:999px;
    background:rgba(79,70,229,.10);
    color:#4F46E5;
    font-size:.72rem;
    font-weight:850;
    letter-spacing:.08em;
}
.control-bar {
    display:grid;
    grid-template-columns: 2.2fr 1fr 1fr;
    gap:14px;
    margin-bottom:24px;
}
.executive-grid {
    display:grid;
    grid-template-columns: repeat(4, minmax(190px, 1fr));
    gap:20px;
    margin:24px 0 34px 0;
}
.metric-card {
    padding:24px;
    min-height:165px;
    border-radius:26px;
    background:rgba(255,255,255,.76);
    border:1px solid rgba(255,255,255,.45);
    box-shadow:0 18px 55px rgba(15,23,42,.07);
    backdrop-filter:blur(22px);
    transition:all .18s ease;
}
.metric-card:hover {
    transform:translateY(-3px);
    box-shadow:0 24px 70px rgba(15,23,42,.10);
}
.metric-icon { font-size:1.6rem; margin-bottom:14px; }
.metric-label {
    font-size:.75rem;
    font-weight:900;
    letter-spacing:.06em;
    color:#64748B;
    text-transform:uppercase;
}
.metric-value {
    margin-top:10px;
    font-size:2.25rem;
    font-weight:950;
    letter-spacing:-.06em;
    color:#0F172A;
}
.metric-note {
    margin-top:12px;
    font-size:.82rem;
    color:#64748B;
    line-height:1.4;
}
.section-title {
    margin-top:30px;
    margin-bottom:8px;
    font-size:1.75rem;
    font-weight:950;
    letter-spacing:-.055em;
}
.section-subtitle {
    color:#64748B;
    font-size:.98rem;
    margin-bottom:18px;
}
button[kind="primary"],
button[kind="secondary"],
.stDownloadButton button,
.stButton button {
    border-radius:999px !important;
    background:linear-gradient(135deg,#4F46E5,#06B6D4) !important;
    color:white !important;
    border:0 !important;
    box-shadow:0 12px 30px rgba(79,70,229,.22) !important;
    font-weight:850 !important;
}
[data-testid="stDataFrame"] {
    border-radius:24px;
    overflow:hidden;
    border:1px solid rgba(15,23,42,.07);
    box-shadow:0 18px 55px rgba(15,23,42,.06);
    background:rgba(255,255,255,.80);
}
.js-plotly-plot,
.plot-container,
svg.main-svg {
    background:transparent !important;
    border:none !important;
    box-shadow:none !important;
}
html, body, [class*="css"] {
    font-family: Inter, ui-sans-serif, system-ui, sans-serif;
}
h1,h2,h3 { letter-spacing:-.05em; }
header[data-testid="stHeader"] {
    display: none !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

[data-testid="stStatusWidget"] {
    display: none !important;
}

#MainMenu {
    visibility: hidden !important;
}

footer {
    visibility: hidden !important;
}

.stApp {
    margin-top: 0rem !important;
}

.block-container {
    padding-top: 1.2rem !important;
}
</style>
""", unsafe_allow_html=True)


class ReporteForensePDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 9, "INFORME TECNICO DE OBSERVABILIDAD Y DISPONIBILIDAD OPERACIONAL", 0, 1, "C")
        self.set_font("Arial", "", 9)
        self.cell(0, 7, f"Generado: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", 0, 1, "C")
        self.line(10, 28, 200, 28)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, "C")


def generar_pdf_bytes(df_fallos, df_servicios, uptime, total_checks, total_fallos, latencia_promedio):
    pdf = ReporteForensePDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "1. Resumen ejecutivo", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(
        0,
        6,
        f"El sistema Aurora registro {total_checks} verificaciones tecnicas. "
        f"La disponibilidad global observada fue {uptime:.2f}%, con {total_fallos} incidentes "
        f"clasificados como errores HTTP, DNS/TLS, fallas de servicio o degradacion por latencia. "
        f"La latencia promedio fue {latencia_promedio:.0f} ms."
    )
    pdf.ln(4)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "2. Salud por servicio", 0, 1)
    pdf.set_font("Arial", "B", 8)
    pdf.cell(75, 7, "Servicio", 1)
    pdf.cell(22, 7, "Uptime", 1)
    pdf.cell(22, 7, "Score", 1)
    pdf.cell(22, 7, "Fallos", 1)
    pdf.cell(28, 7, "Lat. prom.", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 8)
    for _, r in df_servicios.head(20).iterrows():
        url = str(r["url"]).replace("https://", "")[:40]
        pdf.cell(75, 7, url, 1)
        pdf.cell(22, 7, f"{r['uptime']:.2f}%", 1)
        pdf.cell(22, 7, f"{r['health_score']:.1f}", 1)
        pdf.cell(22, 7, str(int(r["fallos"])), 1)
        pdf.cell(28, 7, f"{r['latencia_promedio']:.0f} ms", 1)
        pdf.ln()

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "3. Bitacora de incidentes", 0, 1)
    pdf.set_font("Arial", "B", 8)
    pdf.cell(42, 7, "Fecha UTC", 1)
    pdf.cell(75, 7, "Servicio", 1)
    pdf.cell(22, 7, "Codigo", 1)
    pdf.cell(50, 7, "Evento", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 8)
    for _, row in df_fallos.head(60).iterrows():
        fecha = str(row.get("timestamp", "")).split(".")[0][:19]
        url = str(row.get("url", "")).replace("https://", "")[:38]
        code = str(int(row["http_code"])) if pd.notna(row.get("http_code")) else "DNS/TLS"
        event = str(row.get("error_type", ""))[:32]
        pdf.cell(42, 7, fecha, 1)
        pdf.cell(75, 7, url, 1)
        pdf.cell(22, 7, code, 1)
        pdf.cell(50, 7, event, 1)
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

            for col in ["error_type", "url", "screenshot_url", "content_hash", "ssl_issuer", "ssl_expiry"]:
                if col not in df.columns:
                    df[col] = None

        return df

    except Exception as e:
        st.error("Aurora no pudo conectarse con la bóveda forense.")
        st.exception(e)
        return pd.DataFrame()


def short_url(url: str, max_len: int = 62) -> str:
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
      <svg width="42" height="42" viewBox="0 0 64 64" fill="none">
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

endpoints_disponibles = sorted(df["url"].dropna().unique().tolist())

if "section" not in st.session_state:
    st.session_state.section = "Resumen Ejecutivo"

top1, top2, top3 = st.columns([3.2, 1, 1])

with top1:
    endpoint_seleccionado = st.selectbox(
        "Plataforma",
        ["Todas"] + endpoints_disponibles,
        label_visibility="collapsed",
    )

if endpoint_seleccionado != "Todas":
    df_filtrado = df[df["url"] == endpoint_seleccionado].copy()
else:
    df_filtrado = df.copy()

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

pdf_bytes = generar_pdf_bytes(
    df_fallos,
    df_servicios,
    uptime_porcentaje,
    total_checks,
    total_fallos,
    latencia_promedio,
)

with top2:
    if st.button("Actualizar"):
        load_data.clear()
        st.rerun()

with top3:
    st.download_button(
        label="Descargar PDF",
        data=pdf_bytes,
        file_name=f"Aurora_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
    )

section = st.segmented_control(
    "Vista",
    ["Resumen Ejecutivo", "Latencia", "Incidentes", "Evidencia Forense"],
    default=st.session_state.section,
    key="section",
    label_visibility="collapsed",
)

servicio_mas_caido = df_servicios.sort_values("uptime").iloc[0]
servicio_mas_lento = df_servicios.sort_values("latencia_promedio", ascending=False).iloc[0]
servicio_mas_saludable = df_servicios.sort_values("health_score", ascending=False).iloc[0]
servicio_mas_evidencia = df_servicios.sort_values("evidencia", ascending=False).iloc[0]

if section == "Resumen Ejecutivo":
    st.markdown('<div class="section-title">Gobierno Ejecutivo de Disponibilidad</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Vista consolidada para entender disponibilidad, criticidad, evidencia y salud operativa.</div>', unsafe_allow_html=True)

    st.markdown(f"""
<div class="executive-grid">
<div class="metric-card" title="Porcentaje de verificaciones exitosas dentro del periodo analizado. Excluye errores HTTP, DNS, TLS y errores registrados.">
<div class="metric-icon">🟢</div><div class="metric-label">Disponibilidad</div>
<div class="metric-value">{uptime_porcentaje:.2f}%</div>
<div class="metric-note">Ventana: {ventana_inicio.strftime('%Y-%m-%d %H:%M')} → {ventana_fin.strftime('%Y-%m-%d %H:%M')} UTC</div>
</div>
<div class="metric-card" title="Eventos clasificados como error HTTP, DNS, TLS, timeout, caída o degradación funcional.">
<div class="metric-icon">🚨</div><div class="metric-label">Incidentes</div>
<div class="metric-value">{total_fallos}</div>
<div class="metric-note">Fallos sobre {total_checks} verificaciones registradas.</div>
</div>
<div class="metric-card" title="Tiempo promedio de respuesta. Sobre 3000 ms indica degradación crítica.">
<div class="metric-icon">⚡</div><div class="metric-label">Latencia promedio</div>
<div class="metric-value">{latencia_promedio:.0f} ms</div>
<div class="metric-note">Estado: {classify_latency(latencia_promedio)}. &lt;1000 sano · 1000-3000 degradado · &gt;3000 crítico.</div>
</div>
<div class="metric-card" title="Número total de observaciones técnicas registradas.">
<div class="metric-icon">📡</div><div class="metric-label">Muestras</div>
<div class="metric-value">{total_checks}</div>
<div class="metric-note">Registros acumulados en la bóveda técnica.</div>
</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Diagnóstico Operacional</div>', unsafe_allow_html=True)

    st.markdown(f"""
<div class="executive-grid">
<div class="metric-card" title="Servicio con menor disponibilidad registrada.">
<div class="metric-icon">🔴</div><div class="metric-label">Servicio más caído</div>
<div class="metric-value">{servicio_mas_caido['uptime']:.1f}%</div>
<div class="metric-note">{short_url(servicio_mas_caido['url'])}</div>
</div>
<div class="metric-card" title="Servicio con mayor latencia promedio.">
<div class="metric-icon">🐢</div><div class="metric-label">Servicio más lento</div>
<div class="metric-value">{servicio_mas_lento['latencia_promedio']:.0f} ms</div>
<div class="metric-note">{short_url(servicio_mas_lento['url'])}</div>
</div>
<div class="metric-card" title="Servicio con mejor combinación de disponibilidad y latencia.">
<div class="metric-icon">✅</div><div class="metric-label">Mejor salud</div>
<div class="metric-value">{servicio_mas_saludable['health_score']:.0f}/100</div>
<div class="metric-note">{short_url(servicio_mas_saludable['url'])}</div>
</div>
<div class="metric-card" title="Servicio con mayor volumen de evidencia forense asociada.">
<div class="metric-icon">🧾</div><div class="metric-label">Mayor evidencia</div>
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

    st.dataframe(
        df_health[["url", "uptime", "health_score", "muestras", "fallos", "latencia_promedio", "latencia_maxima", "evidencia"]],
        use_container_width=True,
        hide_index=True,
    )

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
    fig_latencia.update_traces(line=dict(width=3.2), marker=dict(size=7, line=dict(width=1.5, color="white")))
    fig_latencia.update_layout(
        height=560,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0F172A", size=13),
        hovermode="x unified",
        xaxis=dict(title="", showgrid=False, zeroline=False, tickfont=dict(color="#64748B")),
        yaxis=dict(title="Latencia (ms)", showgrid=True, gridcolor="rgba(100,116,139,0.18)", zeroline=False, tickfont=dict(color="#64748B")),
        legend=dict(title="", orientation="h", yanchor="bottom", y=1.08, xanchor="left", x=0, bgcolor="rgba(255,255,255,0)", font=dict(size=12, color="#334155")),
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
    st.markdown('<div class="section-title">Bitácora de Fallos y Tiempos de Inactividad</div>', unsafe_allow_html=True)

    if df_fallos.empty:
        st.success("No se han registrado fallos para los filtros seleccionados.")
    else:
        df_fallos_view = df_fallos[["timestamp", "url", "http_code", "latency_ms", "error_type"]].sort_values(by="timestamp", ascending=False).copy()
        df_fallos_view["timestamp"] = df_fallos_view["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        df_fallos_view["url"] = df_fallos_view["url"].apply(lambda x: short_url(x, 70))
        df_fallos_view["http_code"] = df_fallos_view["http_code"].apply(lambda x: "DNS/TLS" if pd.isna(x) else str(int(x)))
        df_fallos_view["latency_ms"] = df_fallos_view["latency_ms"].astype(int).astype(str) + " ms"
        df_fallos_view = df_fallos_view.rename(columns={"timestamp": "Fecha", "url": "Servicio", "http_code": "Código", "latency_ms": "Latencia", "error_type": "Evento"})
        st.dataframe(df_fallos_view, use_container_width=True, hide_index=True, height=560)

elif section == "Evidencia Forense":
    st.markdown('<div class="section-title">Auditoría de Integridad y Certificados</div>', unsafe_allow_html=True)

    df_evidencia_view = df_filtrado[["timestamp", "url", "content_hash", "ssl_issuer", "ssl_expiry", "screenshot_url"]].sort_values(by="timestamp", ascending=False).copy()
    df_evidencia_view["timestamp"] = df_evidencia_view["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    df_evidencia_view["url"] = df_evidencia_view["url"].apply(lambda x: short_url(x, 70))
    df_evidencia_view["content_hash"] = df_evidencia_view["content_hash"].fillna("Sin hash").apply(lambda x: x[:18] + "..." if isinstance(x, str) and len(x) > 18 else x)
    df_evidencia_view["ssl_issuer"] = df_evidencia_view["ssl_issuer"].fillna("No disponible").apply(lambda x: x[:50] + "..." if isinstance(x, str) and len(x) > 50 else x)
    df_evidencia_view["ssl_expiry"] = df_evidencia_view["ssl_expiry"].fillna("No disponible")
    df_evidencia_view["screenshot_url"] = df_evidencia_view["screenshot_url"].fillna("Sin captura")
    df_evidencia_view = df_evidencia_view.rename(columns={"timestamp": "Fecha", "url": "Servicio", "content_hash": "Hash SHA256", "ssl_issuer": "Emisor SSL", "ssl_expiry": "Expira SSL", "screenshot_url": "Evidencia"})
    st.dataframe(df_evidencia_view, use_container_width=True, hide_index=True, height=560)
