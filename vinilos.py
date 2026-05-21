import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import uuid

# --- CONFIGURACIÓN DE BASE DE DATOS ---
DB_NAME = "tienda_pinturas_v1.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # Tabla de inventario adaptada a productos de pintura
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventario 
                          (producto TEXT, marca TEXT, tipo TEXT, acabado TEXT, 
                           color TEXT, stock INTEGER, p_venta REAL)''')
        # Tabla de registro de ventas
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas 
                          (id TEXT, fecha TEXT, pintura TEXT, cliente TEXT, total REAL)''')
        conn.commit()

# --- 1. SECCIÓN: PRODUCTOS DESTACADOS (VITRINA VIP) ---
def obtener_destacados():
    return [
        {
            "marca": "Titanium Pro", 
            "producto": "Ultra Cover Látex Premium", 
            "precio": 45.99, 
            "tipo": "Látex Acrílico - Alta Resistencia",
            "color": "Blanco Puro",
            "img": "https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=600&auto=format&fit=crop&q=60" # Rodillo pintando pared
        },
        {
            "marca": "ChromaLux", 
            "producto": "Esmalte Al Agua Eco", 
            "precio": 32.50, 
            "tipo": "Esmalte Satinado - Secado Rápido",
            "color": "Verde Selva",
            "img": "https://images.unsplash.com/photo-1580136579312-94651dfd596d?w=600&auto=format&fit=crop&q=60" # Latas de pintura abiertas de colores
        }
    ]

# --- 2. SECCIÓN: INVENTARIO (DATOS REALES DE PINTURAS) ---
def cargar_inventario_completo():
    # Estructura: (producto, marca, tipo, acabado, color, stock, p_venta)
    datos = [
        ("Ultra Cover Látex Premium", "Titanium Pro", "Látex Acrílico", "Mate", "Blanco Puro", 15, 45.99),
        ("Esmalte Al Agua Eco", "ChromaLux", "Esmalte", "Satinado", "Verde Selva", 20, 32.50),
        ("Infinity Wall Professional", "Sherwin Master", "Látex", "Satinado", "Gris Urbano", 12, 55.00),
        ("Protector Exterior Total", "Rust-Oleum", "Pintura Impermeable", "Mate", "Ladrillo", 8, 68.00),
        ("Barniz Marino Poliuretánico", "Cetol", "Barniz Sintético", "Brillante", "Roble Claro", 10, 28.50),
        ("Aerosol Metallic Pro", "Krylon", "Esmalte Sintético", "Brillante", "Oro Ducado", 25, 8.90),
        ("Pintura Tiza para Muebles", "Chalky Line", "Acrílica Especial", "Ultra Mate", "Azul Vintage", 6, 18.50),
        ("Membrana Líquida Techos", "Sika Guard", "Impermeabilizante", "Mate", "Rojo Teja", 14, 75.00),
        ("Pintura Epoxi Alta Resistencia", "Sintex", "Epoxi 2 Componentes", "Brillante", "Gris Industrial", 5, 110.00),
        ("Fondo Blanco Sellador", "Alba", "Imprimación Primer", "Mate", "Blanco", 18, 22.00),
    ]
    
    # Rellenamos hasta obtener más de 70 productos para simular una pinturería completa
    marcas_pool = ["Colorín", "PlastiColor", "Sinteplast", "Benjamin Moore", "Behr", "Glidden"]
    tipos_pool = ["Látex Interior", "Esmalte Sintético", "Acrílico Profesional", "Fondo Antióxido"]
    acabados_pool = ["Mate", "Satinado", "Brillante", "Semimate"]
    colores_pool = ["Azul Marino", "Rojo Esmeralda", "Amarillo Sol", "Negro Profundo", "Beige Arena", "Turquesa"]

    while len(datos) < 75:
        idx = len(datos)
        marca = marcas_pool[idx % len(marcas_pool)]
        tipo = tipos_pool[idx % len(tipos_pool)]
        acabado = acabados_pool[idx % len(acabados_pool)]
        color = colores_pool[idx % len(colores_pool)]
        
        producto = f"Línea Comercial Color-Mix T- {idx}"
        precio = 15.00 + (idx * 0.75)
        datos.append((producto, marca, tipo, acabado, color, 10, precio))

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventario")
        for d in datos:
            cursor.execute("INSERT INTO inventario VALUES (?,?,?,?,?,?,?)", d)
        conn.commit()

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Pinturería VIP - Catálogo y Distribución", layout="wide")

init_db()

# Si el inventario está vacío o faltan registros, lo inicializamos
if pd.read_sql_query("SELECT COUNT(*) FROM inventario", sqlite3.connect(DB_NAME)).iloc[0,0] < 70:
    cargar_inventario_completo()

st.sidebar.title("🎨 COLOR & COATING PANEL")
menu = st.sidebar.selectbox("Navegación:", ["Vitrina VIP", "Inventario Técnico", "Módulo de Ventas / POS"])

