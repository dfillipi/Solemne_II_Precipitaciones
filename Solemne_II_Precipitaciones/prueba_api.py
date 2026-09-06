import requests
import pandas as pd
import html

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
respuesta = requests.get(url, params=parametros)

# Verificar si la conexión fue exitosa
if respuesta.status_code == 200:

    print("Conexión establecida correctamente.")

    # Obtener datos en formato JSON
    datos = respuesta.json()

    # Extraer registros
    registros = datos["result"]["records"]

    # Crear DataFrame
    df = pd.DataFrame(registros)

    print("\nRegistros obtenidos desde la API:", len(df))

    # Eliminar columna interna creada por DataStore
    df = df.drop(columns=["_id"])

    # Recuperar la primera fila que fue utilizada como encabezado
    primera_fila = pd.DataFrame([{
        columna: columna for columna in df.columns
    }])

    # Agregar nuevamente la primera observación
    df = pd.concat([primera_fila, df], ignore_index=True)

    # Asignar nombres claros a las columnas
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

    # Corregir símbolo de grados de la latitud
    df["latitud"] = df["latitud"].apply(html.unescape)

    # Convertir variables numéricas
    df["altitud_m"] = pd.to_numeric(df["altitud_m"], errors="coerce")
    df["anio"] = pd.to_numeric(df["anio"], errors="coerce")
    df["mes"] = pd.to_numeric(df["mes"], errors="coerce")
    df["dia"] = pd.to_numeric(df["dia"], errors="coerce")
    df["precipitacion_mm"] = pd.to_numeric(
        df["precipitacion_mm"],
        errors="coerce"
    )

    # Crear una columna de fecha
    df["fecha"] = pd.to_datetime(
        {
            "year": df["anio"],
            "month": df["mes"],
            "day": df["dia"]
        },
        errors="coerce"
    )

    print("\nTOTAL DE REGISTROS DESPUÉS DE LA LIMPIEZA:")
    print(len(df))

    print("\nCOLUMNAS CORREGIDAS:")
    print(df.columns.tolist())

    print("\nPRIMEROS 10 REGISTROS:")
    print(df.head(10).to_string(index=False))

    print("\nINFORMACIÓN GENERAL:")
    print(df.info())

else:

    print("Error al consultar la API.")
    print("Código de estado:", respuesta.status_code)