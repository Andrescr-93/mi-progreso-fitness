import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import requests
from streamlit_oauth import OAuth2Component

# =========================================================================
# CONFIGURACIÓN INICIAL Y LLAMADO SEGURO A SECRETS
# =========================================================================
st.set_page_config(page_title="PowerFitness - Peso & Sobrecarga", page_icon="💪", layout="wide")

# Lectura cifrada y segura desde tus Secrets configurados
CLIENT_ID = st.secrets["google_oauth"]["client_id"]
CLIENT_SECRET = st.secrets["google_oauth"]["client_secret"]

AUTHORIZE_URL = "https://google.com"
TOKEN_URL = "https://googleapis.com"

SPREADSHEET_ID = "1hZuLJED8zV7y4VvQ_D6oewPjaGd1lijnbo4rznzo82Q"
SCRIPT_URL = "https://google.com"

# Inicializar componente OAuth2 de Google
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, "")

# Inicializar estados de la sesión si no existen
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# =========================================================================
# PANTALLA DE INICIO DE SESIÓN CON GOOGLE
# =========================================================================
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>💪 PowerFitness Tracker</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>Gestiona tu composición corporal y récords de fuerza de forma segura</h4>", unsafe_allow_html=True)
    st.write("---")
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        st.info("Para acceder a tus paneles y sincronizar con Google Sheets, inicia sesión con tu cuenta de Google.")
        
        # DETECCIÓN AUTOMÁTICA DE URL (Local o Nube)
        headers = st.context.headers
        host = headers.get("Host", "localhost:8501")
        is_https = "https" in headers.get("X-Forwarded-Proto", "")
        protocol = "https" if is_https else "http"
        current_url = f"{protocol}://{host}/"
        
        # Renderizar el botón nativo de Google Sign-In
        result = oauth2.authorize_button(
            name="Continuar con Google",
            icon="https://wikimedia.org",
            redirect_uri=current_url,
            scope="openid email profile",
            key="google_auth",
            use_container_width=True
        )
        
        # Procesar el acceso tras un inicio de sesión exitoso
        if result and "token" in result:
            # Saca de manera segura el correo del flujo sin requerir librerías extras de parseo de JWT
            access_token = result["token"]["access_token"]
            userinfo_response = requests.get(
                "https://googleapis.com",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if userinfo_response.status_code == 200:
                user_info = userinfo_response.json()
                email_detectado = user_info.get("email", "").lower()
                
                # Filtro de seguridad obligatorio para tu correo autorizado
                if email_detectado == "ciberth2011@gmail.com":
                    st.session_state.autenticado = True
                    st.session_state.user_email = email_detectado
                    st.session_state.user_name = user_info.get("name", "Edwin")
                    st.success(f"¡Bienvenido {st.session_state.user_name}!")
                    st.rerun()
                else:
                    st.error("Acceso denegado. Este correo de Google no se encuentra autorizado.")
            else:
                st.error("Fallo en la validación de identidad con Google.")

# =========================================================================
# APLICACIÓN PRINCIPAL (ACCESIBLE TRAS LOGUEARSE)
# =========================================================================
else:
    # Barra lateral de usuario
    st.sidebar.markdown(f"### ¡Hola, **{st.session_state.user_name}**! 👋")
    st.sidebar.caption(st.session_state.user_email)
    
    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.rerun()
        
    st.sidebar.divider()
    opcion = st.sidebar.radio("Navegación del Tracker:", ["📉 Control de Peso Corporal", "🏋️ Récords de Fuerza Gym"])

    # Descargar bases de datos históricas de Google Sheets de manera pública
    try:
        df_p_show = pd.read_csv(f"https://google.com{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=PesoCorporal")
        df_g_show = pd.read_csv(f"https://google.com{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=R%C3%A9cordsGym")
    except Exception as e:
        df_p_show = pd.DataFrame(columns=["Fecha", "Peso Corporal (kg)", "Variación Semanal (kg)", "Notas"])
        df_g_show = pd.DataFrame(columns=["Fecha", "Ejercicio", "Peso Levantado (lbs/kg)", "Repeticiones", "RPE (Esfuerzo 1-10)"])

    # =========================================================================
    # SECCIÓN 1: PESO CORPORAL
    # =========================================================================
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
        
        with st.form("formulario_peso", clear_on_submit=True):
            st.subheader("📝 Registrar Peso en Ayunas")
            fecha_w = st.date_input("Fecha de pesaje:", datetime.date.today(), key="fecha_peso")
            peso_w = st.number_input("Peso (kg):", min_value=30.0, max_value=150.0, value=76.0, step=0.1, format="%.1f")
            notas_w = st.text_input("Notas de la semana:", placeholder="Ej: Energía alta, buen descanso...")
            boton_w = st.form_submit_button("🚀 Guardar Peso en Google Sheets")
            
        if boton_w:
            if SCRIPT_URL:
                variacion = 0.0
                if not df_p_show.dropna(how='all').empty:
                    try:
                        df_limpio = df_p_show.dropna(subset=["Peso Corporal (kg)"])
                        ultimo_peso = float(df_limpio.iloc[-1]["Peso Corporal (kg)"])
                        variacion = round(peso_w - ultimo_peso, 2)
                    except:
                        pass
                
                datos_enviar = {
                    "sheet": "PesoCorporal",
                    "Fecha": str(fecha_w),
                    "Peso Corporal (kg)": str(peso_w),
                    "Variación Semanal (kg)": str(variacion),
                    "Notas": str(notas_w)
                }
                
                try:
                    response = requests.post(SCRIPT_URL, json=datos_enviar)
                    if response.status_code == 200:
                        st.success("¡Peso guardado exitosamente!")
                        st.rerun()
                    else:
                        st.error(f"Error en comunicación. Código: {response.status_code}")
                except Exception as ex:
                    st.error(f"Error de red: {ex}")

        # Graficar peso histórico
        df_p_show = df_p_show.dropna(subset=["Fecha", "Peso Corporal (kg)"], how="any")
        if not df_p_show.empty:
            df_p_show["Peso Corporal (kg)"] = pd.to_numeric(df_p_show["Peso Corporal (kg)"], errors='coerce')
            df_p_show = df_p_show.sort_values(by="Fecha")
            
            fig_p = px.line(df_p_show, x="Fecha", y="Peso Corporal (kg)", markers=True, title="Evolución del Peso Real vs Meta")
            fig_p.add_hline(y=65.5, line_dash="dash", line_color="green", annotation_text="Meta (65-66 kg)")
            st.plotly_chart(fig_p, use_container_width=True)
            st.dataframe(df_p_show, use_container_width=True, hide_index=True)
        else:
            st.info("Sincronizando registros con la nube... Si ya guardaste datos, refresca la página en 5 segundos.")

    # =========================================================================
    # SECCIÓN 2: RÉCORDS DEL GIMNASIO
    # =========================================================================
    elif opcion == "🏋️ Récords de Fuerza Gym":
        st.subheader("🏋️ Registro de Sobrecarga Progresiva")
        st.markdown("### Objetivo: Subir la fuerza en el gimnasio para evitar perder músculo en el déficit")
        
        st.divider()
        
        with st.form("formulario_gym", clear_on_submit=True):
            st.subheader("💪 Registrar Serie Pesada")
            fecha_g = st.date_input("Fecha del entrenamiento:", datetime.date.today(), key="fecha_gym")
            ejercicio_g = st.selectbox("Selecciona el Ejercicio:", ["Press de Banca (Pecho)", "Sentadilla Libre (Pierna)", "Peso Muerto (Espalda/Glúteo)", "Press Militar (Hombro)", "Dominadas / Polea Alta", "Curl de Bíceps", "Extensión de Tríceps"])
            
            col_g1, col_g2, col_g3 = st.columns(3)
