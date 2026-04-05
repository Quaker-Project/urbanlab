import streamlit as st
import random

st.set_page_config(page_title="Simulador Criminológico", layout="centered")

st.title("🏙️ Laboratorio de Política Criminal Urbana")

# -------------------------
# INICIO
# -------------------------
if "fase" not in st.session_state:
    st.session_state.fase = "inicio"

if st.session_state.fase == "inicio":
    st.markdown("""
    ## 🎯 Objetivo
    
    Diseñar un plan para reducir la delincuencia en un barrio.
    
    ⚠️ Atención:
    - Las decisiones tienen consecuencias
    - No todo es policía
    - El barrio es un sistema social
    
    👉 Pulsa para comenzar
    """)
    
    if st.button("Comenzar"):
        st.session_state.fase = "barrio"

# -------------------------
# BARRIOS
# -------------------------
if st.session_state.fase == "barrio":
    
    barrios = {
        "A - Alta movilidad": {"desorganizacion": 75, "cohesion": 30, "pobreza": 50},
        "B - Pobreza estructural": {"desorganizacion": 65, "cohesion": 40, "pobreza": 80},
        "C - Diversidad cultural": {"desorganizacion": 60, "cohesion": 35, "pobreza": 60},
        "D - Degradación urbana": {"desorganizacion": 80, "cohesion": 25, "pobreza": 70}
    }
    
    barrio = st.selectbox("Selecciona tu barrio", list(barrios.keys()))
    
    if st.button("Confirmar barrio"):
        base = barrios[barrio]
        
        st.session_state.barrio = {
            "desorganizacion": base["desorganizacion"],
            "cohesion": base["cohesion"],
            "control": 30,
            "pobreza": base["pobreza"],
            "policia": 40,
            "delincuencia": 50
        }
        
        st.session_state.ronda = 1
        st.session_state.fase = "juego"

# -------------------------
# JUEGO
# -------------------------
if st.session_state.fase == "juego":
    
    b = st.session_state.barrio
    
    st.subheader(f"📍 Ronda {st.session_state.ronda}/4")
    
    st.write("Estado actual:", b)
    
    presupuesto = 100
    
    st.subheader("💰 Presupuesto:", presupuesto)
    
    opciones = {
        "Policía intensiva": 30,
        "Programas comunitarios": 25,
        "Rehabilitación urbana": 40,
        "Mediación cultural": 20
    }
    
    seleccion = st.multiselect("Elige intervenciones", opciones.keys())
    
    coste = sum([opciones[o] for o in seleccion])
    
    st.write("Coste:", coste)
    
    if st.button("Ejecutar decisiones"):
        
        if coste > presupuesto:
            st.error("Presupuesto excedido")
        else:
            
            # efectos
            for s in seleccion:
                if s == "Policía intensiva":
                    b["policia"] += 10
                    b["delincuencia"] -= 5
                
                if s == "Programas comunitarios":
                    b["cohesion"] += 10
                    b["control"] += 8
                
                if s == "Rehabilitación urbana":
                    b["desorganizacion"] -= 10
                    b["pobreza"] -= 5
                
                if s == "Mediación cultural":
                    b["cohesion"] += 7
            
            # evento automático
            evento = random.choice([
                "Crisis económica",
                "Aumento de movilidad",
                "Conflicto vecinal",
                "Ninguno"
            ])
            
            st.warning(f"Evento: {evento}")
            
            if evento == "Crisis económica":
                b["pobreza"] += 10
            
            if evento == "Aumento de movilidad":
                b["desorganizacion"] += 10
            
            if evento == "Conflicto vecinal":
                b["cohesion"] -= 10
            
            # cálculo delito
            b["delincuencia"] = (
                b["desorganizacion"] * 0.4 +
                b["pobreza"] * 0.3 -
                b["cohesion"] * 0.3 -
                b["control"] * 0.2
            )
            
            st.success(f"Nivel de delincuencia: {round(b['delincuencia'],2)}")
            
            st.session_state.ronda += 1
            
            if st.session_state.ronda > 4:
                st.session_state.fase = "final"

# -------------------------
# FINAL
# -------------------------
if st.session_state.fase == "final":
    
    b = st.session_state.barrio
    
    st.title("🏁 Resultados finales")
    
    st.write("Delincuencia final:", round(b["delincuencia"],2))
    
    if b["delincuencia"] < 30:
        st.success("🎉 Estrategia estructural eficaz")
    elif b["policia"] > 80:
        st.warning("⚠️ Estrategia basada en control formal")
    else:
        st.info("📊 Resultados mixtos")
    
    st.markdown("""
    ## 🧠 Reflexión
    
    - ¿Has mejorado la cohesión social?
    - ¿Dependiste demasiado de la policía?
    - ¿Atacaste causas estructurales?
    """)
