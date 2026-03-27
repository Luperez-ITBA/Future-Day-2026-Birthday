import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Paradoja del Cumpleaños - ITBA", layout="wide")

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

# --- BARRA LATERAL ---
with st.sidebar:
    try:
        st.image('logo_itba.png', use_container_width=True)
    except:
        st.write("ITBA - Future Day")
    
    st.header("Controles")
    if st.button("🗑️ Reiniciar Experimento"):
        st.session_state.cumples_registrados = []
        st.session_state.hay_coincidencia = False
        st.session_state.ultima_coincidencia = None
        st.rerun()

# --- CUERPO PRINCIPAL ---
st.title("🎂 La Paradoja del Cumpleaños")
st.write("---")

tab1, tab2, tab3 = st.tabs(["🎁 Experimento en Vivo", "📊 Simulación Monte Carlo", "🧠 ¿Por qué sucede?"])

# --- TAB 1: EXPERIMENTO EN VIVO ---
with tab1:
    st.subheader("¿Habrá dos personas aquí que cumplan el mismo día?")
    
    if not st.session_state.hay_coincidencia:
        st.markdown("Invitá a los participantes a registrar su cumpleaños:")
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            mes_elegido = st.selectbox("Mes:", MESES)
        with col_sel2:
            dia_elegido = st.number_input("Día:", min_value=1, max_value=31, value=15)
        
        if st.button("✨ Registrar Cumpleaños", use_container_width=True):
            nueva_fecha = f"{dia_elegido} de {mes_elegido}"
            
            if nueva_fecha in st.session_state.cumples_registrados:
                st.session_state.hay_coincidencia = True
                st.session_state.ultima_coincidencia = nueva_fecha
                st.balloons()
            
            st.session_state.cumples_registrados.append(nueva_fecha)
            st.rerun()
    else:
        st.success(f"🎊 ¡COINCIDENCIA! Dos personas cumplen el **{st.session_state.ultima_coincidencia}**.")
        st.metric("Personas registradas hasta el 'Hit'", len(st.session_state.cumples_registrados))
        if st.button("🔄 Reiniciar para el siguiente grupo"):
            st.session_state.cumples_registrados = []
            st.session_state.hay_coincidencia = False
            st.rerun()

    st.write("---")
    st.write(f"### Invitados en el grupo actual: {len(st.session_state.cumples_registrados)}")
    
    if st.session_state.cumples_registrados:
        grid_cols = st.columns(6)
        for idx, c in enumerate(st.session_state.cumples_registrados):
            with grid_cols[idx % 6]:
                if st.session_state.hay_coincidencia and c == st.session_state.ultima_coincidencia:
                    st.error(f"📍 {c}")
                else:
                    st.info(f"🎂 {c}")

# --- TAB 2: SIMULACIÓN ---
with tab2:
    st.subheader("Simulación de Grupos Aleatorios")
    st.write("¿Qué pasa si repetimos este experimento miles de veces?")
    
    n_personas = st.slider("Elegí el tamaño del grupo (n):", 2, 100, 23)
    
    if st.button("🚀 Ejecutar 1000 simulaciones"):
        exitos = 0
        for _ in range(1000):
            grupo = [random.randint(1, 365) for _ in range(n_personas)]
            if len(grupo) != len(set(grupo)):
                exitos += 1
        
        st.metric(f"Probabilidad medida para n={n_personas}", f"{(exitos/1000)*100:.1f}%")
        
    x_teorico = np.arange(1, 101)
    y_teorico = [1 - np.prod([(365-i)/365 for i in range(n)]) for n in x_teorico]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x_teorico, y_teorico, color='#2ecc71', linewidth=2.5, label="Curva de Probabilidad")
    ax.axhline(0.5, color='red', linestyle='--', alpha=0.4, label="50% (n=23)")
    ax.axhline(0.99, color='orange', linestyle='--', alpha=0.4, label="99% (n=57)")
    
    ax.scatter([23, 57], [0.507, 0.99], color='black', zorder=5)
    ax.annotate('n=23 (50.7%)', (23, 0.52), fontweight='bold')
    ax.annotate('n=57 (99.0%)', (57, 0.94), fontweight='bold')
    
    ax.set_xlabel("Personas en el grupo")
    ax.set_ylabel("Probabilidad de coincidencia")
    ax.set_title("La Curva de la Paradoja")
    ax.grid(True, alpha=0.2)
    ax.legend()
    st.pyplot(fig)

# --- TAB 3: LA MATEMÁTICA ---
with tab3:
    st.subheader("🧠 ¿Por qué nuestra intuición nos engaña?")
    
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
    
    st.info("""
    💡 Con **253 parejas** comparándose entre sí, hay muchísimas oportunidades para que ocurra un "choque". 
    Es por esto que la probabilidad sube tan rápido:
    * Con **23 personas**, tenés un **50.7%** de probabilidad.
    * Con **57 personas**, ¡la probabilidad sube al **99%**! Es estadísticamente casi imposible no encontrar una coincidencia.
    """)