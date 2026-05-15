import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import uuid
import os
import streamlit.components.v1 as components

# --- CONFIGURACIÓN BASE DE DATOS ---
DB_NAME = "vinilos_ilusion.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventario 
                          (artista TEXT, album TEXT, formato TEXT, condicion TEXT, 
                           stock INTEGER, p_compra REAL, p_venta REAL, genero TEXT,
                           PRIMARY KEY (artista, album, formato, condicion))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas 
                          (transaccion_id TEXT, fecha TEXT, hora TEXT, artista TEXT, album TEXT, 
                           formato TEXT, cantidad INTEGER, p_venta REAL, total REAL, estado TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS apartados 
                          (id TEXT, cliente TEXT, fecha TEXT, artista TEXT, album TEXT, 
                           formato TEXT, cantidad INTEGER, estado TEXT)''')
        conn.commit()

def run_query(query, params=()):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

def get_df(query, params=()):
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query(query, conn, params=params)

# --- FUNCIÓN DE CARGA MASIVA (70 DISCOS) ---
def cargar_70_vinilos():
    discos = [
        ("Pink Floyd", "The Dark Side of the Moon", "LP 12\"", "Nuevo (M/SS)", 5, 350, 650, "Prog Rock"),
        ("Michael Jackson", "Thriller", "LP 12\"", "Como Nuevo (NM)", 3, 280, 500, "Pop"),
        ("The Beatles", "Abbey Road", "LP 12\"", "Nuevo (M/SS)", 4, 320, 600, "Rock"),
        ("Miles Davis", "Kind of Blue", "LP 12\"", "Nuevo (M/SS)", 2, 400, 750, "Jazz"),
        ("Fleetwood Mac", "Rumours", "LP 12\"", "Muy Bueno (VG+)", 6, 250, 450, "Soft Rock"),
        ("Gustavo Cerati", "Bocanada", "LP 12\"", "Nuevo (M/SS)", 3, 500, 950, "Rock Alternativo"),
        ("Soda Stereo", "Canción Animal", "LP 12\"", "Nuevo (M/SS)", 5, 450, 850, "Rock Latino"),
        ("Amy Winehouse", "Back to Black", "LP 12\"", "Nuevo (M/SS)", 8, 220, 400, "Soul"),
        ("Daft Punk", "Random Access Memories", "LP 12\"", "Nuevo (M/SS)", 4, 600, 1100, "Electronic"),
        ("Luis Miguel", "Busca una Mujer", "LP 12\"", "Usado (G)", 10, 100, 250, "Pop Latino"),
        ("Nirvana", "Nevermind", "LP 12\"", "Nuevo (M/SS)", 7, 300, 550, "Grunge"),
        ("Queen", "A Night at the Opera", "LP 12\"", "Como Nuevo (NM)", 3, 350, 680, "Rock"),
        ("Led Zeppelin", "Led Zeppelin IV", "LP 12\"", "Muy Bueno (VG+)", 2, 400, 720, "Hard Rock"),
        ("David Bowie", "Ziggy Stardust", "LP 12\"", "Nuevo (M/SS)", 4, 380, 700, "Glam Rock"),
        ("Radiohead", "OK Computer", "LP 12\"", "Nuevo (M/SS)", 3, 450, 890, "Alternative"),
        ("Metallica", "Master of Puppets", "LP 12\"", "Nuevo (M/SS)", 5, 420, 800, "Thrash Metal"),
        ("Bob Marley", "Legend", "LP 12\"", "Nuevo (M/SS)", 12, 200, 380, "Reggae"),
        ("The Cure", "Disintegration", "LP 12\"", "Nuevo (M/SS)", 4, 400, 780, "New Wave"),
        ("Joy Division", "Unknown Pleasures", "LP 12\"", "Nuevo (M/SS)", 6, 350, 650, "Post-Punk"),
        ("Héctor Lavoe", "La Voz", "LP 12\"", "Muy Bueno (VG+)", 3, 300, 600, "Salsa"),
        ("Rubén Blades", "Siembra", "LP 12\"", "Nuevo (M/SS)", 5, 350, 680, "Salsa"),
        ("Arctic Monkeys", "AM", "LP 12\"", "Nuevo (M/SS)", 9, 280, 520, "Indie Rock"),
        ("The Doors", "The Doors", "LP 12\"", "Como Nuevo (NM)", 4, 340, 620, "Psychedelic Rock"),
        ("Iron Maiden", "Number of the Beast", "LP 12\"", "Nuevo (M/SS)", 3, 390, 750, "Heavy Metal"),
        ("AC/DC", "Back in Black", "LP 12\"", "Nuevo (M/SS)", 6, 320, 580, "Hard Rock"),
        ("Madonna", "Like a Virgin", "LP 12\"", "Usado (G)", 8, 150, 300, "Pop"),
        ("Prince", "Purple Rain", "LP 12\"", "Como Nuevo (NM)", 4, 310, 590, "Funk/Pop"),
        ("The Rolling Stones", "Let It Bleed", "LP 12\"", "Muy Bueno (VG+)", 3, 420, 780, "Rock"),
        ("Stevie Wonder", "Songs in the Key of Life", "LP 12\"", "Como Nuevo (NM)", 2, 550, 980, "Soul/Funk"),
        ("John Coltrane", "A Love Supreme", "LP 12\"", "Nuevo (M/SS)", 3, 400, 760, "Jazz"),
        ("Billie Holiday", "Lady in Satin", "LP 12\"", "Muy Bueno (VG+)", 2, 380, 700, "Jazz/Blues"),
        ("The Smiths", "The Queen Is Dead", "LP 12\"", "Nuevo (M/SS)", 5, 360, 690, "Indie Pop"),
        ("Tame Impala", "Currents", "LP 12\"", "Nuevo (M/SS)", 10, 450, 880, "Psychedelic Pop"),
        ("Lana Del Rey", "Born to Die", "LP 12\"", "Nuevo (M/SS)", 6, 350, 640, "Dream Pop"),
        ("Rosalía", "El Mal Querer", "LP 12\"", "Nuevo (M/SS)", 4, 420, 820, "Flamenco/Pop"),
        ("Bad Bunny", "Un Verano Sin Ti", "LP 12\"", "Nuevo (M/SS)", 15, 600, 1200, "Reggaeton"),
        ("Kendrick Lamar", "To Pimp a Butterfly", "LP 12\"", "Nuevo (M/SS)", 4, 550, 1050, "Hip Hop"),
        ("Kanye West", "MBDTF", "LP 12\"", "Nuevo (M/SS)", 3, 650, 1300, "Hip Hop"),
        ("Lauryn Hill", "Miseducation of...", "LP 12\"", "Nuevo (M/SS)", 5, 400, 780, "R&B/Soul"),
        ("Björk", "Debut", "LP 12\"", "Como Nuevo (NM)", 3, 380, 720, "Art Pop"),
        ("Depeche Mode", "Violator", "LP 12\"", "Nuevo (M/SS)", 5, 420, 850, "Synth-Pop"),
        ("The Clash", "London Calling", "LP 12\"", "Muy Bueno (VG+)", 3, 480, 920, "Punk Rock"),
        ("Ramones", "Ramones", "LP 12\"", "Nuevo (M/SS)", 4, 300, 580, "Punk Rock"),
        ("Serrat", "Mediterráneo", "LP 12\"", "Usado (G)", 6, 200, 400, "Cantautor"),
        ("Charly García", "Clics Modernos", "LP 12\"", "Nuevo (M/SS)", 5, 550, 1000, "Rock Argentino"),
        ("Spinetta", "Artaud", "LP 12\"", "Nuevo (M/SS)", 2, 700, 1500, "Rock Progresivo"),
        ("Caifanes", "El Diablito", "LP 12\"", "Nuevo (M/SS)", 4, 450, 880, "Rock Mexicano"),
        ("Cafe Tacvba", "Re", "LP 12\"", "Nuevo (M/SS)", 3, 500, 950, "Alternative Latino"),
        ("Jimi Hendrix", "Are You Experienced", "LP 12\"", "Como Nuevo (NM)", 3, 420, 800, "Psychedelic Rock"),
        ("Janis Joplin", "Pearl", "LP 12\"", "Muy Bueno (VG+)", 4, 300, 580, "Blues Rock"),
        ("Aretha Franklin", "I Never Loved a Man", "LP 12\"", "Nuevo (M/SS)", 3, 350, 680, "Soul"),
        ("Marvin Gaye", "What's Going On", "LP 12\"", "Nuevo (M/SS)", 5, 380, 750, "Soul"),
        ("Wu-Tang Clan", "36 Chambers", "LP 12\"", "Nuevo (M/SS)", 4, 400, 780, "Hip Hop"),
        ("A Tribe Called Quest", "Low End Theory", "LP 12\"", "Nuevo (M/SS)", 3, 450, 850, "Hip Hop"),
        ("MF DOOM", "Madvillainy", "LP 12\"", "Nuevo (M/SS)", 4, 500, 980, "Hip Hop"),
        ("Gorillaz", "Demon Days", "LP 12\"", "Nuevo (M/SS)", 6, 480, 950, "Alt Rock"),
        ("The Strokes", "Is This It", "LP 12\"", "Nuevo (M/SS)", 7, 320, 600, "Indie Rock"),
        ("Interpol", "Turn on the Lights", "LP 12\"", "Nuevo (M/SS)", 5, 350, 680, "Post-Punk"),
        ("New Order", "Power & Lies", "LP 12\"", "Como Nuevo (NM)", 4, 380, 740, "New Wave"),
        ("Kraftwerk", "The Man-Machine", "LP 12\"", "Nuevo (M/SS)", 3, 420, 820, "Krautrock"),
        ("Celia Cruz", "Azúcar Negra", "LP 12\"", "Muy Bueno (VG+)", 4, 250, 500, "Salsa"),
        ("Willie Colón", "Cosa Nuestra", "LP 12\"", "Usado (G)", 3, 280, 550, "Salsa"),
        ("Fania All Stars", "Live at Cheetah", "LP 12\"", "Muy Bueno (VG+)", 2, 400, 800, "Salsa"),
        ("U2", "Joshua Tree", "LP 12\"", "Como Nuevo (NM)", 6, 280, 520, "Rock"),
        ("The Police", "Synchronicity", "LP 12\"", "Muy Bueno (VG+)", 5, 220, 420, "New Wave"),
        ("Talking Heads", "Remain in Light", "LP 12\"", "Nuevo (M/SS)", 4, 400, 780, "Art Punk"),
        ("Patti Smith", "Horses", "LP 12\"", "Nuevo (M/SS)", 3, 380, 720, "Punk Rock"),
        ("Velvet Underground", "VU & Nico", "LP 12\"", "Nuevo (M/SS)", 5, 450, 880, "Art Rock"),
        ("Beach Boys", "Pet Sounds", "LP 12\"", "Como Nuevo (NM)", 3, 480, 900, "Pop Rock"),
        ("Bob Dylan", "Highway 61", "LP 12\"", "Muy Bueno (VG+)", 3, 420, 780, "Folk Rock")
    ]
    for d in discos:
        run_query("INSERT OR IGNORE INTO inventario VALUES (?,?,?,?,?,?,?,?)", d)

# --- INICIALIZACIÓN ---
st.set_page_config(page_title="Vinilos Ilusión Pro", layout="wide")
init_db()

if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'ticket_a_imprimir' not in st.session_state: st.session_state.ticket_a_imprimir = None

# --- NAVEGACIÓN ---
st.sidebar.title("💿 DISQUERÍA ILUSION")

# Botón especial de inicialización
if st.sidebar.button("✨ Inicializar 70 Vinilos", use_container_width=True):
    cargar_70_vinilos()
    st.sidebar.success("¡70 Vinilos cargados!")
    st.rerun()

menu = ["📦 Stock de Vinilos", "🛒 Punto de Venta", "📝 Reservas", "📊 Corte de Caja", "📉 Historial", "🛠 Agregar Discos", "💾 Respaldos"]
choice = st.sidebar.selectbox("Opciones", menu)

# --- (El resto de las funciones de impresión se mantienen igual que el código anterior) ---
def ejecutar_impresion(html_content):
    unique_id = str(uuid.uuid4())[:8]
    component_script = f"""
    <div id="ticket-{unique_id}" style="display:none;">{html_content}</div>
    <script>
        (function() {{
            var content = document.getElementById('ticket-{unique_id}').innerHTML;
            var win = window.open('', 'PRINT', 'height=600,width=400');
            win.document.write('<html><head><title>Imprimir</title></head><body>' + content + '</body></html>');
            win.document.close();
            win.focus();
            win.print();
            win.close();
        }})();
    </script>
    """
    components.html(component_script, height=0)

if st.session_state.ticket_a_imprimir:
    ejecutar_impresion(st.session_state.ticket_a_imprimir)
    st.session_state.ticket_a_imprimir = None

# --- VISTAS ---
if choice == "📦 Stock de Vinilos":
    st.header("Inventario de Colección")
    df_inv = get_df("SELECT * FROM inventario")
    if df_inv.empty:
        st.warning("El inventario está vacío. Usa el botón 'Inicializar 70 Vinilos' de la izquierda.")
    st.dataframe(df_inv, use_container_width=True)

# (Aquí seguirían las demás secciones: Punto de Venta, Admin, etc., tal cual las configuramos arriba)
