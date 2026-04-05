import streamlit as st
import random
import json

st.set_page_config(page_title="UrbanLab", layout="centered")

st.title("🏙️ UrbanLab: Política Criminal")

# -----------------------------
# ESTADO
# -----------------------------
if "fase" not in st.session_state:
    st.session_state.fase = "inicio"

if "historial" not in st.session_state:
    st.session_state.historial = []

if "ranking" not in st.session_state:
    st.session_state.ranking = []

# -----------------------------
# INTERPRETADOR
# -----------------------------
def interpretar_plan(plan):

    texto = plan.lower()

    cambios = {
        "policia": 0,
        "cohesion": 0,
        "control": 0,
        "desorganizacion": 0,
        "pobreza": 0
    }

    score = 0
    feedback = []

    if "polic" in texto:
        cambios["policia"] += 10
        cambios["control"] += 5
        score += 1
        feedback.append("Uso de control formal")

    if "comunit" in texto or "vecin" in texto:
        cambios["cohesion"] += 10
        cambios["control"] += 8
        score += 3
        feedback.append("✔ Cohesión social")

    if "urban" in texto or "espacio" in texto:
        cambios["desorganizacion"] -= 10
        score += 3
        feedback.append("✔ Intervención urbana")

    if "empleo" in texto or "educa" in texto:
        cambios["pobreza"] -= 10
        score += 3
        feedback.append("✔ Intervención estructural")

    return cambios, feedback, min(score,10)

# -----------------------------
# RÚBRICA
# -----------------------------
def calcular_nota(delincuencia, score):

    nota = 0

    if delincuencia < 30:
        nota += 5
    elif delincuencia < 50:
        nota += 3

    nota += score

    return min(10, nota)

# -----------------------------
# BARRIOS (COMPLETOS)
# -----------------------------
barrios = {

    "Exclusión severa (tipo 3000 viviendas)": {
        "desorganizacion": 85, "cohesion": 25, "pobreza": 90,
        "desc": "Alta marginalidad, economías informales y ausencia de control institucional."
    },

    "Centro urbano degradado (tipo Raval)": {
        "desorganizacion": 70, "cohesion": 35, "pobreza": 65,
        "desc": "Alta densidad, población flotante y conflictos de convivencia."
    },

    "Barrio en transformación (tipo Cabanyal)": {
        "desorganizacion": 60, "cohesion": 40, "pobreza": 60,
        "desc": "Cambio urbano con tensiones sociales y desplazamiento."
    },

    "Periferia obrera (tipo Vallecas)": {
        "desorganizacion": 55, "cohesion": 50, "pobreza": 55,
        "desc": "Barrio con identidad comunitaria pero desigualdad creciente."
    },

    "Barrio multicultural (tipo Usera)": {
        "desorganizacion": 65, "cohesion": 45, "pobreza": 60,
        "desc": "Diversidad cultural con posibles conflictos de integración."
    },

    "Barrio aislado (tipo Ciutat Meridiana)": {
        "desorganizacion": 75, "cohesion": 35, "pobreza": 75,
        "desc": "Aislamiento territorial y falta de oportunidades."
    },

    "Polígono marginal (tipo La Mina)": {
        "desorganizacion": 80, "cohesion": 30, "pobreza": 85,
        "desc": "Alta criminalidad estructural y desconfianza institucional."
    }
}

# -----------------------------
# INICIO
# -----------------------------
if st.session_state.fase == "inicio":

    st.markdown("### Diseña una política criminal eficaz")

    if st.button("Comenzar"):
        st.session_state.fase = "barrio"

# -----------------------------
# BARRIO
# -----------------------------
if st.session_state.fase == "barrio":

    barrio = st.selectbox("Selecciona barrio", list(barrios.keys()))

    st.write(barrios[barrio]["desc"])

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

    st.subheader(f"Ronda {st.session_state.ronda}/3")
    st.write(b)

    plan = st.text_area("Plan de intervención")

    if st.button("Ejecutar"):

        if len(plan) < 20:
            st.warning("Describe mejor tu intervención")
            st.stop()

        cambios, feedback, score = interpretar_plan(plan)

        # 🔥 SOLUCIÓN KEYERROR
        for k in cambios:
            if k in b:
                b[k] += cambios[k]

        # evento
        evento = random.choice(["crisis", "conflicto", "ninguno"])

        if evento == "crisis":
            b["pobreza"] += 10

        if evento == "conflicto":
            b["cohesion"] -= 10

        # cálculo delito
        b["delincuencia"] = (
            b["desorganizacion"] * 0.4 +
            b["pobreza"] * 0.3 -
            b["cohesion"] * 0.3 -
            b["control"] * 0.2
        )

        st.write("Feedback:", feedback)
        st.metric("Score teórico", score)

        st.session_state.historial.append({
            "resultado": b["delincuencia"],
            "score": score
        })

        st.session_state.ronda += 1

        if st.session_state.ronda > 3:
            st.session_state.fase = "final"

# -----------------------------
# FINAL
# -----------------------------
if st.session_state.fase == "final":

    b = st.session_state.barrio
    score = st.session_state.historial[-1]["score"]

    nota = calcular_nota(b["delincuencia"], score)

    st.title("Resultado final")
    st.metric("Nota", nota)

    informe = json.dumps({
        "barrio": b,
        "historial": st.session_state.historial,
        "nota": nota
    }, indent=2)

    st.download_button("📄 Descargar informe", informe, file_name="informe.json")

    nombre = st.text_input("Nombre del grupo")

    if st.button("Añadir al ranking"):
        st.session_state.ranking.append({
            "grupo": nombre,
            "nota": nota
        })

    st.subheader("🏆 Ranking")

    ranking = sorted(st.session_state.ranking, key=lambda x: x["nota"], reverse=True)

    for r in ranking:
        st.write(f"{r['grupo']} - {r['nota']}")
