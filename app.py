import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# Configuración inicial de la página
st.set_page_config(page_title="Fitness Tracker - Dieta & Gym", page_icon="💪", layout="wide")

st.title("💪 Mi Progreso - Conectado a la Nube")

# Conexión automática a Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Leer los datos existentes de ambas pestañas de la hoja de cálculo
    df_p_base = conn.read(worksheet="PesoCorporal", ttl="0m")
    df_g_base = conn.read(worksheet="RécordsGym", ttl="0m")
    
    # Limpiar datos vacíos y asegurar formato correcto
    df_p_show = df_p_base.dropna(how="all")
    df_g_show = df_g_base.dropna(how="all")
except Exception as e:
    st.error("Configurando conexión con Google Sheets... Sigue los pasos de configuración de Secrets.")
    df_p_show = pd.DataFrame(columns=["Fecha", "Peso Corporal (kg)", "Variación Semanal (kg)", "Notas"])
    df_g_show = pd.DataFrame(columns=["Fecha", "Ejercicio", "Peso Levantado (lbs/kg)", "Repeticiones", "RPE (Esfuerzo 1-10)"])

# Barra lateral de navegación
st.sidebar.title("Navigation")
opcion = st.sidebar.radio("Selecciona una sección:", ["📉 Control de Peso Corporal", "🏋️ Récords de Fuerza Gym"])

# =========================================================================
# PANTALLA 1: CONTROL DE PESO CORPORAL
# =========================================================================
if opcion == "📉 Control de Peso Corporal":
    st.subheader("📉 Pérdida de Peso Corporal")
    st.markdown("### Objetivo: Pérdida de grasa manteniendo masa muscular [source: 1]")
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Meta de Peso [source: 1]", value="65 - 66 kg")
    col2.metric(label="Fecha Límite [source: 1]", value="Diciembre 2026")
    
    fecha_actual = datetime.date.today()
    fecha_meta = datetime.date(2026, 12, 1)
    dias_restantes = (fecha_meta - fecha_actual).days
    col3.metric(label="Días para la Meta", value=f"{max(0, dias_restantes)} días")
    
    st.divider()
    
    with st.form("formulario_peso", clear_on_submit=True):
        st.subheader("📝 Registrar Peso en Ayunas")
        fecha_w = st.date_input("Fecha de pesaje:", datetime.date.today(), key="fecha_peso")
        peso_w = st.number_input("Peso (kg):", min_value=30.0, max_value=150.0, step=0.1, format="%.1f")
        notas_w = st.text_input("Notas de la semana:", placeholder="Ej: Energía alta, buen descanso...")
        boton_w = st.form_submit_button("Guardar Peso en Google Sheets")
        
    if boton_w:
        variacion = round(peso_w - df_p_show.iloc[-1]["Peso Corporal (kg)"], 2) if not df_p_show.empty else 0.0
        nuevo_p = pd.DataFrame([{"Fecha": fecha_w.strftime("%Y-%m-%d"), "Peso Corporal (kg)": peso_w, "Variación Semanal (kg)": variacion, "Notas": notas_w}])
        
        df_p_final = pd.concat([df_p_show, nuevo_p], ignore_index=True)
        conn.update(worksheet="PesoCorporal", data=df_p_final)
        st.success("¡Peso guardado permanentemente en la nube!")
        st.rerun()

    if not df_p_show.empty:
        fig_p = px.line(df_p_show, x="Fecha", y="Peso Corporal (kg)", markers=True, title="Evolución del Peso Real vs Meta")
        fig_p.add_hline(y=65.5, line_dash="dash", line_color="green", annotation_text="Meta (65-66 kg) [source: 1]")
        st.plotly_chart(fig_p, use_container_width=True)
        st.dataframe(df_p_show, use_container_width=True, hide_index=True)
    else:
        st.info("No hay registros en la nube todavía.")

# =========================================================================
# PANTALLA 2: RÉCORDS DE FUERZA (GYM)
# =========================================================================
elif opcion == "🏋️ Récords de Fuerza Gym":
    st.subheader("🏋️ Registro de Sobrecarga Progresiva")
    st.markdown("### Objetivo: Subir la fuerza en el gimnasio para evitar perder músculo en el déficit [source: 1]")
    
    st.divider()
    
    with st.form("formulario_gym", clear_on_submit=True):
        st.subheader("💪 Registrar Serie Pesada")
        fecha_g = st.date_input("Fecha del entrenamiento:", datetime.date.today(), key="fecha_gym")
        ejercicio_g = st.selectbox("Selecciona el Ejercicio:", ["Press de Banca (Pecho)", "Sentadilla Libre (Pierna)", "Peso Muerto (Espalda/Glúteo)", "Press Militar (Hombro)", "Dominadas / Polea Alta", "Curl de Bíceps", "Extensión de Tríceps"])
        
        col_g1, col_g2, col_g3 = st.columns(3)
        peso_g = col_g1.number_input("Peso Levantado:", min_value=0.0, max_value=500.0, step=0.5, format="%.1f")
        reps_g = col_g2.number_input("Repeticiones logradas:", min_value=1, max_value=50, step=1)
        rpe_g = col_g3.slider("Nivel de Esfuerzo (RPE 1-10):", min_value=1, max_value=10, value=8)
        boton_g = st.form_submit_button("Guardar Serie en la Nube")
        
    if boton_g:
        nuevo_g = pd.DataFrame([{"Fecha": fecha_g.strftime("%Y-%m-%d"), "Ejercicio": ejercicio_g, "Peso Levantado (lbs/kg)": peso_g, "Repeticiones": reps_g, "RPE (Esfuerzo 1-10)": rpe_g}])
        df_g_final = pd.concat([df_g_show, nuevo_g], ignore_index=True)
        conn.update(worksheet="RécordsGym", data=df_g_final)
        st.success(f"¡Récord de {ejercicio_g} guardado de forma permanente!")
        st.rerun()

    if not df_g_show.empty:
        st.subheader("📊 Historial General de Levantamientos")
        st.dataframe(df_g_show, use_container_width=True, hide_index=True)
        
        st.subheader("📈 Progreso por Ejercicio Específico")
        ejercicio_filtro = st.selectbox("Selecciona un ejercicio para ver tu gráfica de aumento de carga:", df_g_show["Ejercicio"].unique())
        df_filtrado = df_g_show[df_g_show["Ejercicio"] == ejercicio_filtro]
        
        fig_g = px.line(df_filtrado, x="Fecha", y="Peso Levantado (lbs/kg)", markers=True, text="Repeticiones", title=f"Evolución de Carga en: {ejercicio_filtro}")
        st.plotly_chart(fig_g, use_container_width=True)
