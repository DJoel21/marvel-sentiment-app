import streamlit as st
import pandas as pd
import plotly.express as px
from textblob import TextBlob

# Configuración inicial de la página
st.set_page_config(
    page_title="Sentimiento Películas Marvel",
    page_icon="🎬",
    layout="wide"
)

# Título de la aplicación
st.title("🎬 Analizador de Sentimientos: Películas de Marvel (MCU)")
st.write("Esta aplicación analiza reseñas de películas del Universo Cinematográfico de Marvel, detecta si las opiniones son **Positivas**, **Negativas** o **Neutrales** y genera gráficos interactivos.")

# Dataset predeterminado con reseñas internas de películas de Marvel
RESEÑAS_MARVEL_DEFAULT = [
    {"Pelicula": "Avengers: Endgame", "Comentario": "Una obra maestra absoluta del cine de superhéroes, el cierre perfecto para la saga."},
    {"Pelicula": "Avengers: Endgame", "Comentario": "Demasiado larga y con algunas inconsistencias en los viajes en el tiempo, pero entretenida."},
    {"Pelicula": "Iron Man", "Comentario": "Robert Downey Jr. interpreta al personaje a la perfección, el inicio brillante del MCU."},
    {"Pelicula": "Spider-Man: No Way Home", "Comentario": "Increíble nostalgia y emoción ver a los tres Spider-Man juntos en pantalla, me encantó."},
    {"Pelicula": "Spider-Man: No Way Home", "Comentario": "Depende demasiado del fan service y el guion tiene varios agujeros de trama."},
    {"Pelicula": "Thor: Love and Thunder", "Comentario": "El humor es excesivo y arruina los momentos dramáticos e importantes de la película."},
    {"Pelicula": "Thor: Love and Thunder", "Comentario": "Efectos visuales geniales y Christian Bale hace una actuación increíble como Gorr."},
    {"Pelicula": "Eternals", "Comentario": "Película aburrida, con personajes poco desarrollados y un ritmo muy lento."},
    {"Pelicula": "Eternals", "Comentario": "Visualmente hermosa y con una propuesta diferente y madura a lo habitual de Marvel."},
    {"Pelicula": "Guardians of the Galaxy Vol. 3", "Comentario": "Emotiva, divertida y con una banda sonora espectacular, excelente historia de origen."},
    {"Pelicula": "Ant-Man and the Wasp: Quantumania", "Comentario": "Efectos especiales decepcionantes y un guion débil que no aprovecha al villano."},
    {"Pelicula": "Captain America: The Winter Soldier", "Comentario": "Las escenas de acción e intriga política la convierten en una de las mejores películas de Marvel."}
]

# Función para evaluar sentimiento
def analizar_sentimiento(texto):
    analysis = TextBlob(str(texto))
    polarity = analysis.sentiment.polarity
    
    if polarity > 0.05:
        return "Positivo"
    elif polarity < -0.05:
        return "Negativo"
    else:
        # Evaluación por palabras clave en español si la polaridad por defecto es neutral
        texto_lower = str(texto).lower()
        palabras_pos = ["excelente", "maestra", "increíble", "brillante", "emotiva", "divertida", "espectacular", "geniales", "hermosa", "mejores", "me encantó", "perfecto"]
        palabras_neg = ["aburrida", "lento", "decepcionantes", "inconsistencias", "agujeros", "excesivo", "arruina", "larga", "débil", "malo", "pésimo"]
        
        c_pos = sum(1 for p in palabras_pos if p in texto_lower)
        c_neg = sum(1 for n in palabras_neg if n in texto_lower)
        
        if c_pos > c_neg:
            return "Positivo"
        elif c_neg > c_pos:
            return "Negativo"
        else:
            return "Neutral"

# Barra lateral para selección de la fuente de datos
st.sidebar.header("⚙️ Fuente de Datos")
opcion_fuente = st.sidebar.radio(
    "Selecciona cómo ingresar las opiniones de Marvel:",
    ["Reseñas Predeterminadas del MCU", "Ingreso Manual de Opiniones", "Cargar Archivo (CSV / TXT)"]
)

df = pd.DataFrame()

# 1. Datos internos predeterminados
if opcion_fuente == "Reseñas Predeterminadas del MCU":
    df = pd.DataFrame(RESEÑAS_MARVEL_DEFAULT)
    st.sidebar.success(f"Cargadas {len(df)} reseñas de prueba del MCU.")

# 2. Entrada manual
elif opcion_fuente == "Ingreso Manual de Opiniones":
    st.subheader("📝 Ingreso Manual de Reseñas de Marvel")
    nombre_pelicula = st.text_input("Nombre de la Película de Marvel:", value="Avengers: Secret Wars")
    texto_manual = st.text_area(
        "Escribe las reseñas (una por línea):",
        value="La película fue increíble, las escenas de acción superaron mis expectativas.\nLos efectos visuales lucen muy falsos y la trama es aburrida.",
        height=150
    )
    if texto_manual:
        lineas = [linea.strip() for linea in texto_manual.split("\n") if linea.strip()]
        df = pd.DataFrame({"Pelicula": nombre_pelicula, "Comentario": lineas})

