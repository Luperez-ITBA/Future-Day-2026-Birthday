import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Paradoja del Cumpleaños - ITBA", layout="wide", initial_sidebar_state="collapsed")

# --- MEMORIA (Session State) ---
if 'cumples_registrados' not in st.session_state:
    st.session_state.cumples_registrados = []
    st.session_state.hay_coincidencia = False
    st.session_state.ultima_coincidencia = None

# Meses en español
MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

# --- ESTILOS CSS UNIFICADOS ---
st.markdown("""
    <style>
    /* Fondo principal */
    .main { background-color: #f8fafc; }
    
    /* Forzar el cursor de 'manito' en los selectbox */
    div[data-baseweb="select"] > div {
        cursor: pointer !important;
    }
    
    /* Forzar la manito en los botones */
    .stButton > button {
        cursor: pointer !important;
    }
    </style>
""", unsafe_allow_html=True)


# --- CABECERA Y CONTROLES (Reemplaza a la sidebar) ---
col_logo, col_titulo, col_reinicio = st.columns([1, 3, 1])

with col_logo:
    try:
        st.image('logo_itba.png', width=150)
    except:
        st.write("### ITBA")

with col_titulo:
    st.title("🎂 La Paradoja del Cumpleaños")

with col_reinicio:
    st.write("") # Espaciador para alinear el botón
    if st.button("🗑️ Reiniciar Experimento", use_container_width=True):
        st.session_state.cumples_registrados = []
        st.session_state.hay_coincidencia = False
        st.session_state.ultima_coincidencia = None
        st.rerun()

st.write("---")

# --- SISTEMA DE PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["🎁 Experimento en Vivo", "📊 Simulación Monte Carlo", "🧠 ¿Por qué sucede?"])

# --- TAB 1: EXPERIMENTO EN VIVO ---
with tab1:
    st.subheader("¿Habrá dos personas aquí que cumplan el mismo día?")
    
    if not st.session_state.hay_coincidencia:
        st.markdown("Invitá a los participantes a registrar su cumpleaños:")
        
        # ACA ESTÁ EL SELECTBOX PARA LOS DÍAS
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            dia_elegido = st.selectbox("Día:", list(range(1, 32)))
        with col_sel2:
            mes_elegido = st.selectbox("Mes:", MESES)
            
        fecha_texto = f"{dia_elegido} de {mes_elegido}"
        
        if st.button("➕ Agregar Cumpleaños", type="primary"):
            if fecha_texto in st.session_state.cumples_registrados:
                st.session_state.hay_coincidencia = True
                st.session_state.ultima_coincidencia = fecha_texto
                st.session_state.cumples_registrados.append(fecha_texto)
                st.balloons()
            else:
                st.session_state.cumples_registrados.append(fecha_texto)
            st.rerun()
            
    else:
        st.success(f"¡HAY COINCIDENCIA! 🎉 Dos personas cumplen el **{st.session_state.ultima_coincidencia}**.")
        st.markdown(f"**Cantidad de personas necesarias:** {len(st.session_state.cumples_registrados)}")
        
        if st.button("🔄 Reiniciar para el siguiente grupo..."):
            st.session_state.cumples_registrados = []
            st.session_state.hay_coincidencia = False
            st.session_state.ultima_coincidencia = None
            st.rerun()
            
    # Muestra los cumples ingresados
    if len(st.session_state.cumples_registrados) > 0:
        st.write("---")
        st.write(f"**Registros actuales ({len(st.session_state.cumples_registrados)} personas):**")
        
        cols = st.columns(4)
        for i, cumple in enumerate(st.session_state.cumples_registrados):
            with cols[i % 4]:
                if st.session_state.hay_coincidencia and cumple == st.session_state.ultima_coincidencia:
                    st.error(f"👤 {i+1}: {cumple}")
                else:
                    st.info(f"👤 {i+1}: {cumple}")


