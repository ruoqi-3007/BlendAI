import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import sqlite3
import hashlib
import os

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="BlendAI", layout="wide", page_icon="🎮")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("Missing GROQ_API_KEY")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# =========================================================
# DB
# =========================================================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    xp INTEGER,
    level INTEGER,
    unlocked TEXT,
    avatar TEXT,
    title TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS skills (
    username TEXT,
    modeling INTEGER,
    materials INTEGER,
    lighting INTEGER,
    animation INTEGER,
    sculpting INTEGER,
    geometry INTEGER
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS achievements (
    username TEXT,
    name TEXT
)
''')

conn.commit()

# =========================================================
# SESSION
# =========================================================
DEFAULTS = {
    "logged_in": False,
    "username": "",
    "xp": 0,
    "level": 1,
    "mission": None,
    "mission_step": 0,
    "messages": [],
    "unlocked": ["Cubo"],
    "avatar": "👨‍🚀",
    "title": "Novice"
}

for k,v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k]=v

# =========================================================
# MISSIONS (ORIGINAL RESTORED)
# =========================================================
MISSIONS = {
    "Cubo": ["Abrir Blender","Crear cubo","Escalar objeto","Material básico"],
    "Donut": ["Crear torus","Subdivision","Glaseado","Render"],
    "Coche": ["Bloqueo base","Ruedas","Low poly","Material"],
    "Sculpt": ["Entrar Sculpt","Clay","Smooth","Detalles"],
    "Materiales PBR": ["Shader","Texturas","Normal Maps","Roughness"],
    "Iluminación": ["HDRI","Lights","Cycles","Cinematic"],
    "Geometry Nodes": ["Nodo base","Distribución","Instancing","Procedural"],
    "Animación": ["Keyframes","Timeline","Camera","Render"]
}

UNLOCKS = {
    "Cubo":"Donut",
    "Donut":"Coche",
    "Coche":"Sculpt",
    "Sculpt":"Materiales PBR",
    "Materiales PBR":"Iluminación",
    "Iluminación":"Geometry Nodes",
    "Geometry Nodes":"Animación"
}

SKILL_MAP = {
    "Cubo":["modeling"],
    "Donut":["modeling","materials"],
    "Coche":["modeling","materials"],
    "Sculpt":["sculpting"],
    "Materiales PBR":["materials"],
    "Iluminación":["lighting"],
    "Geometry Nodes":["geometry"],
    "Animación":["animation"]
}

# =========================================================
# UTILS
# =========================================================

def hash(p):
    return hashlib.sha256(p.encode()).hexdigest()

# =========================================================
# SAVE
# =========================================================

def save():
    c.execute("UPDATE users SET xp=?,level=?,unlocked=?,avatar=?,title=? WHERE username=?",
              (st.session_state.xp,
               st.session_state.level,
               ",".join(st.session_state.unlocked),
               st.session_state.avatar,
               st.session_state.title,
               st.session_state.username))
    conn.commit()

# =========================================================
# TITLE SYSTEM
# =========================================================
TITLES=["Novice","Apprentice","Junior","Artist","Senior","Tech Artist","Expert","Master","Legend","Myth"]

def update_title():
    st.session_state.title=TITLES[min(len(TITLES)-1,st.session_state.level//10)]

# =========================================================
# XP SYSTEM (RESTORED RPG)
# =========================================================

def add_xp(xp,mission=None):

    st.session_state.xp+=xp
    st.session_state.level=min(100,1+st.session_state.xp//50)

    if mission:
        c.execute("SELECT * FROM skills WHERE username=?",(st.session_state.username,))
        if not c.fetchone():
            c.execute("INSERT INTO skills VALUES (?,?,?,?,?,?,?)",
                      (st.session_state.username,0,0,0,0,0,0))

        for s in SKILL_MAP.get(mission,[]):
            c.execute(f"UPDATE skills SET {s}={s}+1 WHERE username=?",
                      (st.session_state.username,))

    update_title()
    save()

# =========================================================
# AI + CONTEXT (RESTORED DDG)
# =========================================================
@st.cache_data(ttl=3600)
def get_context(q):
    try:
        with DDGS() as ddgs:
            r=ddgs.text(q+" Blender docs",max_results=2)
            return "\n".join(x.get("body","") for x in r)[:1000]
    except:
        return ""


def ask_ai(prompt):

    context = get_context(prompt)

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Eres tutor experto en Blender (última versión estable). Explica SIEMPRE paso a paso para principiantes. No asumas conocimientos previos. Divide las explicaciones en pasos numerados claros y añade atajos de teclado cuando sea posible."
            },
            {
                "role": "system",
                "content": context
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.5
    )

    return r.choices[0].message.content

# =========================================================
# LOGIN
# =========================================================

def register(u,p):
    try:
        c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)",
                  (u,hash(p),0,1,"Cubo","👨‍🚀","Novice"))
        conn.commit()
        return True
    except:
        return False


def login(u,p):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (u,hash(p)))
    return c.fetchone()

# =========================================================
# LOGIN SCREEN
# =========================================================
if not st.session_state.logged_in:

    st.title("BlendAI")

    u=st.text_input("User")
    p=st.text_input("Pass",type="password")

    if st.button("Login"):
        user=login(u,p)
        if user:
            st.session_state.logged_in=True
            st.session_state.username=u
            st.session_state.xp=user[2]
            st.session_state.level=user[3]
            st.session_state.unlocked=user[4].split(",")
            st.session_state.avatar=user[5]
            st.session_state.title=user[6]
            st.rerun()

    if st.button("Register"):
        register(u,p)
        st.success("Created")

    st.stop()

# =========================================================
# HEADER
# =========================================================

st.title(f"{st.session_state.avatar} BlendAI")
st.caption(f"{st.session_state.title} | Level {st.session_state.level} | XP {st.session_state.xp}")