# 3. Cargar archivo CSV o TXT
else:
    st.subheader("📂 Cargar Archivo de Comentarios de Marvel")
    archivo = st.file_uploader("Sube un archivo .csv o .txt", type=["csv", "txt"])
    if archivo is not None:
        if archivo.name.endswith(".csv"):
            df_cargado = pd.read_csv(archivo)
            col_comentario = st.selectbox("Selecciona la columna con los comentarios:", df_cargado.columns)
            col_pelicula = st.selectbox("Selecciona la columna con el nombre de la película (opcional):", ["Ninguna"] + list(df_cargado.columns))
            
            df = df_cargado.rename(columns={col_comentario: "Comentario"})
            if col_pelicula != "Ninguna":
                df = df.rename(columns={col_pelicula: "Pelicula"})
            else:
                df["Pelicula"] = "Marvel (General)"
        else:
            contenido = archivo.read().decode("utf-8")
            lineas = [l.strip() for l in contenido.split("\n") if l.strip()]
            df = pd.DataFrame({"Pelicula": "Marvel (General)", "Comentario": lineas})

# Procesar análisis si existen datos
if not df.empty and "Comentario" in df.columns:
    # Aplicar análisis de sentimientos
    df["Sentimiento"] = df["Comentario"].apply(analizar_sentimiento)

    # Filtro por Película en la barra lateral
    lista_peliculas = ["Todas las Películas"] + list(df["Pelicula"].unique())
    pelicula_sel = st.sidebar.selectbox("🎯 Filtrar por Película de Marvel:", lista_peliculas)

    if pelicula_sel != "Todas las Películas":
        df_filtrado = df[df["Pelicula"] == pelicula_sel].copy()
    else:
        df_filtrado = df.copy()

    # Métricas principales
    st.markdown("---")
    st.subheader("📌 Resumen del Análisis de Opiniones")
    
    col1, col2, col3, col4 = st.columns(4)
    total = len(df_filtrado)
    pos = len(df_filtrado[df_filtrado["Sentimiento"] == "Positivo"])
    neg = len(df_filtrado[df_filtrado["Sentimiento"] == "Negativo"])
    neu = len(df_filtrado[df_filtrado["Sentimiento"] == "Neutral"])

    col1.metric("Total Reseñas", total)
    col2.metric("Positivas 🟢", pos, f"{(pos/total*100):.1f}%" if total > 0 else "0%")
    col3.metric("Negativas 🔴", neg, f"{(neg/total*100):.1f}%" if total > 0 else "0%")
    col4.metric("Neutrales ⚪", neu, f"{(neu/total*100):.1f}%" if total > 0 else "0%")

    # Gráficos
    st.markdown("---")
    st.subheader("📊 Gráficos de Sentimiento")
    
    conteo = df_filtrado["Sentimiento"].value_counts().reset_index()
    conteo.columns = ["Sentimiento", "Cantidad"]
    
    colores = {"Positivo": "#2ECC71", "Negativo": "#E74C3C", "Neutral": "#95A5A6"}

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        fig_barras = px.bar(
            conteo,
            x="Sentimiento",
            y="Cantidad",
            color="Sentimiento",
            color_discrete_map=colores,
            title="Cantidad de Comentarios Positivos, Negativos y Neutrales",
            text="Cantidad"
        )
        st.plotly_chart(fig_barras, use_container_width=True)

    with col_g2:
        fig_pastel = px.pie(
            conteo,
            names="Sentimiento",
            values="Cantidad",
            color="Sentimiento",
            color_discrete_map=colores,
            title="Distribución Porcentual de las Críticas",
            hole=0.4
        )
        st.plotly_chart(fig_pastel, use_container_width=True)

    # Gráfico adicional comparativo si hay múltiples películas
    if pelicula_sel == "Todas las Películas" and len(df_filtrado["Pelicula"].unique()) > 1:
        st.subheader("🎬 Comparativa de Sentimientos por Película de Marvel")
        df_comp = df_filtrado.groupby(["Pelicula", "Sentimiento"]).size().reset_index(name="Cantidad")
        fig_comp = px.bar(
            df_comp,
            x="Pelicula",
            y="Cantidad",
            color="Sentimiento",
            barmode="group",
            color_discrete_map=colores,
            title="Reseñas Positivas vs Negativas por Título"
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    # Tabla con datos detallados
    st.markdown("---")
    st.subheader("📋 Detalle de Reseñas Analizadas")
    st.dataframe(df_filtrado, use_container_width=True)

else:
    st.info("Selecciona una opción en el menú lateral o carga un archivo para realizar el análisis.")