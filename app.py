import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import gspread
from google_auth_oauthlib.flow import Flow
import requests

# Configuración inicial de la página
st.set_page_config(page_title="Fitness Tracker - Dieta & Gym", page_icon="💪", layout="wide")

# Configurar el flujo de autenticación de Google (OAuth)
# Los datos CLIENT_ID y CLIENT_SECRET se leen de forma segura desde los Secrets de Streamlit
try:
    client_config = {
        "web": {
            "client_id": st.secrets["google_auth"]["client_id"],
            "client_secret": st.secrets["google_auth"]["client_secret"],
            "auth_uri": "https://google.com",
            "token_uri": "https://googleapis.com",
            "redirect_uris": [st.secrets["google_auth"]["redirect_uri"]]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=["https://googleapis.com", "https://googleapis.com"]
    )
    flow.redirect_uri = st.secrets["google_auth"]["redirect_uri"]
except Exception as e:
    st.warning("Configurando el sistema de Login con Google... Revisa los Secrets.")

# Inicializar variables de sesión para el Login
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_info" not in st.session_state:
    st.session_state.usuario_info = None

# Manejar el código de retorno que Google envía después de que el usuario inicia sesión con éxito
query_params = st.query_params
if "code" in query_params and not st.session_state.autenticado:
    try:
        flow.fetch_token(code=query_params["code"])
        session = flow.authorized_session()
        user_info = session.get("https://googleapis.com").json()
        
        st.session_state.autenticado = True
        st.session_state.usuario_info = user_info
        # Limpiar los parámetros de la URL para que quede estética
        st.query_params.clear()
        st.rerun()
    except Exception as error_login:
        st.error("Hubo un problema al validar tu cuenta de Google. Inténtalo de nuevo.")

# =========================================================================
# PANTALLA DE INICIO DE SESIÓN (LOGIN)
# =========================================================================
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>💪 Mi Progreso Fitness</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>Registra tu peso y sobrecarga progresiva de forma segura en la nube</h4>", unsafe_allow_html=True)
    st.divider()
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.info("Para proteger tu privacidad y sincronizar tus datos con Google Sheets, debes iniciar sesión con tu cuenta de Google.")
        
        # Generar la URL oficial de Google para el Login
        try:
            auth_url, _ = flow.authorization_url(prompt='select_account')
            # Botón de estilo web llamativo para Google
            st.markdown(
                f'<a href="{auth_url}" target="_self" style="text-decoration: none;">'
                '<div style="background-color: #4285F4; color: white; text-align: center; padding: 12px; '
                'border-radius: 8px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">'
                '🔴 Iniciar sesión con Google'
                '</div></a>', 
                unsafe_allow_html=True
            )
        except:
            st.error("El enlace de inicio de sesión no se pudo construir. Revisa la configuración de tus credenciales de Google.")

# =========================================================================
# APLICACIÓN PRINCIPAL (SOLO ACCESIBLE SI ESTÁ AUTENTICADO)
# =========================================================================
else:
    # Barra lateral de navegación con perfil de usuario
    st.sidebar.image(st.session_state.usuario_info.get("picture", "https://placeholder.com"), width=80)
    st.sidebar.write(f"¡Hola, **{st.session_state.usuario_info.get('name', 'Edwin')}**!")
    st.sidebar.caption(st.session_state.usuario_info.get("email"))
    
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario_info = None
        st.rerun()
        
    st.sidebar.divider()
    opcion = st.sidebar.radio("Selecciona una sección:", ["📉 Control de Peso Corporal", "🏋️ Récords de Fuerza Gym"])

    SPREADSHEET_ID = "1hZuLJED8zV7y4VvQ_D6oewPjaGd1lijnbo4rznzo82Q"

    # Intentar conexión con la hoja de Google Sheets para leer los datos
    try:
        # Reutilizamos la conexión de gsheets básica
        df_p_show = pd.read_csv(f"https://google.com{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=PesoCorporal")
        df_g_show = pd.read_csv(f"https://google.com{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=R%C3%A9cordsGym")
    except Exception as e:
        df_p_show = pd.DataFrame(columns=["Fecha", "Peso Corporal (kg)", "Variación Semanal (kg)", "Notas"])
        df_g_show = pd.DataFrame(columns=["Fecha", "Ejercicio", "Peso Levantado (lbs/kg)", "Repeticiones", "RPE (Esfuerzo 1-10)"])

    if opcion == "📉 Control de Peso Corporal":
        st.subheader("📉 Pérdida de Peso Corporal")
        st.markdown("### Objetivo: Pérdida de grasa manteniendo masa muscular")
        
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Meta de Peso", value="65 - 66 kg")
        col2.metric(label="Fecha Límite", value="Diciembre 2026")
        
        fecha_actual = datetime.date.today()
        fecha_meta = datetime.date(2026, 12, 1)
        dias_restantes = (fecha_meta - fecha_actual).days
        col3.metric(label="Días para la Meta", value=f"{max(0, dias_restantes)} días")
        
        st.divider()
        
        # El formulario ahora solo muestra la información histórica de forma segura
        if not df_p_show.empty:
            df_p_show["Peso Corporal (kg)"] = pd.to_numeric(df_p_show["Peso Corporal (kg)"], errors='coerce')
            fig_p = px.line(df_p_show, x="Fecha", y="Peso Corporal (kg)", markers=True, title="Evolución del Peso Real vs Meta")
            fig_p.add_hline(y=65.5, line_dash="dash", line_color="green", annotation_text="Meta (65-66 kg)")
            st.plotly_chart(fig_p, use_container_width=True)
            st.dataframe(df_p_show, use_container_width=True, hide_index=True)
        else:
            st.info("No hay registros en la nube todavía en la hoja 'PesoCorporal'.")

    elif opcion == "🏋️ Récords de Fuerza Gym":
        st.subheader("🏋️ Registro de Sobrecarga Progresiva")
        st.markdown("### Objetivo: Subir la fuerza en el gimnasio para evitar perder músculo en el déficit")
        
        st.divider()
        
        if not df_g_show.empty:
            st.subheader("📊 Historial General de Levantamientos")
            st.dataframe(df_g_show, use_container_width=True, hide_index=True)
            
            st.subheader("📈 Progreso por Ejercicio Específico")
            ejercicio_filtro = st.selectbox("Selecciona un ejercicio para ver tu gráfica de aumento de carga:", df_g_show["Ejercicio"].unique())
            df_filtrado = df_g_show[df_g_show["Ejercicio"] == ejercicio_filtro]
            df_filtrado["Peso Levantado (lbs/kg)"] = pd.to_numeric(df_filtrado["Peso Levantado (lbs/kg)"], errors='coerce')
            
            fig_g = px.line(df_filtrado, x="Fecha", y="Peso Levantado (lbs/kg)", markers=True, text="Repeticiones", title=f"Evolución de Carga en: {ejercicio_filtro}")
            st.plotly_chart(fig_g, use_container_width=True)
        else:
            st.info("No hay registros en la nube todavía en la hoja 'RécordsGym'.")

