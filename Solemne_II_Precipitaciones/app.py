import requests
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import html

# ==========================================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Precipitaciones Chile 2024",
    page_icon="🌧️",
    layout="wide"
)

# ==========================================================
# FUNCIÓN PARA OBTENER Y PREPARAR LOS DATOS
# ==========================================================

@st.cache_data
def cargar_datos():

    # URL de la API de Datos Abiertos del Gobierno de Chile
    url = "https://datos.gob.cl/api/3/action/datastore_search"

    # Identificador del recurso
    resource_id = "b1c63be7-c3d1-4daa-aa29-6128c5646d13"

    # Parámetros de la consulta
    parametros = {
        "resource_id": resource_id,
        "limit": 1000
    }

    # Realizar solicitud GET
    respuesta = requests.get(
        url,
        params=parametros,
        timeout=30
    )

    # Verificar respuesta
    respuesta.raise_for_status()

    # Convertir respuesta a JSON
    datos = respuesta.json()

    # Extraer registros
    registros = datos["result"]["records"]

    # Crear DataFrame
    df = pd.DataFrame(registros)

    # Eliminar columna interna del DataStore
    df = df.drop(columns=["_id"])

    # Recuperar la primera observación utilizada como encabezado
    primera_fila = pd.DataFrame([
        {columna: columna for columna in df.columns}
    ])

    # Incorporar la observación al DataFrame
    df = pd.concat(
        [primera_fila, df],
        ignore_index=True
    )

    # Renombrar columnas
    df.columns = [
        "codigo_estacion",
        "estacion",
        "latitud",
        "altitud_m",
        "anio",
        "mes",
        "dia",
        "precipitacion_mm"
    ]

    # Corregir caracteres especiales
    df["latitud"] = df["latitud"].apply(html.unescape)

    # Convertir variables numéricas
    columnas_numericas = [
        "altitud_m",
        "anio",
        "mes",
        "dia",
        "precipitacion_mm"
    ]

    for columna in columnas_numericas:

        df[columna] = pd.to_numeric(
            df[columna],
            errors="coerce"
        )

    # Crear fecha
    df["fecha"] = pd.to_datetime(
        {
            "year": df["anio"],
            "month": df["mes"],
            "day": df["dia"]
        },
        errors="coerce"
    )

    return df


# ==========================================================
# CARGAR DATOS
# ==========================================================

try:

    df = cargar_datos()

except Exception as error:

    st.error(
        "No fue posible obtener los datos desde la API."
    )

    st.write(error)

    st.stop()


# ==========================================================
# ENCABEZADO
# ==========================================================

st.title("🌧️ Análisis de Precipitaciones en Chile")

st.subheader("Junio de 2024")

st.write(
    """
    Aplicación desarrollada en Python y Streamlit para
    analizar datos públicos de precipitaciones obtenidos
    mediante una API REST del Gobierno de Chile.
    """
)

st.divider()


# ==========================================================
# PANEL LATERAL
# ==========================================================

st.sidebar.header("🔎 Filtros")

lista_estaciones = sorted(
    df["estacion"].dropna().unique()
)

estaciones_seleccionadas = st.sidebar.multiselect(
    "Seleccione una o más estaciones:",
    options=lista_estaciones,
    default=lista_estaciones
)

# Aplicar filtro
if estaciones_seleccionadas:

    df_filtrado = df[
        df["estacion"].isin(estaciones_seleccionadas)
    ].copy()

else:

    df_filtrado = df.copy()

# ==========================================================
# FILTRO POR RANGO DE FECHAS
# ==========================================================

st.sidebar.subheader("📅 Período")

fecha_minima = df["fecha"].min().date()
fecha_maxima = df["fecha"].max().date()

rango_fechas = st.sidebar.date_input(
    "Seleccione el período:",
    value=(fecha_minima, fecha_maxima),
    min_value=fecha_minima,
    max_value=fecha_maxima,
    format="DD/MM/YYYY"
)

# Aplicar filtro cuando existen fecha inicial y final
if len(rango_fechas) == 2:

    fecha_inicio = pd.to_datetime(rango_fechas[0])
    fecha_fin = pd.to_datetime(rango_fechas[1])

    df_filtrado = df_filtrado[
        (df_filtrado["fecha"] >= fecha_inicio)
        & (df_filtrado["fecha"] <= fecha_fin)
    ].copy()

st.sidebar.write(
    "Estaciones seleccionadas:",
    len(estaciones_seleccionadas)
)

st.sidebar.write(
    "Registros mostrados:",
    len(df_filtrado)
)

if len(rango_fechas) == 2:

    st.sidebar.write(
        "Período analizado:",
        rango_fechas[0].strftime("%d/%m/%Y"),
        "al",
        rango_fechas[1].strftime("%d/%m/%Y")
    )

# ==========================================================
# INDICADORES PRINCIPALES
# ==========================================================

st.header("📊 Resumen general")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Estaciones",
        df_filtrado["estacion"].nunique()
    )

with col2:

    st.metric(
        "Registros",
        len(df_filtrado)
    )

with col3:

    promedio = df_filtrado[
        "precipitacion_mm"
    ].mean()

    st.metric(
        "Precipitación promedio",
        f"{promedio:.2f} mm"
    )

with col4:

    maximo = df_filtrado[
        "precipitacion_mm"
    ].max()

    st.metric(
        "Máximo registro diario",
        f"{maximo:.1f} mm"
    )


# ==========================================================
# PESTAÑAS DE NAVEGACIÓN
# ==========================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🏆 Por estación",
        "📅 Evolución diaria",
        "📈 Distribución",
        "📋 Datos"
    ]
)


