import os
import time
import vertexai
import streamlit as st
from datetime import datetime
# from dotenv import load_dotenv
from google.oauth2 import service_account
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage, SystemMessage

# # Acceder a las credenciales desde st.secrets
# credentials_info = st.secrets["google_credentials"]

# # Crear las credenciales de servicio
# credentials = service_account.Credentials.from_service_account_info(credentials_info)

# # Inicializar Vertex AI con las credenciales
# vertexai.init(project=project_id, location=location_l, credentials=credentials)

# # Cargar las credenciales desde st.secrets
# credentials_info = st.secrets["google_credentials"]
# credentials = service_account.Credentials.from_service_account_info(credentials_info)


# load_dotenv()
# os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
# bucket_name = os.getenv("BUCKET_NAME")
# location_l = os.getenv("LOCATION")
# project_id = os.getenv("PROJECT_ID")

fecha = datetime.now()
fecha_actual = fecha.strftime("%d de %B del %Y")

PromptSystem = f"""
```
Esta es la fecha actual: {fecha_actual}.
Eres un sistema de transcripción profesional de alta precisión, especializado en contenido audiovisual de larga duración y dividido en partes. Tu objetivo es generar una transcripción completa, optimizada y **coherente entre partes**, con marcas de tiempo **exactas** que reflejen la ubicación real dentro del audio total, sin reiniciar los tiempos en cada fragmento.

---

### TAREA PRINCIPAL

Transcribe todo el contenido hablado del audio (o segmento del audio) que se te ha proporcionado. Para cada hablante:

1. Agrupa su intervención en **párrafos largos, lógicos y naturales** (mínimo 3 oraciones completas por párrafo).
2. Inserta una única **marca de tiempo exacta** en formato [HH:MM:SS] al **inicio de cada párrafo**, según el segundo real dentro del audio completo (no dentro del fragmento).

---

### CONDICIONES DE SINCRONIZACIÓN

* Si esta es la **primera parte del audio**, los timestamps comienzan desde [00:00:00].
* Si esta es una parte intermedia, usa el valor proporcionado como `timestamp_inicio_parte` para comenzar tu cuenta.
* Calcula todos los tiempos **sumando el tiempo relativo de este fragmento al valor de `timestamp_inicio_parte`.**
* NO reinicies el tiempo, ni inventes saltos grandes.
* NO generes marcas que salten más allá de `timestamp_inicio_parte + duracion_parte`.

---

### FORMATOS Y REGLAS

**REGLAS DE TIMESTAMP:**
* Usa solo el formato [HH:MM:SS] HH:horas, MM:minutos, SS:segundos.
* No coloques múltiples marcas por párrafo.
* Nunca marques timestamps fuera del rango definido.
* Forma primero el párrafo completo y luego determina el timestamp de inicio.

**REGLAS PARA LOS PÁRRAFOS:**
* Cada párrafo debe contener una idea o intervención desarrollada.
* No cortes párrafos de forma abrupta.

**OPTIMIZACIÓN DE TOKENS:**
* Elimina muletillas o repeticiones vacías ("eh", "este", "mmm").
* Conserva repeticiones solo si tienen carga emocional.

---

### FORMATO DE SALIDA:

# Transcripción del Video: "Título del Video"

## Duración de esta parte: duracion_parte minutos

## Esta parte comienza en: [timestamp_inicio_parte]

## Fecha: {fecha_actual}

## Idioma: Español

---

### [HH:MM:SS] Hablante X:

- Texto del párrafo coherente, natural, completo y limpio.

---

### [HH:MM:SS] Hablante Y:

- Continuación natural del discurso en otro bloque, respetando la estructura definida.

---

### NOTA FINAL – CUMPLIMIENTO OBLIGATORIO

* NUNCA reinicies los tiempos en partes posteriores.
* Siempre toma como referencia el timestamp_inicio_parte.
* Sigue estrictamente la estructura de formato proporcionada.
* NO EXPLIQUES este proceso, solo realiza la transcripción como se indica.

---

"""

def generar_transcripcion(base_filename: str, num_segments: int):
    """
    Genera la transcripción de un archivo de audio dividido en segmentos.
    
    Args:
        base_filename (str): Nombre base del archivo de audio.
        num_segments (int): Número de segmentos en los que se divide el audio.
        
    Returns:
        list: Lista de transcripciones generadas por el modelo para cada segmento.
    """
    if "google_credentials" in st.secrets:
    import json
    with open("./tmp/streamlit_gcp_creds.json", "w") as f:
        json.dump(dict(st.secrets["google_credentials"]), f)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./tmp/streamlit_gcp_creds.json"

    bucket_name = st.secrets["BUCKET_NAME"]
    location_l = st.secrets["LOCATION"]
    project_id = st.secrets["PROJECT_ID"]

    vertexai.init(project=project_id, location=location_l)
    
    # Inicializar el modelo 
    model = ChatVertexAI(model_name="gemini-2.5-pro-preview-05-06", temperature=0.7)
    respuestas = []  # Lista para almacenar las respuestas
    respuesta_anterior = ""

    for i in range(num_segments):
        archivo_input = {
            "type": "image_url",
            "image_url": {
                "url": f"gs://{bucket_name}/videos/{base_filename}/{base_filename}_part_{i+1}.mp3"
            },
        }

        if respuesta_anterior:
            text_message = (
                f"""
                - Este audio tiene varias partes; esta es la parte número {i+1}. 
                - Transcripcion anterior que corresponde a la parte **{i-1}** : {respuesta_anterior}. 
                
                - Respeta el timestamp final de la parte anterior y continua desde la ultima parte segun tu anterior respuesta, caundo empiece esta parte del audio desde el segundo 0, solo tienes que seguir segun el tiempo final de la anterior transcripcion. 
                
                IMPORANTE: Esto es un mensaje al sistema no deberas responder a esto, solo debes seguir las instrucciones y generar la transcripción de audio o video."""
            )
        else:
            text_message = (
                f"""
                - Este audio tiene varias partes; esta es la parte número {i+1}. 
                - Comienza la transcripción desde el inicio. 
                
                IMPORANTE: Esto es un mensaje al sistema no deberas responder a esto, solo debes seguir las instrucciones y generar la transcripción de audio o video."""
            )

        message = [
            SystemMessage(content=PromptSystem),
            HumanMessage(content=[text_message, archivo_input]),
        ]

        # Invocar al modelo para obtener la respuesta
        output = model.invoke(message)
        respuesta_actual = str(output.content)
        respuestas.append(respuesta_actual)  # Agregar la respuesta a la lista
        respuesta_anterior = respuesta_actual  # Actualizar la respuesta anterior
        
        texto_completo = "\n\n".join(respuestas)
        time.sleep(60)  # Pausa entre solicitudes
    return texto_completo
