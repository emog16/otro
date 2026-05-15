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
        # Inventario adaptado a música
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventario 
                          (artista TEXT, album TEXT, formato TEXT, condicion TEXT, 
                           stock INTEGER, p_compra REAL, p_venta REAL, genero TEXT,
                           PRIMARY KEY (artista, album, formato, condicion))''')
        # Ventas
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas 
                          (transaccion_id TEXT, fecha TEXT, hora TEXT, artista TEXT, album TEXT, 
                           formato TEXT, cantidad INTEGER, p_venta REAL, total REAL, estado TEXT)''')
        # Apartados (Reservas de discos)
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

# --- FUNCIÓN DE IMPRESIÓN ---
def ejecutar_impresion(html_content):
    unique_id = str(uuid.uuid4())[:8]
    component_script = f"""
    <div id="ticket-{unique_id}" style="display:none;">{html_content}</div>
    <script>
        (function() {{
            var content = document.getElementById('ticket-{unique_id}').innerHTML;
            var win = window.open('', 'PRINT', 'height=600,width=400');
            win.document.write('<html><head><title>Ticket Vinilos</title></head><body>' + content + '</body></html>');
            win.document.close();
            win.focus();
            win.print();
            win.close();
        }})();
    </script>
    """
    components.html(component_script, height=0)

def generar_ticket_html(titulo, id_doc, items, total, cliente=None):
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    return f"""
    <div style="font-family: 'Courier New', monospace; width: 250px; padding: 10px; background: white; color: black; border: 1px solid #ddd;">
        <center><h2 style="margin:0;">VINILOS ILUSIÓN</h2><p style="font-size:12px; margin:0;">Record Store</p></center>
        <hr>
        <p style="font-size:11px;"><b>{titulo}</b>: #{id_doc}<br><b>Fecha:</b> {fecha}</p>
        {f'<p style="font-size:11px;"><b>Cliente:</b> {cliente}</p>' if cliente else ''}
        <table style="width:100%; font-size:10px;">
            {"".join([f"<tr><td>{it['album'][:15]}...</td><td align='center'>{it['cantidad']}</td><td align='right'>${it['subtotal']:,.2f}</td></tr>" for it in items])}
        </table>
        <hr><h3 align="right">TOTAL: ${total:,.2f}</h3>
        <center><p style="font-size:9px;">¡Gracias por apoyar la cultura física!</p></center>
    </div>
    """

# --- INICIALIZACIÓN ---
st.set_page_config(page_title="Vinilos Ilusión Pro", layout="wide")
init_db()

if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'ticket_a_imprimir' not in st.session_state: st.session_state.ticket_a_imprimir = None

# --- NAVEGACIÓN ---
st.sidebar.title("💿 DISQUERÍA ILUSION")
menu = ["📦 Stock de Vinilos", "🛒 Punto de Venta", "📝 Reservas", "📊 Corte de Caja", "📉 Historial", "🛠 Agregar Discos", "💾 Respaldos"]
choice = st.sidebar.selectbox("Opciones", menu)

if st.session_state.ticket_a_imprimir:
    ejecutar_impresion(st.session_state.ticket_a_imprimir)
    st.session_state.ticket_a_imprimir = None

# --- 1. INVENTARIO ---
if choice == "📦 Stock de Vinilos":
    st.header("Inventario de Colección")
    df_inv = get_df("SELECT artista, album, formato, condicion, stock, p_venta, genero FROM inventario")
    st.dataframe(df_inv, use_container_width=True)

