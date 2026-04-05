import streamlit as st
import random
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

st.set_page_config(page_title="UrbanLab PRO", layout="centered")

st.title("🏙️ UrbanLab PRO: Simulación de Política Criminal")

# -----------------------------
# ESTADO
# -----------------------------
if "fase" not in st.session_state:
    st.session_state.fase = "inicio"

if "historial" not in st.session_state:
    st.session_state.historial = []

if "informes" not in st.session_state:
    st.session_state.informes = []

# -----------------------------
# INTERPRETADOR
# -----------------------------
def interpretar_plan(plan):

    texto = plan.lower()

    cambios = {"policia":0,"cohesion":0,"control":0,"desorganizacion":0,"pobreza":0}
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

    if "urban" in texto:
        cambios["desorganizacion"] -= 10
        score += 3
        feedback.append("✔ Mejora urbana")

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
# PDF
# -----------------------------
def generar_pdf(texto):
    tmp = tempfile.NamedTemporaryFile(delete=False)
    doc = SimpleDocTemplate(tmp.name)
    styles = getSampleStyleSheet()
    content = [Paragraph(texto, styles["Normal"])]
    doc.build(content)
    return tmp.name

# -----------------------------
# BARRIOS
# -----------------------------
barrios = {
    "Exclusión severa": {"desorganizacion":85,"cohesion":25,"pobreza":90},
    "Centro degradado": {"desorganizacion":70,"cohesion":35,"pobreza":65},
    "Barrio en cambio": {"desorganizacion":60,"cohesion":40,"pobreza":60}
}

# -----------------------------
# INICIO
# -----------------------------
if st.session_state.fase == "inicio":
    st.markdown("### Diseña una política criminal basada en la teoría")

    if st.button("Comenzar"):
        st.session_state.fase = "barrio"

# -----------------------------
# BARRIO
# -----------------------------
if st.session_state.fase == "barrio":

    barrio = st.selectbox("Selecciona barrio", list(barrios.keys()))

    if st.button("Confirmar"):
        base = barrios[barrio]

        st.session_state.barrio = {
            "nombre": barrio,
            "desorganizacion": base["desorganizacion"],
            "cohesion": base["cohesion"],
            "control":30,
            "pobreza": base["pobreza"],
            "delincuencia":60
        }

        st.session_state.ronda = 1
        st.session_state.fase = "juego"

# -----------------------------
# JUEGO (3 RONDAS)
# -----------------------------
if st.session_state.fase == "juego":

    b = st.session_state.barrio

    st.subheader(f"Ronda {st.session_state.ronda}/3")
    st.write(b)

    plan = st.text_area("Plan de intervención")

    if st.button("Ejecutar"):

        if len(plan) < 20:
            st.warning("Escribe un plan más desarrollado")
            st.stop()

        cambios, feedback, score = interpretar_plan(plan)

        for k in cambios:
            b[k] += cambios[k]

        # evento
        evento = random.choice(["crisis", "conflicto", "ninguno"])

        if evento == "crisis":
            b["pobreza"] += 10

        if evento == "conflicto":
            b["cohesion"] -= 10

        b["delincuencia"] = (
            b["desorganizacion"]*0.4 +
            b["pobreza"]*0.3 -
            b["cohesion"]*0.3 -
            b["control"]*0.2
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

    informe = f"""
    Barrio: {b['nombre']}
    Delincuencia final: {round(b['delincuencia'],2)}
    Nota: {nota}
    """

    pdf = generar_pdf(informe)

    with open(pdf, "rb") as f:
        st.download_button("📄 Descargar PDF", f, file_name="informe.pdf")

    nombre = st.text_input("Nombre del grupo")

    if st.button("Subir informe"):
        st.session_state.informes.append({
            "grupo": nombre,
            "nota": nota
        })

    st.subheader("🏆 Ranking")

    ranking = sorted(st.session_state.informes, key=lambda x: x["nota"], reverse=True)

    for r in ranking:
        st.write(f"{r['grupo']} - Nota: {r['nota']}")