# ==========================================================
# TAB 1 - PRECIPITACIÓN POR ESTACIÓN
# ==========================================================

with tab1:

    st.subheader(
        "Precipitación acumulada por estación"
    )

    # Calcular precipitación acumulada por estación
    acumulado_estacion = (
        df_filtrado
        .groupby("estacion")["precipitacion_mm"]
        .sum()
        .sort_values(ascending=False)
    )

    # Determinar cantidad de estaciones a mostrar
    if len(acumulado_estacion) <= 5:

        cantidad = len(acumulado_estacion)

        st.write(
            f"Se muestran las {cantidad} estaciones seleccionadas."
        )

    else:

        cantidad = st.slider(
            "Cantidad de estaciones a visualizar:",
            min_value=5,
            max_value=min(
                20,
                len(acumulado_estacion)
            ),
            value=min(
                10,
                len(acumulado_estacion)
            )
        )

    # Preparar datos para el gráfico
    datos_grafico = (
        acumulado_estacion
        .head(cantidad)
        .sort_values()
    )

    # Crear gráfico
    fig1, ax1 = plt.subplots(
        figsize=(12, 7)
    )

    barras = ax1.barh(
        datos_grafico.index,
        datos_grafico.values
    )

    # Mostrar valor al final de cada barra
    ax1.bar_label(
        barras,
        fmt="%.1f mm",
        padding=3
    )

    ax1.set_title(
        "Estaciones con mayor precipitación acumulada"
    )

    ax1.set_xlabel(
        "Precipitación acumulada (mm)"
    )

    ax1.set_ylabel(
        "Estación meteorológica"
    )

    fig1.tight_layout()

    # Mostrar gráfico en Streamlit
    st.pyplot(fig1)

    # Mostrar interpretación automática
    if not acumulado_estacion.empty:

        estacion_mayor = acumulado_estacion.index[0]

        valor_mayor = acumulado_estacion.iloc[0]

        st.info(
            f"La estación con mayor precipitación "
            f"acumulada dentro de la selección es "
            f"{estacion_mayor}, con "
            f"{valor_mayor:.1f} mm."
        )


# ==========================================================
# TAB 2 - EVOLUCIÓN DIARIA
# ==========================================================

with tab2:

    st.subheader(
        "Precipitación total diaria"
    )

    precipitacion_diaria = (
        df_filtrado
        .groupby("fecha")["precipitacion_mm"]
        .sum()
    )

    fig2, ax2 = plt.subplots(
        figsize=(12, 6)
    )

    ax2.plot(
        precipitacion_diaria.index,
        precipitacion_diaria.values,
        marker="o"
    )

    ax2.set_title(
        "Evolución diaria de las precipitaciones"
    )

    ax2.set_xlabel("Fecha")

    ax2.set_ylabel(
        "Precipitación total (mm)"
    )

    plt.xticks(rotation=45)

    fig2.tight_layout()

    st.pyplot(fig2)

    if not precipitacion_diaria.empty:

        fecha_maxima = (
            precipitacion_diaria.idxmax()
        )

        valor_maximo = (
            precipitacion_diaria.max()
        )

        st.info(
            f"El mayor total diario de la selección "
            f"se registró el "
            f"{fecha_maxima.strftime('%d-%m-%Y')}, "
            f"con {valor_maximo:.1f} mm acumulados "
            f"entre las estaciones seleccionadas."
        )


# ==========================================================
# TAB 3 - DISTRIBUCIÓN
# ==========================================================

with tab3:

    st.subheader(
        "Distribución de los registros de precipitación"
    )

    fig3, ax3 = plt.subplots(
        figsize=(11, 6)
    )

    ax3.hist(
        df_filtrado[
            "precipitacion_mm"
        ].dropna(),
        bins=20
    )

    ax3.set_title(
        "Distribución de precipitaciones"
    )

    ax3.set_xlabel(
        "Precipitación (mm)"
    )

    ax3.set_ylabel(
        "Frecuencia"
    )

    fig3.tight_layout()

    st.pyplot(fig3)

    st.write(
        """
        La distribución permite observar la frecuencia
        de los diferentes niveles de precipitación.
        Los valores bajos presentan una mayor frecuencia,
        mientras que los eventos de alta precipitación
        ocurren con menor frecuencia.
        """
    )


# ==========================================================
# TAB 4 - DATOS
# ==========================================================

with tab4:

    st.subheader(
        "Exploración de los registros"
    )

    columnas_mostrar = [
        "codigo_estacion",
        "estacion",
        "latitud",
        "altitud_m",
        "fecha",
        "precipitacion_mm"
    ]

    st.dataframe(
        df_filtrado[columnas_mostrar],
        use_container_width=True
    )

    # Preparar archivo CSV para descarga
    csv = (
        df_filtrado[columnas_mostrar]
        .to_csv(
            index=False
        )
        .encode("utf-8")
    )

    st.download_button(
        label="⬇️ Descargar datos filtrados",
        data=csv,
        file_name="precipitaciones_filtradas.csv",
        mime="text/csv"
    )


# ==========================================================
# INFORMACIÓN ADICIONAL
# ==========================================================

st.divider()

with st.expander(
    "ℹ️ Información sobre el proyecto"
):

    st.write(
        """
        Los datos utilizados en esta aplicación
        corresponden a registros meteorológicos
        disponibles públicamente a través del
        Portal de Datos Abiertos del Gobierno de Chile.

        El procesamiento fue realizado utilizando
        Python, Requests, JSON, Pandas, Matplotlib
        y Streamlit.
        """
    )

    st.write(
        "Período analizado: junio de 2024."
    )

    st.write(
        "Cantidad total de registros procesados:",
        len(df)
    )