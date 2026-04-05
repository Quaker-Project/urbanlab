import streamlit as st
import random
import json
import os
from openai import OpenAI

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="UrbanLab Criminología", layout="centered")

api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("Falta configurar OPENAI_API_KEY")
    st.stop()

client = OpenAI(api_key=api_key)

st.title("🏙️ UrbanLab: Simulación de Política Criminal")

# -----------------------------
# ESTADO
# -----------------------------
if "fase" not in st.session_state:
    st.session_state.fase = "inicio"

if "historial" not in st.session_state:
    st.session_state.historial = []

if "otros_barrios" not in st.session_state:
    st.session_state.otros_barrios = {
        "Zona colindante": {"delincuencia": 60}
    }

# -----------------------------
# IA
# -----------------------------
def interpretar_plan_ia(plan):
    prompt = f"""
    Eres experto en criminología urbana (teoría de la desorganización social).

    Analiza este plan:
    "{plan}"

    Devuelve SOLO JSON con:
    policia (-10 a 10)
    cohesion (-10 a 10)
    control_informal (-10 a 10)
    desorganizacion (-10 a 10)
    pobreza (-10 a 10)
    tipo_estrategia (punitiva, estructural, mixta)
    coherencia_teorica (0-10)
    evaluacion (feedback en español)
    """

    r = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    try:
        return json.loads(r.choices[0].message.content)
    except:
        return None

# -----------------------------
# BARRIOS REALISTAS
# -----------------------------
barrios = {

    "Periferia de exclusión severa": {
        "datos": {"desorganizacion": 85, "cohesion": 25, "pobreza": 90},
        "descripcion": """
        🏙️ Gran conjunto de vivienda social construido en la periferia, con fuerte concentración de exclusión.

        👥 Población:
        - Alta tasa de desempleo estructural
        - Economías informales
        - Familias con múltiples vulnerabilidades

        🏚️ Entorno:
        - Edificios deteriorados
        - Espacios públicos degradados
        - Escasa presencia institucional efectiva

        ⚠️ Problemas:
        - Alta criminalidad visible
        - Mercados ilegales consolidados
        - Desconfianza hacia instituciones

        🗣️ Testimonios:
        “Aquí la policía entra pero no cambia nada”
        “Los chavales crecen viendo lo mismo”
        """
    },

    "Centro urbano degradado": {
        "datos": {"desorganizacion": 70, "cohesion": 35, "pobreza": 65},
        "descripcion": """
        🏙️ Barrio céntrico con alta densidad, mezcla social y fuerte presión urbana.

        👥 Población:
        - Diversidad cultural
        - Población flotante
        - Turismo y economía informal

        🏚️ Entorno:
        - Vivienda antigua
        - Alta rotación residencial

        ⚠️ Problemas:
        - Delincuencia oportunista
        - Conflictos de convivencia
        - Saturación del espacio público

        🗣️ Testimonios:
        “Esto ya no es un barrio, es un lugar de paso”
        """
    },

    "Barrio en transformación urbana": {
        "datos": {"desorganizacion": 60, "cohesion": 40, "pobreza": 60},
        "descripcion": """
        🏙️ Barrio histórico en proceso de renovación urbana.

        👥 Población:
        - Vecinos tradicionales + nuevos residentes
        - Tensiones por gentrificación

        🏚️ Entorno:
        - Mejora de infraestructuras
        - Cambios en usos del espacio

        ⚠️ Problemas:
        - Conflictos sociales
        - Desplazamiento poblacional

        🗣️ Testimonios:
        “El barrio está cambiando demasiado rápido”
        """
    },

    "Periferia obrera consolidada": {
        "datos": {"desorganizacion": 55, "cohesion": 50, "pobreza": 55},
        "descripcion": """
        🏙️ Barrio de tradición obrera con identidad comunitaria.

        👥 Población:
        - Redes vecinales fuertes
        - Historia de organización social

        🏚️ Entorno:
        - Equipamientos básicos
        - Espacios públicos activos

        ⚠️ Problemas:
        - Delincuencia juvenil
        - Desigualdad creciente

        🗣️ Testimonios:
        “Aquí nos conocemos todos, pero las cosas están cambiando”
        """
    },

    "Barrio aislado geográficamente": {
        "datos": {"desorganizacion": 75, "cohesion": 35, "pobreza": 75},
        "descripcion": """
        🏙️ Barrio periférico con aislamiento físico y malas conexiones.

        👥 Población:
        - Alta vulnerabilidad social
        - Limitada movilidad

        🏚️ Entorno:
        - Barreras geográficas
        - Transporte deficiente

        ⚠️ Problemas:
        - Exclusión territorial
        - Falta de oportunidades

        🗣️ Testimonios:
        “Estamos fuera de todo”
        """
    }
}

