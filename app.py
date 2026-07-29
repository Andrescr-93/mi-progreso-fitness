import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

# Configuración inicial de la página
st.set_page_config(page_title="Fitness Tracker - Dieta & Gym", page_icon="💪", layout="wide")

# Inicializar variables de sesión para el Login si no existen
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_email" not in st.session_state:
    st.session_state.usuario_email = None

# =========================================================================
# PANTALLA DE INICIO DE SESIÓN (LOGIN SIMPLIFICADO Y SEGURO)
# =========================================================================
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center;'>💪 Mi Progreso Fitness</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>Registra tu peso y sobrecarga progresiva de forma segura en la nube</h4>", unsafe_allow_html=True)
    st.divider()
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.info("Para proteger tu privacidad y sincronizar tus datos con Google Sheets, por favor introduce tu correo autorizado.")
        
        with st.form("login_form", clear_on_submit=False):
            email_input = st.text_input("Correo electrónico de Google:", placeholder="ejemplo@gmail.com")
            boton_login = st.form_submit_button("🔑 Verificar Acceso")
            
        if boton_login:
            # Validar que el correo ingresado sea exactamente tu usuario de prueba autorizado
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
    # Barra lateral de navegación con perfil de usuario
    st.sidebar.write(f"¡Hola, **Edwin**!")
    st.sidebar.caption(st.session_state.usuario_email)
    
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario_email = None
        st.rerun()
        
    st.sidebar.divider()
    opcion = st.sidebar.radio("Selecciona una sección:", ["📉 Control de Peso Corporal", "🏋️ Récords de Fuerza Gym"])

    SPREADSHEET_ID = "1hZuLJED8zV7y4VvQ_D6oewPjaGd1lijnbo4rznzo82Q"

    try:
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