# --- 2. PUNTO DE VENTA ---
elif choice == "🛒 Punto de Venta":
    st.header("Venta de Discos")
    df_inv = get_df("SELECT * FROM inventario WHERE stock > 0")
    
    if not df_inv.empty:
        c1, c2 = st.columns(2)
        with c1:
            art_sel = st.selectbox("Artista", sorted(df_inv['artista'].unique()))
            df_f = df_inv[df_inv['artista'] == art_sel]
            alb_sel = st.selectbox("Álbum", sorted(df_f['album'].unique()))
            df_f = df_f[df_f['album'] == alb_sel]
            formato_sel = st.selectbox("Formato/Condición", df_f.apply(lambda x: f"{x['formato']} ({x['condicion']})", axis=1))
            
            # Extraer fila seleccionada
            item = df_f.iloc[0] 
            
            st.info(f"Disponibles: {item['stock']} | Precio: ${item['p_venta']:,.2f}")
            cant = st.number_input("Cantidad", 1, int(item['stock']))
            
            if st.button("➕ Añadir a la Bolsa", use_container_width=True):
                st.session_state.carrito.append({
                    'artista': item['artista'], 'album': item['album'], 'formato': item['formato'],
                    'cantidad': cant, 'precio': item['p_venta'], 'subtotal': item['p_venta']*cant
                })
                st.rerun()
            
            if st.button("🗑️ Vaciar Bolsa", type="secondary", use_container_width=True):
                st.session_state.carrito = []
                st.rerun()

        with c2:
            if st.session_state.carrito:
                st.subheader("Bolsa de Compra")
                st.table(pd.DataFrame(st.session_state.carrito)[['artista', 'album', 'cantidad', 'subtotal']])
                total_v = sum(i['subtotal'] for i in st.session_state.carrito)
                if st.button(f"✅ Finalizar Venta (${total_v:,.2f})", type="primary", use_container_width=True):
                    t_id = "VIN-" + str(uuid.uuid4())[:6].upper()
                    now = datetime.now()
                    for i in st.session_state.carrito:
                        run_query("INSERT INTO ventas VALUES (?,?,?,?,?,?,?,?,?,?)", 
                                  (t_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), i['artista'], i['album'], i['formato'], i['cantidad'], i['precio'], i['subtotal'], "COMPLETADA"))
                        run_query("UPDATE inventario SET stock = stock - ? WHERE artista=? AND album=? AND formato=?", (i['cantidad'], i['artista'], i['album'], i['formato']))
                    st.session_state.ticket_a_imprimir = generar_ticket_html("TICKET VENTA", t_id, st.session_state.carrito, total_v)
                    st.session_state.carrito = []
                    st.rerun()

# --- 4. CORTE DE CAJA ---
elif choice == "📊 Corte de Caja":
    st.header("Corte de Caja / Ganancias Musicales")
    periodo = st.radio("Periodo:", ["Hoy", "Esta Semana", "Este Mes"], horizontal=True)
    
    hoy = datetime.now()
    if periodo == "Hoy": fecha_inicio = hoy.strftime("%Y-%m-%d")
    elif periodo == "Esta Semana": fecha_inicio = (hoy - timedelta(days=hoy.weekday())).strftime("%Y-%m-%d")
    else: fecha_inicio = hoy.strftime("%Y-%m-01")
    
    query_corte = """
        SELECT v.*, i.p_compra 
        FROM ventas v 
        LEFT JOIN inventario i ON v.artista = i.artista AND v.album = i.album AND v.formato = i.formato
        WHERE v.fecha >= ? AND v.estado = 'COMPLETADA'
    """
    df_corte = get_df(query_corte, (fecha_inicio,))
    
    if not df_corte.empty:
        total_v = df_corte['total'].sum()
        total_c = (df_corte['cantidad'] * df_corte['p_compra']).sum()
        utilidad = total_v - total_c
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Venta Bruta", f"${total_v:,.2f}")
        c2.metric("Costo de Discos", f"${total_c:,.2f}")
        c3.metric("Ganancia Real", f"${utilidad:,.2f}")
        st.dataframe(df_corte, use_container_width=True)
    else:
        st.info("No hay registros en este periodo.")

# --- 6. ADMIN / AGREGAR DISCOS ---
elif choice == "🛠 Agregar Discos":
    st.header("Gestión de Catálogo")
    with st.form("disco_nuevo"):
        c1, c2 = st.columns(2)
        art = c1.text_input("Artista / Banda")
        alb = c2.text_input("Nombre del Álbum")
        c3, c4, c5 = st.columns(3)
        fmt = c3.selectbox("Formato", ["LP 12\"", "EP 10\"", "Single 7\"", "Boxset", "CD"])
        con = c4.selectbox("Condición", ["Nuevo (M/SS)", "Como Nuevo (NM)", "Muy Bueno (VG+)", "Usado (G)"])
        gen = c5.text_input("Género")
        c6, c7, c8 = st.columns(3)
        stk = c6.number_input("Stock", 0)
        pc = c7.number_input("Precio Compra", 0.0)
        pv = c8.number_input("Precio Venta", 0.0)
        
        if st.form_submit_button("Guardar en Catálogo"):
            run_query("INSERT OR REPLACE INTO inventario VALUES (?,?,?,?,?,?,?,?)", (art, alb, fmt, con, stk, pc, pv, gen))
            st.success(f"Disco de {art} guardado correctamente.")

# --- 7. RESPALDOS ---
elif choice == "💾 Respaldos":
    st.header("Backup de Datos")
    if os.path.exists(DB_NAME):
        with open(DB_NAME, "rb") as f:
            st.download_button("📥 Descargar Base de Datos", f, f"Backup_Discos_{datetime.now().strftime('%Y%m%d')}.db")
