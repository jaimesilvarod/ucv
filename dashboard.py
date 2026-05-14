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

/* ===== BASE ===== */

.stApp {
    background:
        radial-gradient(circle at top right, rgba(37,99,235,0.08), transparent 30%),
        linear-gradient(180deg, #F4F7FB 0%, #EEF2FF 100%);
    color: #0F172A;
}

/* ===== SIDEBAR ===== */

[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.88);
    backdrop-filter: blur(18px);
    border-right: 1px solid rgba(15,23,42,0.06);
}

[data-testid="stSidebar"] * {
    color: #0F172A !important;
}

/* ===== MAIN ===== */

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* ===== HERO ===== */

.hero-card {
    padding: 42px;
    border-radius: 30px;
    background:
        linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,250,252,0.92));
    border: 1px solid rgba(15,23,42,0.06);
    box-shadow:
        0 10px 40px rgba(15,23,42,0.06),
        0 2px 8px rgba(15,23,42,0.04);
    margin-bottom: 28px;
}

.hero-pill {
    display: inline-block;
    padding: 8px 16px;
    border-radius: 999px;
    background: rgba(37,99,235,0.08);
    color: #2563EB;
    font-size: 0.8rem;
    font-weight: 700;
    margin-bottom: 20px;
}

.hero-title {
    font-size: 3.2rem;
    line-height: 1;
    font-weight: 900;
    letter-spacing: -0.07em;
    color: #0F172A;
    margin-bottom: 14px;
}

.hero-subtitle {
    font-size: 1.05rem;
    color: #475569;
    max-width: 850px;
    line-height: 1.6;
}

/* ===== KPI CARDS ===== */

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.82);
    backdrop-filter: blur(14px);
    border-radius: 24px;
    padding: 22px;
    border: 1px solid rgba(15,23,42,0.05);
    box-shadow:
        0 4px 20px rgba(15,23,42,0.04);
}

/* ELIMINA cajas externas */
[data-testid="stVerticalBlock"] > div:has([data-testid="stMetric"]) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

[data-testid="stMetricLabel"] {
    color: #64748B;
    font-size: 0.9rem;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: #0F172A;
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.05em;
}

/* ===== TABS ===== */

button[data-baseweb="tab"] {
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 0;
    color: #64748B;
    font-weight: 600;
    padding: 14px 8px;
    margin-right: 24px;
}

button[data-baseweb="tab"]:hover {
    color: #0F172A;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #2563EB;
    border-bottom: 2px solid #2563EB;
    background: transparent;
}

/* ===== BUTTONS ===== */

.stButton > button,
.stDownloadButton > button {
    border-radius: 14px;
    border: none;
    background: linear-gradient(135deg,#2563EB,#4F46E5);
    color: white;
    font-weight: 700;
    padding: 0.75rem 1rem;
    box-shadow: 0 8px 24px rgba(37,99,235,0.22);
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-1px);
}

/* ===== DATAFRAMES ===== */

[data-testid="stDataFrame"] {
    border-radius: 22px;
    overflow: hidden;
    border: 1px solid rgba(15,23,42,0.06);
    box-shadow:
        0 8px 24px rgba(15,23,42,0.04);
}

/* ===== PLOTLY ===== */

.js-plotly-plot {
    border-radius: 24px;
    background: rgba(255,255,255,0.78);
    padding: 10px;
    border: 1px solid rgba(15,23,42,0.05);
}

/* ===== TYPOGRAPHY ===== */

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
<div class="hero-card">
    <div class="hero-pill">
        MONITOREO FORENSE ACTIVO
    </div>

    <div class="hero-title">
        Panel de Auditoría de Infraestructura Web
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
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
            st.metric("Uptime General", f"{uptime_porcentaje:.2f}%")
            
    with col2:
            st.metric("Total de Muestras", total_checks)
            
    with col3:
            st.metric("Incidentes Registrados", total_fallos)
            
    with col4:
            st.metric("Latencia Promedio", f"{latencia_promedio:.0f} ms")

    st.markdown("---")

    # --- PESTAÑAS DE ANÁLISIS ---
    tab1, tab2, tab3 = st.tabs(["📈 Análisis de Latencia", "🚨 Registro de Incidentes", "🔐 Evidencia Forense (Hashes & SSL)"])

    with tab1:
        st.subheader("Evolución de Tiempos de Respuesta (ms)")
        fig_latencia = px.line(
            df_filtrado, 
            x="timestamp", 
            y="latency_ms", 
            color="url",
            template="plotly_dark"
        )
        fig_latencia.update_layout(
            template="plotly_dark",
            height=520,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC", family="Inter, sans-serif"),
            xaxis=dict(
                showgrid=False,
                title="",
                color="#CBD5E1"
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(148,163,184,0.18)",
                title="Latencia (ms)",
                color="#CBD5E1"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.08,
                xanchor="right",
                x=1,
                bgcolor="rgba(15,23,42,0.65)",
                bordercolor="rgba(148,163,184,0.18)",
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
