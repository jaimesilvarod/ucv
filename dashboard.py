import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone
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
        radial-gradient(circle at 8% 14%, rgba(79,70,229,.24), transparent 24%),
        radial-gradient(circle at 28% 8%, rgba(6,182,212,.18), transparent 28%),
        radial-gradient(circle at 74% 6%, rgba(16,185,129,.22), transparent 30%),
        radial-gradient(circle at 88% 36%, rgba(34,211,238,.14), transparent 28%),
        radial-gradient(circle at 52% 88%, rgba(139,92,246,.15), transparent 32%),
        linear-gradient(180deg, #F8FBFF 0%, #EEF4FF 48%, #F7F9FF 100%);
    color: #0F172A;
    margin-top: 0rem !important;
}

section[data-testid="stSidebar"] { display:none !important; }

.block-container {
    max-width: 100% !important;
    padding: 1.2rem 4rem 5rem 4rem !important;
}

html, body, [class*="css"] {
    font-family: Inter, ui-sans-serif, system-ui, sans-serif;
}

h1,h2,h3 { letter-spacing:-.05em; }

header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
    display: none !important;
}

#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }

.topbar{
    display:flex !important;
    align-items:center !important;
    justify-content:space-between !important;
    margin-bottom:.4rem !important;
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

/* ===== COMPACT NAVIGATION ===== */

div[data-testid="stSegmentedControl"] {
    max-width: 620px !important;
    margin: 14px 0 18px 0 !important;
}

div[data-testid="stSegmentedControl"] > div {
    display: flex !important;
    width: fit-content !important;
    gap: 6px !important;
    padding: 6px !important;
    border-radius: 18px !important;
    background: rgba(255,255,255,.62) !important;
    border: 1px solid rgba(255,255,255,.70) !important;
    box-shadow:
        0 12px 36px rgba(15,23,42,.06),
        inset 0 1px 0 rgba(255,255,255,.58) !important;
    backdrop-filter: blur(22px) !important;
    -webkit-backdrop-filter: blur(22px) !important;
}

div[data-testid="stSegmentedControl"] label {
    width: auto !important;
}

div[data-testid="stSegmentedControl"] label > div {
    width: auto !important;
    justify-content: center !important;
    border-radius: 13px !important;
    min-height: 38px !important;
    padding: 0 16px !important;
    font-size: .82rem !important;
    font-weight: 850 !important;
    color: #475569 !important;
    border: 1px solid transparent !important;
    transition: all .18s ease !important;
}

div[data-testid="stSegmentedControl"] label:hover > div {
    background: rgba(255,255,255,.68) !important;
    color: #0F172A !important;
}

div[data-testid="stSegmentedControl"] label[aria-checked="true"] > div,
div[data-testid="stSegmentedControl"] label[data-baseweb="radio"]:has(input:checked) > div {
    background: linear-gradient(135deg,#4F46E5,#06B6D4,#10B981) !important;
    color: white !important;
    box-shadow:
        0 12px 28px rgba(79,70,229,.24),
        inset 0 1px 0 rgba(255,255,255,.25) !important;
}

/* ===== FILTER BAR ===== */

div[data-baseweb="select"] > div {
    min-height: 44px !important;
    border-radius: 16px !important;
    background: rgba(255,255,255,.78) !important;
    border: 1px solid rgba(255,255,255,.70) !important;
    box-shadow: 0 10px 28px rgba(15,23,42,.05) !important;
}

button[kind="primary"],
button[kind="secondary"],
.stDownloadButton button,
.stButton button {
    min-height: 44px !important;
    border-radius:999px !important;
    background:linear-gradient(135deg,#4F46E5,#06B6D4) !important;
    color:white !important;
    border:0 !important;
    box-shadow:0 12px 30px rgba(79,70,229,.22) !important;
    font-weight:850 !important;
    padding: 0 22px !important;
}

/* ===== SECTIONS ===== */

.section-title{
    margin-top:12px !important;
    margin-bottom:4px !important;
    font-size:1.55rem !important;
    font-weight:900 !important;
    letter-spacing:-.05em !important;
}

.section-subtitle{
    margin-bottom:10px !important;
    font-size:.95rem !important;
    color:#64748B !important;
}

/* ===== CARDS ===== */

.executive-grid{
    display:grid !important;
    grid-template-columns:repeat(4,minmax(180px,1fr)) !important;
    gap:16px !important;
    margin-top:16px !important;
    margin-bottom:20px !important;
}

.metric-card{
    position:relative !important;
    padding:20px 24px !important;
    min-height:138px !important;
    border-radius:24px !important;
    background:
        linear-gradient(145deg, rgba(255,255,255,.80), rgba(255,255,255,.50)) !important;
    border:1px solid rgba(255,255,255,.70) !important;
    box-shadow:
        0 18px 48px rgba(15,23,42,.07),
        inset 0 1px 0 rgba(255,255,255,.82) !important;
    backdrop-filter:blur(22px) !important;
    -webkit-backdrop-filter:blur(22px) !important;
    transition:all .18s ease !important;
    overflow:hidden !important;
}

.metric-card::before {
    content:"";
    position:absolute;
    inset:0;
    background:
        radial-gradient(circle at 16% 18%, rgba(79,70,229,.12), transparent 28%),
        radial-gradient(circle at 90% 12%, rgba(6,182,212,.12), transparent 32%);
    pointer-events:none;
}

.metric-card:hover {
    transform:translateY(-4px);
    box-shadow:0 26px 80px rgba(15,23,42,.12);
}

.metric-icon {
    position:relative;
    width:34px;
    height:34px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:999px;
    background:linear-gradient(135deg, rgba(79,70,229,.18), rgba(6,182,212,.18), rgba(16,185,129,.16));
    font-size:1.2rem;
    margin-bottom:18px;
}

.metric-label {
    position:relative;
    font-size:.75rem;
    font-weight:900;
    letter-spacing:.06em;
    color:#64748B;
    text-transform:uppercase;
}

.metric-value {
    position:relative;
    margin-top:12px;
    font-size:2.15rem;
    font-weight:950;
    letter-spacing:-.06em;
    color:#0F172A;
}

.metric-note {
    position:relative;
    margin-top:12px;
    font-size:.82rem;
    color:#64748B;
    line-height:1.4;
}

/* ===== TABLES / CHARTS ===== */

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

/* ===== FLOATING PDF ===== */

.floating-pdf {
    position: fixed;
    right: 28px;
    bottom: 28px;
    z-index: 9999;
}

.floating-pdf .stDownloadButton button {
    min-height: 46px !important;
    padding: 0 22px !important;
    box-shadow: 0 18px 48px rgba(79,70,229,.28) !important;
}

/* ===== RESPONSIVE ===== */

@media (max-width: 1100px) {
    .block-container {
        padding: 1rem 1.3rem 5rem 1.3rem !important;
    }

    .executive-grid {
        grid-template-columns: repeat(2, minmax(180px, 1fr)) !important;
    }
}

@media (max-width: 700px) {
    .executive-grid {
        grid-template-columns: 1fr !important;
    }

    div[data-testid="stSegmentedControl"] > div {
        width: 100% !important;
        flex-wrap: wrap !important;
    }
}
</style>
""", unsafe_allow_html=True)


class ReporteForensePDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 9, "INFORME TECNICO DE OBSERVABILIDAD Y DISPONIBILIDAD OPERACIONAL", 0, 1, "C")
        self.set_font("Arial", "", 9)
        self.cell(0, 7, f"Generado: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC", 0, 1, "C")
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
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
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

section = st.segmented_control(
    "Vista",
    ["Resumen Ejecutivo", "Latencia", "Incidentes", "Evidencia Forense"],
    default=st.session_state.section,
    key="section",
    label_visibility="collapsed",
)

control1, control2, control3 = st.columns([2.4, 1.1, .7])

with control1:
    endpoint_seleccionado = st.selectbox(
        "Mostrando",
        ["Todas"] + endpoints_disponibles,
        format_func=lambda x: "Mostrando: TODOS" if x == "Todas" else f"Mostrando: {short_url(x, 80)}",
        label_visibility="collapsed",
    )

with control2:
    ventana = st.selectbox(
        "Ventana",
        ["Últimas 24 horas", "Últimos 7 días", "Últimos 30 días", "Todo"],
        label_visibility="collapsed",
    )

with control3:
    if st.button("Actualizar"):
        load_data.clear()
        st.rerun()

df_base = df.copy()
now_utc = pd.Timestamp.now(tz="UTC")

if ventana == "Últimas 24 horas":
    df_base = df_base[df_base["timestamp"] >= now_utc - pd.Timedelta(hours=24)]
elif ventana == "Últimos 7 días":
    df_base = df_base[df_base["timestamp"] >= now_utc - pd.Timedelta(days=7)]
elif ventana == "Últimos 30 días":
    df_base = df_base[df_base["timestamp"] >= now_utc - pd.Timedelta(days=30)]

if endpoint_seleccionado != "Todas":
    df_filtrado = df_base[df_base["url"] == endpoint_seleccionado].copy()
else:
    df_filtrado = df_base.copy()

if df_filtrado.empty:
    st.warning("No hay datos para el endpoint o ventana seleccionada.")
    st.stop()

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

st.markdown('<div class="floating-pdf">', unsafe_allow_html=True)
st.download_button(
    label="Descargar informe PDF",
    data=pdf_bytes,
    file_name=f"Aurora_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
    mime="application/pdf",
    key="floating_pdf",
)
st.markdown('</div>', unsafe_allow_html=True)

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
    df_health = df_health.sort_values(
        by=["uptime", "fallos", "latencia_promedio"],
        ascending=[True, False, False],
    )

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
    df_evidencia_view = df_evidencia_view.rename(columns={
        "timestamp": "Fecha",
        "url": "Servicio",
        "content_hash": "Hash SHA256",
        "ssl_issuer": "Emisor SSL",
        "ssl_expiry": "Expira SSL",
        "screenshot_url": "Evidencia"
    })
    st.dataframe(df_evidencia_view, use_container_width=True, hide_index=True, height=560)
