import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

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
            markers=True,
            title="Latencia Histórica por Endpoint",
            template="plotly_dark",
            labels={"timestamp": "Fecha/Hora UTC", "latency_ms": "Latencia (ms)", "url": "Plataforma"}
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
