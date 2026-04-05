import streamlit as st
import random
import json

st.set_page_config(page_title="UrbanLab Criminología", layout="centered")

st.title("🏙️ UrbanLab: Simulación de Política Criminal")

# -----------------------------
# ESTADO GLOBAL
# -----------------------------
if "fase" not in st.session_state:
    st.session_state.fase = "inicio"

if "historial" not in st.session_state:
    st.session_state.historial = []

if "informes_subidos" not in st.session_state:
    st.session_state.informes_subidos = []

# -----------------------------
# INTERPRETADOR (SIN IA)
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

    evaluacion = []
    puntuacion = 0

    if "polic" in texto:
        cambios["policia"] += 10
        cambios["control"] += 5
        evaluacion.append("Uso de control formal (efecto limitado)")
        puntuacion += 1

    if "comunit" in texto or "vecin" in texto:
        cambios["cohesion"] += 10
        cambios["control"] += 8
        evaluacion.append("✔ Refuerza cohesión social")
        puntuacion += 3

    if "urban" in texto or "espacio" in texto:
        cambios["desorganizacion"] -= 10
        evaluacion.append("✔ Mejora entorno urbano")
        puntuacion += 3

    if "empleo" in texto or "educa" in texto:
        cambios["pobreza"] -= 10
        evaluacion.append("✔ Actúa sobre causas estructurales")
        puntuacion += 3

    if "mediacion" in texto:
        cambios["cohesion"] += 8
        evaluacion.append("✔ Mejora relaciones sociales")
        puntuacion += 2

    if cambios["policia"] > 0 and puntuacion <= 1:
        evaluacion.append("⚠️ Estrategia excesivamente punitiva")
        puntuacion -= 2

    return cambios, evaluacion, max(0, min(10, puntuacion))

# -----------------------------
# BARRIOS
# -----------------------------
barrios = {
    "Periferia de exclusión severa": {
        "datos": {"desorganizacion": 85, "cohesion": 25, "pobreza": 90},
        "descripcion": "Zona con alta marginalidad, economías informales y débil control social."
    },
    "Centro urbano degradado": {
        "datos": {"desorganizacion": 70, "cohesion": 35, "pobreza": 65},
        "descripcion": "Barrio céntrico con alta rotación y conflictos de convivencia."
    },
    "Barrio en transformación": {
        "datos": {"desorganizacion": 60, "cohesion": 40, "pobreza": 60},
        "descripcion": "Barrio en cambio con tensiones sociales y urbanas."
    }
}

# -----------------------------
# INICIO
# -----------------------------
if st.session_state.fase == "inicio":
    st.markdown("### Diseña una política criminal basada en la teoría de la desorganización social")
    
    if st.button("Comenzar"):
        st.session_state.fase = "barrio"

# -----------------------------
# SELECCIÓN DE BARRIO
# -----------------------------
if st.session_state.fase == "barrio":

    barrio = st.selectbox("Selecciona tu barrio", list(barrios.keys()))
    
    st.write(barrios[barrio]["descripcion"])

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
    st.write("Estado:", b)

    diagnostico = st.text_area("🔍 Diagnóstico del barrio")
    plan = st.text_area("🧠 Plan de intervención")

    if st.button("Ejecutar plan"):

        if not diagnostico or not plan:
            st.warning("Completa diagnóstico y plan")
            st.stop()

        cambios, evaluacion, score = interpretar_plan(plan)

        for k in cambios:
            b[k] += cambios[k]

        b["delincuencia"] = (
            b["desorganizacion"] * 0.4 +
            b["pobreza"] * 0.3 -
            b["cohesion"] * 0.3 -
            b["control"] * 0.2
        )

        st.success(f"📉 Delincuencia: {round(b['delincuencia'],2)}")

        st.write("Evaluación:")
        for e in evaluacion:
            st.write("-", e)

        st.metric("Puntuación teórica", score)

        st.session_state.historial.append({
            "plan": plan,
            "resultado": b["delincuencia"]
        })

        st.session_state.ronda += 1

        if st.session_state.ronda > 3:
            st.session_state.fase = "final"

# -----------------------------
# FINAL + INFORMES
# -----------------------------
if st.session_state.fase == "final":

    st.title("🏁 Informe final")

    informe = f"""
    Barrio: {st.session_state.barrio['nombre']}
    Delincuencia final: {round(st.session_state.barrio['delincuencia'],2)}

    Historial:
    {json.dumps(st.session_state.historial, indent=2)}
    """

    st.download_button("📥 Descargar tu informe", informe)

    # -------------------------
    # SUBIR INFORMES
    # -------------------------
    st.subheader("📤 Subir informe para evaluación")

    nombre_grupo = st.text_input("Nombre del grupo")

    if st.button("Subir informe"):
        if nombre_grupo:
            st.session_state.informes_subidos.append({
                "grupo": nombre_grupo,
                "contenido": informe
            })
            st.success("Informe subido correctamente")

    # -------------------------
    # VER Y DESCARGAR INFORMES
    # -------------------------
    st.subheader("📥 Informes de otros grupos")

    for i, inf in enumerate(st.session_state.informes_subidos):
        st.write(f"Grupo: {inf['grupo']}")
        st.download_button(
            label=f"Descargar informe {inf['grupo']}",
            data=inf["contenido"],
            file_name=f"informe_{inf['grupo']}.txt",
            key=i
        )
