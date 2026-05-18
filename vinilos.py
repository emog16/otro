import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import uuid

# --- CONFIGURACIÓN DE BASE DE DATOS ---
DB_NAME = "tienda_vinilos_v1.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventario 
                          (album TEXT, artista TEXT, formato TEXT, edicion TEXT, 
                           stock INTEGER, p_venta REAL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas 
                          (id TEXT, fecha TEXT, vinilo TEXT, cliente TEXT, total REAL)''')
        conn.commit()

# --- 1. SECCIÓN: VINILOS PRINCIPALES (VITRINA VIP) ---
def obtener_destacados():
    return [
        {
            "artista": "Pink Floyd", 
            "album": "The Dark Side of the Moon", 
            "precio": 450.00, 
            "formato": "LP 180g - 50th Anniversary Box Set",
            "img": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?w=600&auto=format&fit=crop&q=60" # Imagen de vinilo girando
        },
        {
            "artista": "Daft Punk", 
            "album": "Random Access Memories", 
            "precio": 180.00, 
            "formato": "2xLP Clear Vinyl - 10th Anniversary",
            "img": "https://images.unsplash.com/photo-1539628399213-d6aa19c93074?w=600&auto=format&fit=crop&q=60" # Imagen de portadas/discos
        }
    ]

# --- 2. SECCIÓN: INVENTARIO (DATOS REALES DE VINILOS) ---
def cargar_inventario_completo():
    datos = [
        ("The Dark Side of the Moon", "Pink Floyd", "12\" LP 180g", "50th Anniversary", 5, 450.00),
        ("Random Access Memories", "Daft Punk", "2xLP Clear Vinyl", "10th Anniversary", 8, 180.00),
        ("Abbey Road", "The Beatles", "12\" LP Picture Disc", "Limited Edition", 3, 95.00),
        ("Thriller", "Michael Jackson", "12\" LP UltraDisc One-Step", "MoFi Box Set", 2, 135.00),
        ("Kind of Blue", "Miles Davis", "2xLP 45 RPM", "Analogue Productions", 4, 120.00),
        ("Back to Black", "Amy Winehouse", "12\" LP Pink Vinyl", "Exclusive Edition", 10, 45.00),
        ("Rumours", "Fleetwood Mac", "12\" LP Gold Standard", "Collector Series", 6, 85.00),
        ("The Rise and Fall of Ziggy Stardust", "David Bowie", "12\" LP Half-Speed Master", "50th Edition", 4, 75.00),
        ("To Pimp a Butterfly", "Kendrick Lamar", "2xLP Clear Vinyl", "Interscope Edition", 7, 65.00),
        ("Blonde", "Frank Ocean", "2xLP Black Vinyl", "Official Repress 2022", 1, 299.00),
    ]
    
    artistas_pool = ["Led Zeppelin", "Nirvana", "Radiohead", "Queen", "Metallica", "The Rolling Stones", "Madonna"]
    while len(datos) < 70:
        art = artistas_pool[len(datos) % len(artistas_pool)]
        datos.append((f"Collector Album Vol. {len(datos)}", art, "12\" LP Colored", "Limited Deluxe", 3, 35.00 + (len(datos)*0.50)))

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventario")
        for d in datos:
            cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?)", (d[0], d[1], d[2], d[3], d[4], d[5]))
        conn.commit()

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Disquería VIP - Vinilos de Colección", layout="wide")

init_db()
if pd.read_sql_query("SELECT COUNT(*) FROM inventario", sqlite3.connect(DB_NAME)).iloc[0,0] < 70:
    cargar_inventario_completo()

st.sidebar.title("🎵 AUDIO CONTROL PANEL")
menu = st.sidebar.selectbox("Ir a:", ["Vitrina VIP", "Inventario Técnico", "Sección de Compras"])

if menu == "Vitrina VIP":
    st.title("⚡ Joyas de la Corona - Ediciones Coleccionista")
    destacados = obtener_destacados()
    cols = st.columns(2)
    for i, item in enumerate(destacados):
        with cols[i % 2]:
            img_src = item['img']
            
            st.markdown(f"""
                <div style="background-color:#0f0f11; padding:20px; border-radius:15px; border:1px solid #1db954; text-align:center; margin-bottom:20px;">
                    <img src="{img_src}" style="width:100%; height:280px; object-fit:cover; border-radius:10px;">
                    <h2 style="color:white; margin-top:15px; font-family:sans-serif;">{item['album']}</h2>
                    <h3 style="color:#888; font-size:18px; font-weight:normal; margin-top:-10px;">{item['artista']}</h3>
                    <p style="color:#1db954; font-size:24px; font-weight:bold; margin: 10px 0;">${item['precio']:.2f} USD</p>
                    <p style="color:#aaa; font-style: italic; font-size:14px;">{item['formato']}</p>
                </div>
            """, unsafe_allow_html=True)

elif menu == "Inventario Técnico":
    st.title("📦 Catálogo General de Vinilos (70 Títulos)")
    df = pd.read_sql_query("SELECT artista as Artista, album as Álbum, formato as [Tipo Formato], edicion as [Edición Especial], p_venta as [Precio USD] FROM inventario", sqlite3.connect(DB_NAME))
    st.dataframe(df, use_container_width=True, height=700)

elif menu == "Sección de Compras":
    st.title("🛒 Checkout - Registro de Ventas")
    df_inv = pd.read_sql_query("SELECT * FROM inventario WHERE stock > 0", sqlite3.connect(DB_NAME))
    
    col_v, col_h = st.columns([1, 1])
    with col_v:
        nombre_vinilo = st.selectbox("Seleccione el Vinilo", df_inv['artista'] + " - " + df_inv['album'])
        cliente = st.text_input("Nombre del Melómano / Comprador")
        
        # Extraer el álbum exacto para buscar el precio
        album_seleccionado = nombre_vinilo.split(" - ", 1)[1]
        vinilo_info = df_inv[df_inv['album'] == album_seleccionado].iloc[0]
        
        st.write(f"**Precio del Ejemplar:** ${vinilo_info['p_venta']:.2f} USD")
        if st.button("Procesar Transacción"):
            if cliente:
                with sqlite3.connect(DB_NAME) as conn:
                    conn.execute("INSERT INTO ventas VALUES (?,?,?,?,?)", 
                                 (str(uuid.uuid4())[:8], datetime.now().strftime("%Y-%m-%d %H:%M"), nombre_vinilo, cliente, vinilo_info['p_venta']))
                    conn.execute("UPDATE inventario SET stock = stock - 1 WHERE album = ?", (vinilo_info['album'],))
                st.balloons()
                st.success("¡Venta procesada con éxito! El stock ha sido actualizado.")
            else:
                st.error("Por favor, ingrese el nombre del cliente para el recibo.")
    
    with col_h:
        st.subheader("📋 Historial de Ventas de la Tienda")
        ventas = pd.read_sql_query("SELECT fecha as Fecha, vinilo as [Álbum / Artista], cliente as Cliente, total as [Total Pagado] FROM ventas", sqlite3.connect(DB_NAME))
        st.table(ventas)
