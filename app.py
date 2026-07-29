import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import requests

# Configuración inicial de la página
st.set_page_config(page_title="Fitness Tracker - Dieta & Gym", page_icon="💪", layout="wide")

# Inicializar variables de sesión para el Login si no existen
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_email" not in st.session_state:
    st.session_state.usuario_email = None

# =========================================================================
# PANTALLA DE INICIO DE SESIÓN (LOGIN)
# =========================================================================
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>💪 Mi Progreso Fitness</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>Registra tu peso y sobrecarga progresiva de forma segura en la nube</h4>", unsafe_allow_html=True)
    st.divider()
    
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l2:
        st.info("Para proteger tu privacidad y sincronizar tus datos con Google Sheets, por favor introduce tu correo autorizado.")
        
        with st.form("login_form", clear_on_submit=False):
            email_input = st.text_input("Correo electrónico de Google:", placeholder="ejemplo@gmail.com")
            boton_login = st.form_submit_button("🔑 Verificar Acceso")
            
        if boton_login:
            if email_input.strip().lower() == "ciberth2011@gmail.com":
                st.session_state.autenticado = True
                st.session_state.usuario_email = email_input.strip().lower()
                st.success("¡Acceso concedido!")
                st.rerun()
            else:
                st.error("Acceso denegado. Este correo no se encuentra en la lista de usuarios autorizados.")

# =========================================================================
# APLICACIÓN PRINCIPAL (SOLO ACCESIBLE SI PASÓ LA VERIFICACIÓN)
# =========================================================================
else:
    st.sidebar.write(f"¡Hola, **Edwin**!")
    st.sidebar.caption(st.session_state.usuario_email)
    
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario_email = None
        st.rerun()
        
    st.sidebar.divider()
    opcion = st.sidebar.radio("Selecciona una sección:", ["📉 Control de Peso Corporal", "🏋️ Récords de Fuerza Gym"])

    SPREADSHEET_ID = "1hZuLJED8zV7y4VvQ_D6oewPjaGd1lijnbo4rznzo82Q"
    
    # URL FIJA ASIGNADA DIRECTAMENTE PARA EVITAR ERRORES DE SECRETS
    SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzH4Cmjq12LHH4MbzYQ9uAkWH2u_qdcAdu7170N45CeUAfBtMqVIgByBji-nYZJ8yrJ_Q/exec"

    # Intentar leer los datos históricos de Google Sheets de forma pública
    try:
        df_p_show = pd.read_csv(f"https://google.com{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=PesoCorporal")
        df_g_show = pd.read_csv(f"https://google.com{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=R%C3%A9cordsGym")
    except Exception as e:
        df_p_show = pd.DataFrame(columns=["Fecha", "Peso Corporal (kg)", "Variación Semanal (kg)", "Notas"])
        df_g_show = pd.DataFrame(columns=["Fecha", "Ejercicio", "Peso Levantado (lbs/kg)", "Repeticiones", "RPE (Esfuerzo 1-10)"])

    # =========================================================================
    # PANTALLA 1: PESO CORPORAL
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
                        ultimo_peso = float(df_p_show.dropna(how='all').iloc[-1]["Peso Corporal (kg)"])
                        variacion = round(peso_w - ultimo_peso, 2)
                    except:
                        pass
                
                datos_enviar = {
                    "Fecha": str(fecha_w),
                    "Peso Corporal (kg)": str(peso_w),
                    "Variación Semanal (kg)": str(variacion),
                    "Notas": str(notas_w)
                }
                
                response = requests.post(SCRIPT_URL, json=datos_enviar)
                if response.status_code == 200:
                    st.success("¡Peso guardado exitosamente en tu Google Sheets en la nube!")
                    st.rerun()
                else:
                    st.error("Error al conectar con el script de Google. Verifica la configuración.")
            else:
                st.error("Falta configurar la variable SCRIPT_URL en el código.")

        if not df_p_show.dropna(how='all').empty:
            df_p_show["Peso Corporal (kg)"] = pd.to_numeric(df_p_show["Peso Corporal (kg)"], errors='coerce')
            fig_p = px.line(df_p_show, x="Fecha", y="Peso Corporal (kg)", markers=True, title="Evolución del Peso Real vs Meta")
            fig_p.add_hline(y=65.5, line_dash="dash", line_color="green", annotation_text="Meta (65-66 kg)")
            st.plotly_chart(fig_p, use_container_width=True)
            st.dataframe(df_p_show, use_container_width=True, hide_index=True)
        else:
            st.info("No hay registros en la nube todavía en la hoja 'PesoCorporal'.")

    # =========================================================================
    # PANTALLA 2: RÉCORDS DEL GIMNASIO
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
            peso_g = col_g1.number_input("Peso Levantado:", min_value=0.0, max_value=500.0, value=20.0, step=0.5, format="%.1f")
            reps_g = col_g2.number_input("Repeticiones logradas:", min_value=1, max_value=50, value=10, step=1)
            rpe_g = col_g3.slider("Nivel de Esfuerzo (RPE 1-10):", min_value=1, max_value=10, value=8)
            boton_g = st.form_submit_button("🚀 Guardar Serie en Google Sheets")
            
        if boton_g:
            if SCRIPT_URL:
                datos_enviar_g = {
                    "Fecha": str(fecha_g),
                    "Ejercicio": str(ejercicio_g),
                    "Peso Levantado (lbs/kg)": str(peso_g),
                    "Repeticiones": str(reps_g),
                    "E1-10": str(rpe_g)
                }
                response = requests.post(SCRIPT_URL, json=datos_enviar_g)
                if response.status_code == 200:
                    st.success(f"¡Récord de {ejercicio_g} guardado en la nube con éxito!")
                    st.rerun()
                else:
                    st.error("Error al conectar con el script de Google. Verifica la configuración.")
            else:
                st.error("Falta configurar la variable SCRIPT_URL en el código.")

        if not df_g_show.dropna(how='all').empty:
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
