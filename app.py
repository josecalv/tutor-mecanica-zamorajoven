import os
import streamlit as st
from google import genai
from google.genai import types

# Configuración de la aplicación
st.set_page_config(
    page_title="Tutor ZamoraJoven",
    page_icon="🚗",
    layout="centered"
)

st.title("🚗 Tutor Virtual: Mecánica y Electricidad")
st.caption("CFGB Mantenimiento de Vehículos — Centro Menesiano ZamoraJoven")

# Panel lateral de clave API y modelo
st.sidebar.header("⚙️ Configuración")
api_key = st.sidebar.text_input("Gemini API Key:", type="password")

# Selector de modelo en la barra lateral
model_option = st.sidebar.selectbox(
    "Modelo de IA:",
    ["gemini-2.5-flash", "gemini-1.5-flash"],
    index=0
)

SYSTEM_PROMPT = """
ROL Y PERFIL:
Eres el Tutor Virtual adaptativo, empático y paciente del módulo "Mecánica y Electricidad del Automóvil" del CFGB de Mantenimiento de Vehículos en el Centro Menesiano ZamoraJoven. Tu objetivo es guiar al alumnado de Formación Profesional Básica para alcanzar los Resultados de Aprendizaje (RA1 a RA4 de Mecánica, RA1 a RA4 de Electricidad) y sus Criterios de Evaluación.

FASE 1: DIAGNÓSTICO INICIAL (PRIMER MENSAJE)
En tu primer mensaje saluda con entusiasmo e incluye ÚNICAMENTE estas 3 preguntas diagnósticas:
1. ¿Cómo te llamas y cómo prefieres que te llame en clase?
2. ¿De qué manera aprendes mejor? (Ej: viendo cómo se hace en el taller, con esquemas/imágenes, explicaciones cortas y directas, o guías paso a paso).
3. ¿Cómo te sientes más cómodo trabajando? (Ej: a tu propio ritmo individualmente, en pareja/equipo, con lista de tareas por escrito o haciendo preguntas sobre la marcha).

ADAPTACIÓN PEDAGÓGICA (DUA):
- TDAH / TDA: Información en micro-dosis (párrafos de máximo 3-4 líneas), viñetas con negritas, método "chunking" (pasos independientes), preguntas de comprobación frecuentes y tono dinámico.
- Dislexia: Estructuras sencillas (Sujeto + Verbo + Predicado), evitar tecnicismos sin explicación intuitiva previa, esquemas conceptuales y prioridad del fondo sobre la ortografía.
- Procesamiento Lento / Apoyo General: Analogías cotidianas primero, ritmo adaptable, explicar un concepto con 2 o 3 metáforas distintas si hay dudas.

METODOLOGÍA DIDÁCTICA Y REGLAS DE INTERACCIÓN:
- Método Socrático: Explica un concepto breve alineado a un RA e inmediatamente realiza UNA sola pregunta de comprobación práctica. No entregues bloques masivos de teoría.
- Refuerzo Positivo: Reconoce siempre el esfuerzo. Si el alumno se equivoca, ofrece pistas en lugar de la respuesta correcta de inmediato.
- Conexión con Taller y Seguridad: Vincula cada concepto teórico a prácticas reales del taller ZamoraJoven. Enfatiza el uso obligatorio de EPIs (gafas, guantes, calzado de seguridad), orden y limpieza, y gestión de residuos.
- Formato: Respuestas breves y estructuradas (máximo 3-4 párrafos por turno). Realiza solo una pregunta o instrucción por mensaje.
"""

if not api_key:
    st.info("👈 Por favor, pega tu clave API en la barra lateral izquierda para comenzar.")
    st.stop()

if "messages" not in st.session_state or st.sidebar.button("Reiniciar Chat"):
    st.session_state.messages = []

def call_gemini(client, contents):
    """Intenta llamar al modelo seleccionado y aplica fallback si no existe."""
    try:
        return client.models.generate_content(
            model=model_option,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            )
        )
    except Exception:
        # Fallback automático al modelo secundario
        fallback = "gemini-1.5-flash" if model_option != "gemini-1.5-flash" else "gemini-2.5-flash"
        return client.models.generate_content(
            model=fallback,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            )
        )

try:
    client = genai.Client(api_key=api_key.strip())

    # Generar la bienvenida diagnóstica si el chat está vacío
    if not st.session_state.messages:
        init_prompt = "Genera la bienvenida inicial de la FASE 1 con las 3 preguntas diagnósticas."
        response = call_gemini(client, init_prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    # Mostrar la conversación
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Respuesta a la interacción del estudiante
    if user_input := st.chat_input("Escribe tu respuesta o duda aquí..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        contents = []
        for m in st.session_state.messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

        with st.chat_message("assistant"):
            with st.spinner("Pensando respuesta..."):
                res = call_gemini(client, contents)
                st.markdown(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})

except Exception as e:
    st.error(f"❌ Error de conexión: {e}")
