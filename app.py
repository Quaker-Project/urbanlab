import streamlit as st
import random
import json
import os
from openai import OpenAI

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
st.set_page_config(page_title="UrbanLab Criminología", layout="centered")

# 🔑 API KEY SEGURA
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ Falta configurar OPENAI_API_KEY en Streamlit Secrets")
    st.stop()

client = OpenAI(api_key=api_key)

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
    Eres experto en criminología urbana basado en la teoría de la desorganización social.

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
    evaluacion (breve feedback crítico en español)
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    contenido = response.choices[0].message.content

    try:
        return json.loads(contenido)
    except:
        return None

# -----------------------------
# PANTALLA INICIO
# -----------------------------
if st.session_state.fase == "inicio":
    st.markdown("""
    ## 🎯 Misión

    Diseñar una política criminal eficaz basada en la teoría de la desorganización social.

    ⚠️ Objetivo:
    - Reducir la delincuencia
    - SIN destruir la cohesión social
    - Actuando sobre causas estructurales

    👉 Pulsa comenzar
    """)

    if st.button("Comenzar"):
        st.session_state.fase = "barrio"

# -----------------------------
# SELECCIÓN DE BARRIO
# -----------------------------
if st.session_state.fase == "barrio":

    barrios = {
        "Alta movilidad residencial": {"desorganizacion": 75, "cohesion": 30, "pobreza": 50},
        "Pobreza estructural": {"desorganizacion": 65, "cohesion": 40, "pobreza": 80},
        "Diversidad cultural conflictiva": {"desorganizacion": 60, "cohesion": 35, "pobreza": 60}
    }

    barrio = st.selectbox("Selecciona tu barrio", list(barrios.keys()))

    if st.button("Confirmar barrio"):

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
# JUEGO PRINCIPAL
# -----------------------------
if st.session_state.fase == "juego":

    b = st.session_state.barrio

    st.subheader(f"📍 Ronda {st.session_state.ronda}/3")

    st.write("📊 Estado actual del barrio:", b)

    plan = st.text_area("🧠 Describe tu plan de intervención")

    if st.button("Ejecutar plan"):

        if not plan.strip():
            st.warning("Escribe un plan antes de ejecutar")
            st.stop()

        datos = interpretar_plan_ia(plan)

        if datos is None:
            st.error("⚠️ Error interpretando el plan. Sé más claro.")
            st.stop()

        # -------------------------
        # APLICAR EFECTOS
        # -------------------------
        b["policia"] += datos["policia"]
        b["cohesion"] += datos["cohesion"]
        b["control"] += datos["control_informal"]
        b["desorganizacion"] += datos["desorganizacion"]
        b["pobreza"] += datos["pobreza"]

        # -------------------------
        # INTERACCIÓN ENTRE BARRIOS
        # -------------------------
        if b["policia"] > 70:
            st.warning("🚨 Desplazamiento del delito a otros barrios")
            for ob in st.session_state.otros_barrios:
                st.session_state.otros_barrios[ob]["delincuencia"] += 5

        # -------------------------
        # EVENTOS
        # -------------------------
        evento = random.choice(["crisis", "conflicto", "ninguno"])

        if evento == "crisis":
            st.warning("💥 Crisis económica")
            b["pobreza"] += 10

        if evento == "conflicto":
            st.warning("⚠️ Conflicto vecinal")
            b["cohesion"] -= 10

        # -------------------------
        # CÁLCULO DEL DELITO
        # -------------------------
        b["delincuencia"] = (
            b["desorganizacion"] * 0.4 +
            b["pobreza"] * 0.3 -
            b["cohesion"] * 0.3 -
            b["control"] * 0.2
        )

        # -------------------------
        # GUARDAR HISTORIAL
        # -------------------------
        st.session_state.historial.append({
            "ronda": st.session_state.ronda,
            "plan": plan,
            "delincuencia": round(b["delincuencia"], 2),
            "tipo": datos["tipo_estrategia"],
            "coherencia": datos["coherencia_teorica"]
        })

        # -------------------------
        # FEEDBACK
        # -------------------------
        st.success(f"📉 Delincuencia: {round(b['delincuencia'],2)}")

        st.write("🧠 Evaluación IA:")
        st.write(datos["evaluacion"])

        st.metric("Coherencia teórica", datos["coherencia_teorica"])

        # -------------------------
        # SIGUIENTE RONDA
        # -------------------------
        st.session_state.ronda += 1

        if st.session_state.ronda > 3:
            st.session_state.fase = "final"

# -----------------------------
# INFORME FINAL
# -----------------------------
if st.session_state.fase == "final":

    st.title("🏁 Informe final")

    b = st.session_state.barrio
    historial = st.session_state.historial

    delincuencia_final = round(b["delincuencia"], 2)
    estrategias = [h["tipo"] for h in historial]

    informe = f"""
    INFORME FINAL - URBANLAB

    Barrio: {b['nombre']}

    Delincuencia final: {delincuencia_final}

    Estrategias utilizadas: {estrategias}

    Historial completo:
    {json.dumps(historial, indent=2, ensure_ascii=False)}
    """

    st.download_button(
        label="📥 Descargar informe",
        data=informe,
        file_name="informe_urbanlab.txt"
    )

    # Evaluación final
    if delincuencia_final < 30:
        st.success("🎉 Estrategia estructural eficaz")
    elif "punitiva" in estrategias:
        st.warning("⚠️ Dependencia excesiva del control formal")
    else:
        st.info("📊 Resultado mixto")

    st.markdown("""
    ## 🧠 Reflexión final

    - ¿Has actuado sobre las causas estructurales?
    - ¿Qué papel ha tenido la cohesión social?
    - ¿Has dependido demasiado de la policía?
    """)
