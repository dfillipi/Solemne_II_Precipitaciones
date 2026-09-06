import requests
import pandas as pd
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

if respuesta.status_code == 200:

    print("Conexión establecida correctamente.")

    # Obtener datos JSON
    datos = respuesta.json()

    # Extraer registros y crear DataFrame
    registros = datos["result"]["records"]
    df = pd.DataFrame(registros)

    # Eliminar columna interna de la API
    df = df.drop(columns=["_id"])

    # Recuperar primera observación utilizada como encabezado
    primera_fila = pd.DataFrame([
        {columna: columna for columna in df.columns}
    ])

    df = pd.concat([primera_fila, df], ignore_index=True)

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

    # Convertir columnas numéricas
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

    # ---------------------------------------------------
    # ANÁLISIS DESCRIPTIVO
    # ---------------------------------------------------

    print("\nRESUMEN GENERAL")
    print("--------------------------------")

    print("Cantidad total de registros:", len(df))

    print(
        "Registros con precipitación:",
        df["precipitacion_mm"].notna().sum()
    )

    print(
        "Registros sin precipitación:",
        df["precipitacion_mm"].isna().sum()
    )

    print(
        "Cantidad de estaciones:",
        df["estacion"].nunique()
    )

    print(
        "Fecha inicial:",
        df["fecha"].min()
    )

    print(
        "Fecha final:",
        df["fecha"].max()
    )

    # Estadísticas de precipitación
    print("\nESTADÍSTICAS DE PRECIPITACIÓN")
    print("--------------------------------")

    print(
        "Promedio:",
        round(df["precipitacion_mm"].mean(), 2),
        "mm"
    )

    print(
        "Máximo:",
        round(df["precipitacion_mm"].max(), 2),
        "mm"
    )

    print(
        "Mínimo:",
        round(df["precipitacion_mm"].min(), 2),
        "mm"
    )

    print(
        "Desviación estándar:",
        round(df["precipitacion_mm"].std(), 2),
        "mm"
    )

    # Registro con mayor precipitación
    mayor_precipitacion = df.loc[
        df["precipitacion_mm"].idxmax()
    ]

    print("\nREGISTRO CON MAYOR PRECIPITACIÓN")
    print("--------------------------------")

    print(
        "Estación:",
        mayor_precipitacion["estacion"]
    )

    print(
        "Fecha:",
        mayor_precipitacion["fecha"]
    )

    print(
        "Precipitación:",
        mayor_precipitacion["precipitacion_mm"],
        "mm"
    )

    # Precipitación acumulada por estación
    precipitacion_estacion = (
        df.groupby("estacion")["precipitacion_mm"]
        .sum()
        .sort_values(ascending=False)
    )

    print("\nPRECIPITACIÓN ACUMULADA POR ESTACIÓN")
    print("--------------------------------")

    print(precipitacion_estacion)

else:

    print("Error al consultar la API.")
    print("Código de estado:", respuesta.status_code)