# -----------------------------
# INICIO
# -----------------------------
if st.session_state.fase == "inicio":
    st.markdown("""
    ## 🎯 Misión

    Diseñar una política criminal basada en la teoría de la desorganización social.

    👉 Reduce la delincuencia sin romper la cohesión social
    """)

    if st.button("Comenzar"):
        st.session_state.fase = "barrio"

# -----------------------------
# BARRIO
# -----------------------------
if st.session_state.fase == "barrio":

    barrio = st.selectbox("Selecciona tu barrio", list(barrios.keys()))

    if barrio:
        st.subheader("📍 Contexto del barrio")
        st.markdown(barrios[barrio]["descripcion"])

    if st.button("Confirmar"):
        base = barrios[barrio]["datos"]

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

    st.write("📊 Estado del barrio:", b)

    diagnostico = st.text_area("🔍 Diagnóstico del problema")

    plan = st.text_area("🧠 Diseña tu intervención")

    if st.button("Ejecutar plan"):

        if not diagnostico or not plan:
            st.warning("Completa diagnóstico y plan")
            st.stop()

        datos = interpretar_plan_ia(plan)

        if datos is None:
            st.error("Error interpretando el plan")
            st.stop()

        # aplicar efectos
        b["policia"] += datos["policia"]
        b["cohesion"] += datos["cohesion"]
        b["control"] += datos["control_informal"]
        b["desorganizacion"] += datos["desorganizacion"]
        b["pobreza"] += datos["pobreza"]

        # interacción barrios
        if b["policia"] > 70:
            st.warning("🚨 Desplazamiento del delito")
            for ob in st.session_state.otros_barrios:
                st.session_state.otros_barrios[ob]["delincuencia"] += 5

        # evento
        evento = random.choice(["crisis", "conflicto", "ninguno"])

        if evento == "crisis":
            st.warning("💥 Crisis económica")
            b["pobreza"] += 10

        if evento == "conflicto":
            st.warning("⚠️ Conflicto vecinal")
            b["cohesion"] -= 10

        # delito
        b["delincuencia"] = (
            b["desorganizacion"] * 0.4 +
            b["pobreza"] * 0.3 -
            b["cohesion"] * 0.3 -
            b["control"] * 0.2
        )

        st.success(f"📉 Delincuencia: {round(b['delincuencia'],2)}")
        st.write(datos["evaluacion"])
        st.metric("Coherencia teórica", datos["coherencia_teorica"])

        st.session_state.historial.append({
            "plan": plan,
            "resultado": b["delincuencia"]
        })

        st.session_state.ronda += 1

        if st.session_state.ronda > 3:
            st.session_state.fase = "final"

# -----------------------------
# FINAL
# -----------------------------
if st.session_state.fase == "final":

    st.title("🏁 Informe final")

    informe = f"""
    Barrio: {st.session_state.barrio['nombre']}
    Delincuencia final: {round(st.session_state.barrio['delincuencia'],2)}
    Historial: {st.session_state.historial}
    """

    st.download_button("📥 Descargar informe", informe)

    st.success("Simulación completada")
