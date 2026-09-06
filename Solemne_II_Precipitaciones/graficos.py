import requests
import pandas as pd
import matplotlib.pyplot as plt
import html

# URL de la API de Datos Abiertos del Gobierno de Chile
url = "https://datos.gob.cl/api/3/action/datastore_search"

# Identificador del recurso
resource_id = "b1c63be7-c3d1-4daa-aa29-6128c5646d13"

# Parámetros de consulta
parametros = {
    "resource_id": resource_id,
    "limit": 1000
}

# Realizar solicitud GET
respuesta = requests.get(url, params=parametros)

# Verificar conexión
if respuesta.status_code == 200:

    print("Conexión establecida correctamente.")

    # Obtener respuesta JSON
    datos = respuesta.json()

    # Extraer registros
    registros = datos["result"]["records"]

    # Crear DataFrame
    df = pd.DataFrame(registros)

    # Eliminar columna interna de la API
    df = df.drop(columns=["_id"])

    # Recuperar primera observación utilizada como encabezado
    primera_fila = pd.DataFrame([
        {columna: columna for columna in df.columns}
    ])

    # Incorporar nuevamente la primera observación
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
    df["altitud_m"] = pd.to_numeric(
        df["altitud_m"],
        errors="coerce"
    )

    df["anio"] = pd.to_numeric(
        df["anio"],
        errors="coerce"
    )

    df["mes"] = pd.to_numeric(
        df["mes"],
        errors="coerce"
    )

    df["dia"] = pd.to_numeric(
        df["dia"],
        errors="coerce"
    )

    df["precipitacion_mm"] = pd.to_numeric(
        df["precipitacion_mm"],
        errors="coerce"
    )

    # Crear columna fecha
    df["fecha"] = pd.to_datetime(
        {
            "year": df["anio"],
            "month": df["mes"],
            "day": df["dia"]
        },
        errors="coerce"
    )

    # ==================================================
    # GRÁFICO 1
    # 10 ESTACIONES CON MAYOR PRECIPITACIÓN ACUMULADA
    # ==================================================

    acumulado_estacion = (
        df.groupby("estacion")["precipitacion_mm"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    acumulado_grafico = acumulado_estacion.sort_values()

    fig, ax = plt.subplots(figsize=(13, 8))

    barras = ax.barh(
        acumulado_grafico.index,
        acumulado_grafico.values
    )

    # Mostrar valor al final de cada barra
    ax.bar_label(
        barras,
        fmt="%.1f mm",
        padding=4
    )

    ax.set_title(
        "10 estaciones con mayor precipitación acumulada\nJunio 2024",
        fontsize=15
    )

    ax.set_xlabel("Precipitación acumulada (mm)")
    ax.set_ylabel("Estación meteorológica")

    # Ajustar espacio para nombres largos
    fig.subplots_adjust(
        left=0.36,
        right=0.91,
        top=0.88,
        bottom=0.12
    )

    plt.show()

    # ==================================================
    # GRÁFICO 2
    # PRECIPITACIÓN TOTAL DIARIA
    # ==================================================

    precipitacion_diaria = (
        df.groupby("fecha")["precipitacion_mm"]
        .sum()
    )

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(
        precipitacion_diaria.index,
        precipitacion_diaria.values,
        marker="o"
    )

    ax.set_title(
        "Precipitación total diaria registrada\nJunio 2024",
        fontsize=15
    )

    ax.set_xlabel("Fecha")
    ax.set_ylabel("Precipitación total (mm)")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.show()

    # ==================================================
    # GRÁFICO 3
    # DISTRIBUCIÓN DE LOS REGISTROS DE PRECIPITACIÓN
    # ==================================================

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(
        df["precipitacion_mm"].dropna(),
        bins=20
    )

    ax.set_title(
        "Distribución de los registros de precipitación\nJunio 2024",
        fontsize=15
    )

    ax.set_xlabel("Precipitación (mm)")
    ax.set_ylabel("Frecuencia")

    plt.tight_layout()

    plt.show()

else:

    print("Error al consultar la API.")
    print("Código de estado:", respuesta.status_code)