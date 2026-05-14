import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from fpdf import FPDF
import base64
import tempfile

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser el primer comando de Streamlit siempre)
st.set_page_config(
    page_title="Forensic Web Monitor | UCV", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

/* ===== APP ===== */

.stApp {
    background:
        radial-gradient(circle at top right, rgba(79,70,229,0.08), transparent 25%),
        radial-gradient(circle at bottom left, rgba(6,182,212,0.08), transparent 22%),
        #F6F8FC;
    color: #0F172A;
}

/* ===== SIDEBAR ===== */

[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.82);
    backdrop-filter: blur(18px);
    border-right: 1px solid rgba(15,23,42,0.06);
}

[data-testid="stSidebar"] * {
    color: #0F172A !important;
}

/* ===== MAIN ===== */

.block-container {
    max-width: 1600px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

/* ===== HERO ===== */

.hero {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 14px;
    border-radius: 999px;
    background: rgba(79,70,229,0.08);
    color: #4F46E5;
    font-size: 0.78rem;
    font-weight: 700;
    margin-bottom: 24px;
}

.hero-title {
    font-size: 4rem;
    line-height: 0.95;
    font-weight: 900;
    letter-spacing: -0.08em;
    color: #0F172A;
    max-width: 950px;
}

.hero-subtitle {
    margin-top: 22px;
    font-size: 1.08rem;
    line-height: 1.7;
    color: #475569;
    max-width: 820px;
}

/* ===== KPI STRIP ===== */

.kpi-strip {
    display: flex;
    gap: 42px;
    padding-top: 1rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid rgba(15,23,42,0.08);
    margin-bottom: 2rem;
}

.kpi-item {
    min-width: 180px;
}

.kpi-label {
    font-size: 0.82rem;
    color: #64748B;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.06em;
    color: #0F172A;
}

/* ===== PLOTLY ===== */

.js-plotly-plot {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* ===== DATAFRAME ===== */

[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(15,23,42,0.06);
}

/* ===== BUTTONS ===== */

.stButton > button,
.stDownloadButton > button {
    border-radius: 12px;
    border: none;
    background: linear-gradient(135deg,#4F46E5,#06B6D4);
    color: white;
    font-weight: 700;
    padding: 0.72rem 1rem;
    box-shadow:
        0 10px 24px rgba(79,70,229,0.18);
}

/* ===== TYPO ===== */

html, body, [class*="css"] {
    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        sans-serif;
}

h1,h2,h3 {
    letter-spacing: -0.05em;
}

</style>
""", unsafe_allow_html=True)

# 2. DEFINICIÓN DE CLASES Y FUNCIONES
class ReporteForensePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'REPORTE DE AUDITORIA FORENSE DE INFRAESTRUCTURA', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Generado el: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC', 0, 1, 'C')
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def generar_pdf_bytes(df_fallos, uptime, total_incidentes):
    pdf = ReporteForensePDF()
    pdf.add_page()
    
    # Resumen Ejecutivo
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '1. RESUMEN EJECUTIVO', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 8, f"Durante el periodo analizado, la infraestructura presento un Uptime global del {uptime:.2f}%. Se detectaron un total de {total_incidentes} incidentes criticos (Errores 400+, Timeouts o caidas de DNS).")
    pdf.ln(5)
    
    # Tabla de Incidentes
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '2. BITACORA DE INCIDENTES CRITICOS', 0, 1)
    
    pdf.set_font('Arial', 'B', 9)
    # Cabeceras de tabla
    pdf.cell(45, 8, 'Timestamp (UTC)', 1)
    pdf.cell(75, 8, 'Endpoint', 1)
    pdf.cell(20, 8, 'HTTP', 1)
    pdf.cell(50, 8, 'Detalle', 1)
    pdf.ln()
    
    pdf.set_font('Arial', '', 8)
    for index, row in df_fallos.head(50).iterrows():
        fecha_str = str(row['timestamp']).split('.')[0]
        url_corta = str(row['url']).replace('https://', '')[:35] + "..." if len(str(row['url'])) > 35 else str(row['url']).replace('https://', '')
        http_code = str(int(row['http_code'])) if pd.notna(row['http_code']) else "DNS/TLS"
        error_type = str(row['error_type'])[:30]
        
        pdf.cell(45, 8, fecha_str, 1)
        pdf.cell(75, 8, url_corta, 1)
        pdf.cell(20, 8, http_code, 1)
        pdf.cell(50, 8, error_type, 1)
        pdf.ln()
        
    # Guardado a prueba de fallos usando un archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            return f.read()

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

@st.cache_data(ttl=300)
def load_data():
    response = supabase.table("incidentes").select("*").order("timestamp", desc=True).limit(2000).execute()
    df = pd.DataFrame(response.data)
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['latency_ms'] = pd.to_numeric(df['latency_ms'], errors='coerce').fillna(0)
        df['http_code'] = pd.to_numeric(df['http_code'], errors='coerce')
    return df

# 4. INTERFAZ PRINCIPAL
st.markdown("""
<div class="hero">

<div class="hero-pill">
🛡️ MONITOREO FORENSE ACTIVO
</div>

<div class="hero-title">
Infraestructura Web y Evidencia Operacional
</div>

<div class="hero-subtitle">
Observabilidad avanzada de disponibilidad, latencia, DNS, certificados SSL,
integridad criptográfica y comportamiento operativo de plataformas académicas.
</div>

</div>
""", unsafe_allow_html=True)

df = load_data()

if df.empty:
    st.warning("Aún no hay suficientes datos en la bóveda forense. Espera a que el agente termine sus primeros ciclos.")
else:
    # --- BARRA LATERAL: FILTROS ---
    st.sidebar.header("Filtros de Auditoría")
    
    endpoints_disponibles = df['url'].unique().tolist()
    endpoint_seleccionado = st.sidebar.selectbox("Seleccionar Plataforma:", ["Todas"] + endpoints_disponibles)
    
    if endpoint_seleccionado != "Todas":
        df_filtrado = df[df['url'] == endpoint_seleccionado]
    else:
        df_filtrado = df

    # --- CÁLCULOS LOGICOS ---
    total_checks = len(df_filtrado)
    df_fallos = df_filtrado[(df_filtrado['http_code'] >= 400) | (df_filtrado['http_code'].isna()) | (df_filtrado['error_type'] != 'OK')]
    total_fallos = len(df_fallos)
    
    uptime_porcentaje = 100.0 if total_checks == 0 else ((total_checks - total_fallos) / total_checks) * 100
    latencia_promedio = df_filtrado['latency_ms'].mean()

    # --- MÉTRICAS GLOBALES (KPIs) ---
    st.markdown(f"""
    <div class="kpi-strip">
    
    <div class="kpi-item">
    <div class="kpi-label">UPTIME GENERAL</div>
    <div class="kpi-value">{uptime:.2f}%</div>
    </div>
    
    <div class="kpi-item">
    <div class="kpi-label">INCIDENTES</div>
    <div class="kpi-value">{incidentes}</div>
    </div>
    
    <div class="kpi-item">
    <div class="kpi-label">LATENCIA PROMEDIO</div>
    <div class="kpi-value">{latencia} ms</div>
    </div>
    
    <div class="kpi-item">
    <div class="kpi-label">MUESTRAS</div>
    <div class="kpi-value">{muestras}</div>
    </div>
    
    </div>
    """, unsafe_allow_html=True)

    # --- PESTAÑAS DE ANÁLISIS ---
    tab1, tab2, tab3 = st.tabs(["📈 Análisis de Latencia", "🚨 Registro de Incidentes", "🔐 Evidencia Forense (Hashes & SSL)"])

    with tab1:
        st.subheader("Evolución de Tiempos de Respuesta (ms)")
        fig_latencia = px.line(
            df_filtrado,
            x="timestamp",
            y="latency_ms",
            color="url",
            template="plotly_white"
        )
        
        fig_latencia.update_layout(
            height=520,
            plot_bgcolor="rgba(255,255,255,0)",
            paper_bgcolor="rgba(255,255,255,0)",
            font=dict(color="#0F172A"),
            xaxis=dict(showgrid=False, title=""),
            yaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.25)", title="Latencia (ms)"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.08,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="rgba(15,23,42,0.08)",
                borderwidth=1
            ),
            margin=dict(l=10, r=10, t=45, b=10),
        )
        fig_latencia.update_traces(line=dict(width=3), mode="lines+markers")
        st.plotly_chart(fig_latencia, use_container_width=True)

    with tab2:
        st.subheader("Bitácora de Fallos y Tiempos de Inactividad")
        if not df_fallos.empty:
            df_mostrar_fallos = df_fallos[['timestamp', 'url', 'http_code', 'latency_ms', 'error_type']].copy()
            df_mostrar_fallos = df_mostrar_fallos.sort_values(by="timestamp", ascending=False)
            st.dataframe(df_mostrar_fallos, use_container_width=True, hide_index=True)
        else:
            st.success("No se han registrado fallos para los filtros seleccionados.")

    with tab3:
        st.subheader("Auditoría de Integridad y Certificados")
        st.markdown("Registros criptográficos para demostrar la inmutabilidad de la evidencia.")
        df_evidencia = df_filtrado[['timestamp', 'url', 'content_hash', 'ssl_issuer', 'ssl_expiry', 'screenshot_url']].copy()
        st.dataframe(df_evidencia, use_container_width=True, hide_index=True)

    # --- EXPORTADOR PDF REUBICADO AQUÍ (Donde las variables ya existen) ---
    st.sidebar.markdown("---")
    if not df_fallos.empty:
        st.sidebar.subheader("Exportar Evidencia")
        pdf_bytes = generar_pdf_bytes(df_fallos, uptime_porcentaje, total_fallos)
        
        st.sidebar.download_button(
            label="📥 Descargar Reporte PDF",
            data=pdf_bytes,
            file_name=f"Auditoria_UCV_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )

    if st.sidebar.button("🔄 Forzar Actualización de Datos"):
        load_data.clear()
