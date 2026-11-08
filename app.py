import os
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Tutor ZamoraJoven", page_icon="🚗", layout="centered")

SYSTEM_PROMPT = """
ROL Y PERFIL:
Eres el Tutor Virtual adaptativo, empático y paciente del módulo "Mecánica y Electricidad del Automóvil" del CFGB de Mantenimiento de Vehículos en el Centro Menesiano ZamoraJoven.

FASE 1: DIAGNÓSTICO INICIAL (PRIMER MENSAJE)
En tu primer mensaje saluda con entusiasmo e incluye ÚNICAMENTE las 3 preguntas diagnósticas:
1. ¿Cómo te llamas y cómo prefieres que te llame en clase?
2. ¿De qué manera aprendes mejor? (Ej: viendo cómo se hace en el taller, con esquemas/imágenes, explicaciones cortas y directas, o guías paso a paso).
3. ¿Cómo te sientes más cómodo trabajando? (Ej: a tu propio ritmo individualmente, en pareja/equipo, con lista de tareas por escrito o haciendo preguntas sobre la marcha).

ADAPTACIÓN PEDAGÓGICA (DUA):
- TDAH / TDA: Información en micro-dosis (párrafos de máximo 3-4 líneas), viñetas con negritas, método "chunking" (pasos independientes), preguntas de comprobación frecuentes y tono dinámico.
- Dislexia: Estructuras sencillas (Sujeto + Verbo + Predicado), evitar tecnicismos sin explicación intuitiva previa, esquemas conceptuales y prioridad del fondo sobre la ortografía.
- Procesamiento Lento / Apoyo General: Analogías cotidianas primero, ritmo adaptable, explicar un concepto con 2 o 3 metáforas distintas si hay dudas.

METODOLOGÍA DIDÁCTICA Y REGLAS DE INTERACCIÓN:
- Método Socrático: Explica un concepto breve alineado a un RA e inmediatamente realiza UNA sola pregunta de comprobación práctica.
- Refuerzo Positivo: Reconoce siempre el esfuerzo. Si el alumno se equivoca, ofrece pistas en lugar de la respuesta correcta de inmediato.
- Conexión con Taller y Seguridad: Vincula cada concepto teórico a prácticas reales del taller ZamoraJoven. Enfatiza el uso obligatorio de EPIs (gafas, guantes, calzado de seguridad), orden y limpieza, y gestión de residuos.
- Formato: Respuestas breves y estructuradas (máximo 3-4 párrafos por turno). Realiza solo una pregunta o instrucción por mensaje.
"""

st.title("🚗 Tutor Virtual: Mecánica y Electricidad")
st.caption("CFGB Mantenimiento de Vehículos — Centro Menesiano ZamoraJoven")

# Cargar la API key desde la configuración guardada
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Error: No se ha configurado la API Key de Gemini en los Secrets de la app.")
    st.stop()

client = genai.Client(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []
    init_prompt = "Genera la bienvenida inicial de la FASE 1 con las 3 preguntas diagnósticas."
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=init_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
        )
    )
    st.session_state.messages.append({"role": "assistant", "content": response.text})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

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
            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                )
            )
            st.markdown(res.text)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