# --- VISTA 1: VITRINA VIP ---
if menu == "Vitrina VIP":
    st.title("⚡ Productos Destacados - Máxima Cobertura")
    destacados = obtener_destacados()
    cols = st.columns(2)
    
    for i, item in enumerate(destacados):
        with cols[i % 2]:
            img_src = item['img']
            st.markdown(f"""
                <div style="background-color:#1e1e24; padding:20px; border-radius:15px; border:2px solid #ff4b4b; text-align:center; margin-bottom:20px;">
                    <img src="{img_src}" style="width:100%; height:280px; object-fit:cover; border-radius:10px;">
                    <h2 style="color:white; margin-top:15px; font-family:sans-serif;">{item['producto']}</h2>
                    <h3 style="color:#ff4b4b; font-size:18px; font-weight:bold; margin-top:-5px;">{item['marca']}</h3>
                    <p style="color:#aaa; font-size:16px; margin: 5px 0;">Color: <b>{item['color']}</b></p>
                    <p style="color:#5cd65c; font-size:26px; font-weight:bold; margin: 10px 0;">${item['precio']:.2f} USD</p>
                    <p style="color:#bbb; font-style: italic; font-size:14px;">{item['tipo']}</p>
                </div>
            """, unsafe_allow_html=True)

# --- VISTA 2: INVENTARIO TÉCNICO ---
elif menu == "Inventario Técnico":
    st.title("📦 Catálogo Técnico de Stock de Pinturas")
    st.markdown("Filtra, analiza y audita el stock actual de la sucursal en tiempo real.")
    
    query = """
        SELECT marca as Marca, producto as [Línea Producto], tipo as Tipo, 
               acabado as Acabado, color as Color, stock as [Stock Cajas], 
               p_venta as [Precio Unitario USD] 
        FROM inventario
    """
    df = pd.read_sql_query(query, sqlite3.connect(DB_NAME))
    st.dataframe(df, use_container_width=True, height=650)

# --- VISTA 3: MÓDULO DE VENTAS (CHECKOUT) ---
elif menu == "Módulo de Ventas / POS":
    st.title("🛒 Checkout de Clientes y Notas de Venta")
    
    # Cargamos solo los productos que tengan stock disponible
    df_inv = pd.read_sql_query("SELECT * FROM inventario WHERE stock > 0", sqlite3.connect(DB_NAME))
    
    col_v, col_h = st.columns([1, 1])
    
    with col_v:
        st.subheader("Registrar Nueva Venta")
        
        # Etiqueta amigable que combina Marca + Producto + Color
        lista_productos = df_inv['marca'] + " - " + df_inv['producto'] + " (" + df_inv['color'] + ")"
        seleccion = st.selectbox("Seleccione el Producto solicitado:", lista_productos)
        
        cliente = st.text_input("Nombre del Cliente / Contratista Pintor")
        
        # Extraemos el nombre exacto del producto para buscar su precio y stock
        # Formato del string: "Marca - Producto (Color)"
        marca_sel = seleccion.split(" - ", 1)[0]
        resto = seleccion.split(" - ", 1)[1]
        producto_sel = resto.split(" (")[0]
        
        # Filtrar fila de la DB local para mostrar precio
        pintura_info = df_inv[(df_inv['marca'] == marca_sel) & (df_inv['producto'] == producto_sel)].iloc[0]
        
        st.info(f"💡 **Especificaciones:** Tipo: {pintura_info['tipo']} | Acabado: {pintura_info['acabado']} | Stock: {pintura_info['stock']} unidades.")
        st.write(f"### **Precio Final:** ${pintura_info['p_venta']:.2f} USD")
        
        if st.button("Procesar Factura de Venta"):
            if cliente:
                with sqlite3.connect(DB_NAME) as conn:
                    # Inserción en el historial de ventas
                    conn.execute("INSERT INTO ventas VALUES (?,?,?,?,?)", 
                                 (str(uuid.uuid4())[:8], 
                                  datetime.now().strftime("%Y-%m-%d %H:%M"), 
                                  f"{marca_sel} - {producto_sel}", 
                                  cliente, 
                                  pintura_info['p_venta']))
                    
                    # Descuento de stock en el almacén
                    conn.execute("UPDATE inventario SET stock = stock - 1 WHERE producto = ? AND marca = ?", 
                                 (pintura_info['producto'], pintura_info['marca']))
                    conn.commit()
                
                st.balloons()
                st.success(f"¡Venta registrada para **{cliente}**! El stock fue actualizado exitosamente.")
                st.rerun()
            else:
                st.error("Por favor, ingrese el nombre del comprador para poder emitir el comprobante.")
    
    with col_h:
        st.subheader("📋 Libro de Ventas Recientes")
        ventas = pd.read_sql_query("SELECT id as [Nro Ticket], fecha as Fecha, pintura as [Detalle Producto], cliente as Cliente, total as [Total Pagado USD] FROM ventas ORDER BY fecha DESC", sqlite3.connect(DB_NAME))
        
        if ventas.empty:
            st.warning("Aún no se registran transacciones en el turno actual.")
        else:
            st.table(ventas)
