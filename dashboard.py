import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from fpdf import FPDF
import base64

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
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generar_pdf_bytes(df_fallos, uptime, total_incidentes):
    pdf = ReporteForensePDF()
    pdf.add_page()
    
    # Resumen Ejecutivo
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '1. RESUMEN EJECUTIVO', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 8, f"Durante el periodo analizado, la infraestructura presentó un Uptime global del {uptime:.2f}%. Se detectaron un total de {total_incidentes} incidentes críticos (Errores 400+, Timeouts o caídas de DNS).")
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
    for index, row in df_fallos.head(50).iterrows(): # Limitamos a los últimos 50 para el PDF
        fecha_str = str(row['timestamp']).split('.')[0]
        url_corta = str(row['url']).replace('https://', '')[:35] + "..." if len(str(row['url'])) > 35 else str(row['url']).replace('https://', '')
        http_code = str(int(row['http_code'])) if pd.notna(row['http_code']) else "DNS/TLS"
        error_type = str(row['error_type'])[:30]
        
        pdf.cell(45, 8, fecha_str, 1)
        pdf.cell(75, 8, url_corta, 1)
        pdf.cell(20, 8, http_code, 1)
        pdf.cell(50, 8, error_type, 1)
        pdf.ln()
        
    return pdf.output(dest='S').encode('latin1')

# Añadir el botón de descarga en la barra lateral
if not df_fallos.empty:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Exportar Evidencia")
    pdf_bytes = generar_pdf_bytes(df_fallos, uptime_porcentaje, total_fallos)
    
    st.sidebar.download_button(
        label="📥 Descargar Reporte PDF",
        data=pdf_bytes,
        file_name=f"Auditoria_UCV_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf"
    )

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Forensic Web Monitor | UCV", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

def aplicar_estilo_premium():
    st.markdown("""
        <style>
        /* Ocultar elementos por defecto de Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Estilo premium para las tarjetas de métricas (KPIs) */
        div[data-testid="metric-container"] {
            background-color: #1E1E1E;
            border: 1px solid #333333;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            border-left: 5px solid #00C853; /* Borde verde estilo Power BI */
        }
        
        /* Mejorar la tipografía de las métricas */
        div[data-testid="metric-container"] label {
            font-size: 1rem !important;
            color: #A0A0A0 !important;
        }
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700 !important;
        }
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo_premium()

# 2. CONEXIÓN A LA BÓVEDA FORENSE
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# 3. EXTRACCIÓN DE DATOS (Cacheado cada 5 minutos)
@st.cache_data(ttl=300)
def load_data():
    response = supabase.table("incidentes").select("*").order("timestamp", desc=True).limit(2000).execute()
    df = pd.DataFrame(response.data)
    if not df.empty:
        # Convertir timestamps a formato manejable
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['latency_ms'] = pd.to_numeric(df['latency_ms'], errors='coerce').fillna(0)
        df['http_code'] = pd.to_numeric(df['http_code'], errors='coerce')
    return df

st.title("🛡️ Panel de Auditoría de Infraestructura Web")
st.markdown("Monitor forense de disponibilidad, latencia y cambios de estado.")

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

    # --- MÉTRICAS GLOBALES (KPIs) ---
    total_checks = len(df_filtrado)
    df_fallos = df_filtrado[(df_filtrado['http_code'] >= 400) | (df_filtrado['http_code'].isna()) | (df_filtrado['error_type'] != 'OK')]
    total_fallos = len(df_fallos)
    
    uptime_porcentaje = 100.0 if total_checks == 0 else ((total_checks - total_fallos) / total_checks) * 100
    latencia_promedio = df_filtrado['latency_ms'].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Uptime General", f"{uptime_porcentaje:.2f}%")
    col2.metric("Total de Muestras", total_checks)
    col3.metric("Incidentes Registrados", total_fallos)
    col4.metric("Latencia Promedio", f"{latencia_promedio:.0f} ms")

    st.markdown("---")

    # --- PESTAÑAS DE ANÁLISIS ---
    tab1, tab2, tab3 = st.tabs(["📈 Análisis de Latencia", "🚨 Registro de Incidentes", "🔐 Evidencia Forense (Hashes & SSL)"])

    # Pestaña 1: Gráficas
    with tab1:
        st.subheader("Evolución de Tiempos de Respuesta (ms)")
        fig_latencia = px.line(
            df_filtrado, 
            x="timestamp", 
            y="latency_ms", 
            color="url",
            template="plotly_dark"
        )
        # Rediseño premium de la gráfica
        fig_latencia.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, title=""),
            yaxis=dict(showgrid=True, gridcolor="#333333", title="Latencia (ms)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig_latencia, use_container_width=True)

    # Pestaña 2: Tabla de Fallos Críticos
    with tab2:
        st.subheader("Bitácora de Fallos y Tiempos de Inactividad")
        if not df_fallos.empty:
            df_mostrar_fallos = df_fallos[['timestamp', 'url', 'http_code', 'latency_ms', 'error_type']].copy()
            df_mostrar_fallos = df_mostrar_fallos.sort_values(by="timestamp", ascending=False)
            st.dataframe(df_mostrar_fallos, use_container_width=True, hide_index=True)
        else:
            st.success("No se han registrado fallos para los filtros seleccionados.")

    # Pestaña 3: Cadena de Custodia (Evidencia)
    with tab3:
        st.subheader("Auditoría de Integridad y Certificados")
        st.markdown("Registros criptográficos para demostrar la inmutabilidad de la evidencia.")
        df_evidencia = df_filtrado[['timestamp', 'url', 'content_hash', 'ssl_issuer', 'ssl_expiry', 'screenshot_url']].copy()
        st.dataframe(df_evidencia, use_container_width=True, hide_index=True)

    # Botón de refresco manual
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Forzar Actualización de Datos"):
        load_data.clear()
