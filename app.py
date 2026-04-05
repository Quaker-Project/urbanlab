import streamlit as st
import random
import json
from openai import OpenAI

# 🔑 API (pon tu clave en Streamlit secrets)
client = OpenAI(api_key=st.secrets["1234"])

st.set_page_config(page_title="UrbanLab Criminología", layout="centered")

st.title("🏙️ UrbanLab: Simulación de Política Criminal")

# -----------------------------
# ESTADO INICIAL
# -----------------------------
if "fase" not in st.session_state:
    st.session_state.fase = "inicio"

if "historial" not in st.session_state:
    st.session_state.historial = []

if "otros_barrios" not in st.session_state:
    st.session_state.otros_barrios = {
        "Barrio Norte": {"policia": 50, "delincuencia": 60},
        "Barrio Sur": {"policia": 30, "delincuencia": 70}
    }

# -----------------------------
# FUNCIÓN IA
# -----------------------------
def interpretar_plan_ia(plan_texto):
    
    prompt = f"""
    Eres experto en criminología urbana.

    Analiza este plan:
    "{plan_texto}"

    Devuelve SOLO JSON con:
    policia (-10 a 10)
    cohesion (-10 a 10)
    control_informal (-10 a 10)
    desorganizacion (-10 a 10)
    pobreza (-10 a 10)
    tipo_estrategia (punitiva, estructural, mixta)
    coherencia_teorica (0-10)
    evaluacion (breve feedback)
    """
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    
    return json.loads(response.choices[0].message.content)

# -----------------------------
# INICIO
# -----------------------------
if st.session_state.fase == "inicio":
    st.markdown("""
    ## 🎯 Misión
    
    Reduce la delincuencia SIN destruir la cohesión social.
    
    - Diseña políticas reales
    - Justifica con teoría
    - Observa consecuencias
    
    """)

    if st.button("Comenzar"):
        st.session_state.fase = "barrio"

# -----------------------------
# BARRIOS
# -----------------------------
if st.session_state.fase == "barrio":
    
    barrios = {
        "Movilidad alta": {"desorganizacion": 75, "cohesion": 30, "pobreza": 50},
        "Pobreza estructural": {"desorganizacion": 65, "cohesion": 40, "pobreza": 80},
        "Diversidad conflictiva": {"desorganizacion": 60, "cohesion": 35, "pobreza": 60}
    }
    
    barrio = st.selectbox("Selecciona tu barrio", list(barrios.keys()))
    
    if st.button("Confirmar"):
        base = barrios[barrio]
        
        st.session_state.barrio = {
            "nombre": barrio,
            "desorganizacion": base["desorganizacion"],
            "cohesion": base["cohesion"],
            "control": 30,
            "pobreza": base["pobreza"],
            "policia": 40,
            "delincuencia": 60
        }
        
        st.session_state.ronda = 1
        st.session_state.fase = "juego"

# -----------------------------
# JUEGO
# -----------------------------
if st.session_state.fase == "juego":
    
    b = st.session_state.barrio
    
    st.subheader(f"📍 Ronda {st.session_state.ronda}/3")
    
    st.write(b)
    
    plan = st.text_area("🧠 Diseña tu plan")
    
    if st.button("Ejecutar plan"):
        
        try:
            datos = interpretar_plan_ia(plan)
        except:
            st.error("Error con IA. Reformula tu plan.")
            st.stop()
        
        # aplicar cambios
        b["policia"] += datos["policia"]
        b["cohesion"] += datos["cohesion"]
        b["control"] += datos["control_informal"]
        b["desorganizacion"] += datos["desorganizacion"]
        b["pobreza"] += datos["pobreza"]
        
        # 🌍 INTERACCIÓN ENTRE BARRIOS (IA + reglas)
        if b["policia"] > 70:
            st.warning("🚨 Desplazamiento del delito a otros barrios")
            for ob in st.session_state.otros_barrios:
                st.session_state.otros_barrios[ob]["delincuencia"] += 5
        
        # evento aleatorio
        evento = random.choice(["crisis", "conflicto", "ninguno"])
        
        if evento == "crisis":
            st.warning("💥 Crisis económica")
            b["pobreza"] += 10
        
        if evento == "conflicto":
            st.warning("⚠️ Conflicto comunitario")
            b["cohesion"] -= 10
        
        # cálculo delito
        b["delincuencia"] = (
            b["desorganizacion"] * 0.4 +
            b["pobreza"] * 0.3 -
            b["cohesion"] * 0.3 -
            b["control"] * 0.2
        )
        
        # guardar historial
        st.session_state.historial.append({
            "ronda": st.session_state.ronda,
            "plan": plan,
            "resultado": b["delincuencia"],
            "tipo": datos["tipo_estrategia"],
            "coherencia": datos["coherencia_teorica"]
        })
        
        st.success(f"Delincuencia: {round(b['delincuencia'],2)}")
        st.write("🧠 Evaluación IA:", datos["evaluacion"])
        st.metric("Coherencia teórica", datos["coherencia_teorica"])
        
        st.session_state.ronda += 1
        
        if st.session_state.ronda > 3:
            st.session_state.fase = "final"

# -----------------------------
# INFORME FINAL
# -----------------------------
if st.session_state.fase == "final":
    
    st.title("🏁 Informe final")
    
    historial = st.session_state.historial
    
    delincuencia_final = st.session_state.barrio["delincuencia"]
    
    estrategias = [h["tipo"] for h in historial]
    
    informe = f"""
    INFORME FINAL
    
    Barrio: {st.session_state.barrio['nombre']}
    
    Delincuencia final: {round(delincuencia_final,2)}
    
    Estrategias utilizadas: {estrategias}
    
    Historial:
    {historial}
    """
    
    st.download_button(
        label="📥 Descargar informe",
        data=informe,
        file_name="informe_urbanlab.txt"
    )
    
    if delincuencia_final < 30:
        st.success("🎉 Excelente estrategia estructural")
    elif "punitiva" in estrategias:
        st.warning("⚠️ Dependencia del control formal")
    else:
        st.info("📊 Resultado mixto")