# --- TAB 2: SIMULACIÓN MONTE CARLO ---
with tab2:
    st.subheader("Simulemos miles de habitaciones virtuales")
    st.markdown("¿Qué probabilidad hay de encontrar coincidencias según el tamaño del grupo?")
    
    cant_personas = st.slider("Tamaño del grupo de personas:", min_value=2, max_value=75, value=23)
    iteraciones = 2000
    
    if st.button(f"🎲 Simular {iteraciones} habitaciones con {cant_personas} personas"):
        coincidencias_simuladas = 0
        
        progress_bar = st.progress(0)
        
        for i in range(iteraciones):
            # Asumimos año no bisiesto de 365 días
            cumples_random = np.random.randint(1, 366, size=cant_personas)
            if len(cumples_random) != len(set(cumples_random)):
                coincidencias_simuladas += 1
                
            if i % 100 == 0:
                progress_bar.progress(i / iteraciones)
                
        progress_bar.progress(1.0)
        
        prob_empirica = coincidencias_simuladas / iteraciones
        
        st.success(f"En {coincidencias_simuladas} de las {iteraciones} habitaciones hubo al menos una coincidencia.")
        st.metric(f"Probabilidad Estimada (Simulación)", f"{prob_empirica*100:.1f}%")
        
        # Gráfico estático general
        fig, ax = plt.subplots(figsize=(10, 4))
        n_vals = np.arange(1, 76)
        # Fórmula teórica
        prob_teorica = 1 - np.exp(-n_vals * (n_vals - 1) / (2 * 365))
        
        ax.plot(n_vals, prob_teorica * 100, color='#0074D9', linewidth=2.5, label="Probabilidad Teórica")
        ax.axhline(50, color='#e74c3c', linestyle='--', alpha=0.7, label="50% (n=23)")
        ax.axvline(23, color='#e74c3c', linestyle='--', alpha=0.7)
        ax.axhline(99, color='#2ecc71', linestyle='--', alpha=0.7, label="99% (n=57)")
        ax.axvline(57, color='#2ecc71', linestyle='--', alpha=0.7)
        ax.scatter([23, 57], [50, 99], color='black', zorder=5)
        ax.annotate('n=23', xy=(24, 40), fontsize=10)
        ax.annotate('n=57', xy=(58, 85), fontsize=10)
        
        ax.set_title("Probabilidad Teórica vs Tamaño del Grupo")
        ax.set_xlabel("Número de Personas en la Habitación")
        ax.set_ylabel("Probabilidad de Coincidencia (%)")
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        st.pyplot(fig)


# --- TAB 3: ¿POR QUÉ SUCEDE? (MATEMÁTICA) ---
with tab3:
    st.subheader("La Matemática detrás de la Intuición que Engaña")
    
    st.markdown("""
    ### 1. El Método de las "Casillas Ocupadas"
    Imaginá el año como 365 casillas vacías. Es más fácil calcular la probabilidad de que **nadie** coincida:
    * La **1ra persona** elige cualquier casilla (365/365).
    * La **2da persona**, para no coincidir, debe elegir una de las **364** restantes.
    * La **3ra persona** debe elegir una de las **363**...
    """)
    
    st.latex(r"P(\text{no coincidencia}) = \frac{365}{365} \times \frac{364}{365} \times \frac{363}{365} \times \dots \times \frac{365-n+1}{365}")
    
    st.markdown("Finalmente, la probabilidad de que **al menos una pareja coincida** es el complemento:")
    st.latex(r"P(\text{coincidencia}) = 1 - P(\text{no coincidencia})")
    
    st.markdown("""
    ### 2. El Poder de las Parejas (Combinatoria)
    La clave es que no buscamos a alguien que cumpla años como **VOS**, sino **cualquier pareja** que coincida entre sí. 
    
    En un grupo de **23 personas**, existen:
    """)
    
    st.latex(r"\binom{23}{2} = \frac{23 \times 22}{2} = 253 \text{ parejas posibles}")
    
    st.markdown("""
    ¡Estás haciendo 253 comparaciones simultáneas! Con 253 cruces posibles y 365 días disponibles, tiene mucho más sentido que la probabilidad cruce el 50%.
    """)
