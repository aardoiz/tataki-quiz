import streamlit as st
import json
import random
import os

# Función para cargar preguntas desde un archivo JSON
def cargar_preguntas(archivo):
    try:
        with open(archivo, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"El archivo {archivo} no se encontró.")
        return []

# Obtener lista de archivos JSON disponibles en la carpeta actual
datasets = [f for f in os.listdir() if f.endswith('.json')]

# Sidebar para seleccionar el conjunto de preguntas
dataset_seleccionado = st.sidebar.selectbox("Selecciona un conjunto de preguntas:", datasets)

# Cargar las preguntas del dataset seleccionado
preguntas = cargar_preguntas(dataset_seleccionado)

# Barajar preguntas al inicio
def iniciar_quiz():
    if preguntas:
        random.shuffle(preguntas)
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.show_feedback = False
    st.session_state.selected_answer = None
    st.session_state.current_options = None
    st.session_state.current_options_question = None

if 'quiz_started' not in st.session_state:
    iniciar_quiz()
    st.session_state.quiz_started = True

if st.sidebar.button("Reiniciar Quiz"):
    iniciar_quiz()
    st.rerun()

# Inicializar variables de estado de la sesión
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'show_feedback' not in st.session_state:
    st.session_state.show_feedback = False
if 'selected_answer' not in st.session_state:
    st.session_state.selected_answer = None
if 'current_options' not in st.session_state:
    st.session_state.current_options = None
if 'current_options_question' not in st.session_state:
    st.session_state.current_options_question = None

def mostrar_pregunta():
    """Mostrar la pregunta actual con opciones de respuesta aleatorizadas."""
    question_data = preguntas[st.session_state.current_question]
    st.subheader(f"Pregunta {st.session_state.current_question + 1}")
    st.write(question_data['pregunta'])

    option_keys = [key for key in question_data.keys() if key.isalpha() and len(key) == 1]
    option_keys = sorted(option_keys)
    
    if (st.session_state.current_options is None or 
        st.session_state.current_options_question != st.session_state.current_question):
        options = [(key, question_data[key]) for key in option_keys]
        random.shuffle(options)
        st.session_state.current_options = options
        st.session_state.current_options_question = st.session_state.current_question
    else:
        options = st.session_state.current_options

    selected = st.radio("Selecciona tu respuesta:", options, format_func=lambda opt: f"{opt[1]}")
    
    if st.button("Enviar respuesta"):
        st.session_state.selected_answer = selected
        if selected[0].lower() == question_data['respuesta'].lower():
            st.session_state.score += 1
        st.session_state.show_feedback = True
        st.rerun()

def mostrar_feedback():
    """Mostrar retroalimentación después de enviar la respuesta."""
    question_data = preguntas[st.session_state.current_question]
    correct_key = question_data['respuesta'].lower()
    selected_key = st.session_state.selected_answer[0].lower()
    
    st.markdown("---")
    if selected_key == correct_key:
        st.success("¡Respuesta Correcta! ✅")
    else:
        correct_text = question_data.get(correct_key, "Opción correcta no disponible.")
        options = st.session_state.current_options
        formatted_options = ""
        for key, text in options:
            if key.lower() == correct_key:
                formatted_options += f"**Respuesta correcta: {text}**\n\n"
            else:
                formatted_options += f"{text}\n\n"
        error_message = f"**Respuesta Incorrecta ❌**\n\n_{question_data['pregunta']}_\n\n---\n\n{formatted_options}"
        st.error(error_message)
    
    if st.session_state.current_question == len(preguntas) - 1:
        if st.button("Finalizar examen"):
            st.session_state.current_question += 1
            st.rerun()
    else:
        if st.button("Siguiente pregunta"):
            st.session_state.current_question += 1
            st.session_state.show_feedback = False
            st.session_state.selected_answer = None
            st.session_state.current_options = None
            st.session_state.current_options_question = None
            st.rerun()

def main():
    st.title("Tataki Examinator 3000")
    progreso = st.session_state.current_question / len(preguntas) if preguntas else 0
    st.progress(progreso)
    st.write(f"Pregunta {min(st.session_state.current_question + 1, len(preguntas))} de {len(preguntas)}")
    st.write(f"Puntuación actual: {st.session_state.score} correctas")
    
    if preguntas:
        if st.session_state.current_question < len(preguntas):
            if not st.session_state.show_feedback:
                mostrar_pregunta()
            else:
                mostrar_feedback()
        else:
            st.balloons()
            st.success(f"¡Examen completado! Puntuación final: {st.session_state.score}/{len(preguntas)}")
            if st.button("Volver a empezar"):
                iniciar_quiz()
                st.rerun()
    else:
        st.warning("No hay preguntas disponibles en el conjunto seleccionado.")

if __name__ == "__main__":
    main()
