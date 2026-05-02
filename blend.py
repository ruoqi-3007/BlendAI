import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import os

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="BlendAI",
    layout="wide",
    page_icon="🎮"
)

ICONO_IA = "https://upload.wikimedia.org/wikipedia/commons/0/0c/Blender_logo_no_text.svg"
ICONO_USUARIO = "👨‍🎨"

# =========================================================
# CSS (AUTO LIGHT/DARK MODE)
# =========================================================
st.markdown("""
<style>

.stButton>button {
    border-radius: 12px;
    border: 1px solid rgba(120,120,120,0.3);
    transition: 0.3s;
    font-weight: 600;
}

.stButton>button:hover {
    border: 1px solid #00C8FF;
    transform: scale(1.02);
}

.block {
    padding: 14px;
    border-radius: 14px;
    margin-bottom: 10px;
    border: 1px solid rgba(120,120,120,0.2);
    backdrop-filter: blur(6px);
}

[data-testid="stSidebar"] {
    border-right: 1px solid rgba(120,120,120,0.15);
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# API
# =========================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ No se encontró la API KEY de Groq")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# =========================================================
# SESSION STATE
# =========================================================
DEFAULT_STATE = {
    "xp": 0,
    "level": 1,
    "mission": None,
    "mission_step": 0,
    "messages": [],
    "unlocked": ["Cubo"]
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# MISSIONS
# =========================================================
MISSIONS = {

    "Cubo": [
        "Abrir Blender",
        "Crear cubo",
        "Mover y escalar",
        "Material básico"
    ],

    "Donut": [
        "Crear torus",
        "Subdivision Surface",
        "Glaseado",
        "Render final"
    ],

    "Coche": [
        "Bloqueo base",
        "Ruedas",
        "Low poly",
        "Materiales"
    ],

    "Playa": [
        "Terreno",
        "Arena",
        "Agua",
        "Palmeras"
    ],

    "Habitación": [
        "Paredes",
        "Muebles",
        "Iluminación interior",
        "Render"
    ],

    "Espada": [
        "Hoja",
        "Mango",
        "Metal",
        "Render épico"
    ],

    "Animación": [
        "Keyframes",
        "Timeline",
        "Movimiento cámara",
        "Render animación"
    ],

    "Sculpt": [
        "Entrar en Sculpt Mode",
        "Clay Strips",
        "Smooth Brush",
        "Detalles faciales"
    ],

    "Materiales PBR": [
        "Shader Editor",
        "Texturas PBR",
        "Roughness",
        "Normal Maps"
    ],

    "Iluminación": [
        "HDRI",
        "Three Point Lighting",
        "Area Lights",
        "Cinematic Look"
    ]
}

# =========================================================
# UNLOCKS
# =========================================================
UNLOCKS = {
    "Cubo": "Donut",
    "Donut": "Coche",
    "Coche": "Playa",
    "Playa": "Habitación",
    "Habitación": "Espada",
    "Espada": "Animación",
    "Animación": "Sculpt",
    "Sculpt": "Materiales PBR",
    "Materiales PBR": "Iluminación"
}

# =========================================================
# DAILY CHALLENGES
# =========================================================
DAILY_CHALLENGES = [
    "Modela un objeto usando solo cubos",
    "Crea una escena low-poly",
    "Haz un material metálico",
    "Ilumina una habitación",
    "Haz una animación simple"
]

# =========================================================
# RANKS
# =========================================================
def get_rank(level):

    if level < 3:
        return "🟢 Beginner"
    elif level < 6:
        return "🔵 Apprentice"
    elif level < 10:
        return "🟣 Artist"
    elif level < 15:
        return "🟠 Technical Artist"
    else:
        return "🔴 Blender Master"

# =========================================================
# XP SYSTEM
# =========================================================
def check_level_up(old_level):

    if st.session_state.level > old_level:
        st.balloons()
        st.success(
            f"🎉 LEVEL UP! Ahora eres nivel {st.session_state.level}"
        )


def add_xp(amount):

    old_level = st.session_state.level

    st.session_state.xp += amount

    st.session_state.level = 1 + st.session_state.xp // 50

    check_level_up(old_level)


def show_xp_feedback(xp_gain):
    st.toast(f"⭐ +{xp_gain} XP", icon="🎮")

# =========================================================
# BLENDER DOCS
# =========================================================
def get_blender_latest_info(query):

    try:
        with DDGS() as ddgs:

            results = ddgs.text(
                f"Blender 4.2 {query} site:docs.blender.org",
                max_results=2
            )

            return "\n".join(
                r.get("body", "")
                for r in results
                if r.get("body")
            )[:1000]

    except:
        return ""

# =========================================================
# AI
# =========================================================
def ask_ai(prompt):

    contexto = get_blender_latest_info(prompt)

    system = f"""
Eres BlendAI, un Consultor Senior en Gráficos 3D y tutor experto en Blender 4.2+.

ESTILO DE RESPUESTA:
- Profesional, técnico y conciso.
- Usa Markdown estrictamente.
- Herramientas en **negrita**.
- Atajos en `código`.
- Indica siempre el modo Blender necesario.
- Ajusta dificultad según Nivel {st.session_state.level}.
- Da feedback como entrenador profesional tipo RPG educativo.

FORMATO:
1. Objetivo
2. Acción técnica
3. Shortcut
4. Consejo profesional

MISIÓN ACTUAL:
{st.session_state.mission}

PASO ACTUAL:
{st.session_state.mission_step}
"""

    messages = [
        {
            "role": "system",
            "content": system
        }
    ]

    if contexto:
        messages.append({
            "role": "assistant",
            "content": f"📚 Referencia técnica Blender:\n{contexto}"
        })

    messages.append({
        "role": "user",
        "content": prompt
    })

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.6,
            max_tokens=700
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Error: {str(e)}"

# =========================================================
# MISSIONS
# =========================================================
def start_mission(name):

    st.session_state.mission = name
    st.session_state.mission_step = 0

    return ask_ai(
        f"Iniciamos la misión {name}. Dame el PASO 1 detallado."
    )


def complete_step():

    mission = st.session_state.mission

    st.session_state.mission_step += 1

    xp_gain = 10

    add_xp(xp_gain)
    show_xp_feedback(xp_gain)

    if st.session_state.mission_step >= len(MISSIONS[mission]):

        add_xp(50)

        if mission in UNLOCKS:

            next_mission = UNLOCKS[mission]

            if next_mission not in st.session_state.unlocked:
                st.session_state.unlocked.append(next_mission)

        st.session_state.mission = None

        return "🎉 ¡Misión completada! Has desbloqueado nuevo contenido."

    return ask_ai(
        "He completado el paso anterior. Dame el siguiente paso."
    )

# =========================================================
# HEADER
# =========================================================
st.title("🚀 BlendAI")
st.caption("Aprende Blender como un videojuego profesional 🎮")

# =========================================================
# LAYOUT
# =========================================================
col1, col2 = st.columns([2.3, 1])

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.title("🎮 BlendAI")

    st.subheader("📊 Perfil")

    st.write(f"⭐ XP: {st.session_state.xp}")
    st.write(f"🏅 Nivel: {st.session_state.level}")

    st.write(
        f"🏆 Rango: {get_rank(st.session_state.level)}"
    )

    current_xp = st.session_state.xp % 50
    progress = current_xp / 50

    st.progress(progress)

    st.caption(
        f"{current_xp}/50 XP para siguiente nivel"
    )

    st.divider()

    st.subheader("🔥 Reto diario")

    challenge = DAILY_CHALLENGES[
        st.session_state.level % len(DAILY_CHALLENGES)
    ]

    st.info(challenge)

    st.divider()

    st.subheader("🗺️ Misiones")

    for mission in st.session_state.unlocked:

        if st.button(
            f"🎯 {mission}",
            use_container_width=True
        ):

            msg = start_mission(mission)

            st.session_state.messages.append({
                "role": "assistant",
                "content": msg
            })

            st.rerun()

    st.divider()

    st.subheader("⚙️ Sistema")

    if st.button(
        "🔄 Reiniciar BlendAI",
        use_container_width=True
    ):

        for key, value in DEFAULT_STATE.items():
            st.session_state[key] = value

        st.rerun()

# =========================================================
# MAIN CHAT
# =========================================================
with col1:

    st.subheader("🎓 Tutor IA")

    if st.session_state.mission:

        total_steps = len(
            MISSIONS[st.session_state.mission]
        )

        st.info(
            f"🎯 Misión actual: {st.session_state.mission}"
        )

        st.progress(
            st.session_state.mission_step / total_steps
        )

        st.caption(
            f"Paso {st.session_state.mission_step + 1}/{total_steps}"
        )

    for msg in st.session_state.messages:

        avatar = (
            ICONO_IA
            if msg["role"] == "assistant"
            else ICONO_USUARIO
        )

        with st.chat_message(
            msg["role"],
            avatar=avatar
        ):

            st.markdown(msg["content"])

    if st.session_state.mission:

        if st.button(
            "✅ Completar paso",
            use_container_width=True
        ):

            with st.spinner("BlendAI está evaluando..."):
                msg = complete_step()

            st.session_state.messages.append({
                "role": "assistant",
                "content": msg
            })

            st.rerun()

# =========================================================
# SIDE PANEL
# =========================================================
with col2:

    st.subheader("💬 Chat libre")

    st.caption(
        "Preguntas rápidas sobre Blender"
    )

    quick_questions = [
        "¿Cómo hacer una playa realista?",
        "¿Cómo usar Geometry Nodes?",
        "¿Cómo iluminar una escena?",
        "¿Cómo hacer agua realista?",
        "¿Cómo renderizar en Cycles?",
        "¿Cómo optimizar topología?"
    ]

    for q in quick_questions:

        if st.button(
            q,
            use_container_width=True
        ):

            with st.spinner("BlendAI está analizando..."):
                response = ask_ai(q)

            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

            st.rerun()

# =========================================================
# CHAT INPUT
# =========================================================
if prompt := st.chat_input(
    "Pregunta cualquier cosa sobre Blender..."
):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.spinner("BlendAI está analizando..."):
        response = ask_ai(prompt)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    st.rerun()