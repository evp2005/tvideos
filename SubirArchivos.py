# Cargar las variables de entorno
import os
import json
import streamlit as st
# from dotenv import load_dotenv
from google.cloud import storage
from google.oauth2 import service_account

# load_dotenv()
# os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
# bucket_documents = os.getenv("BUCKET_DOCUMENTS")

def subir_archivo(user_id, ruta_archivo_local, tipo_archivo):
    bucket_documents = st.secrets["BUCKET_DOCUMENTS"]

    # Cargar las credenciales desde st.secrets
    credentials_info = st.secrets["google_credentials"]
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    
    # Inicializa el cliente de GCS
    storage_client = storage.Client(credentials=credentials)
    
    # Obtiene el bucket
    bucket = storage_client.bucket(bucket_documents)
    
    # Define el nombre del blob con la carpeta 'archivitos'
    blob = bucket.blob(f'documents/{user_id}/Transcripcion.{tipo_archivo}')
    
    # Sube el archivo al blob
    blob.upload_from_filename(ruta_archivo_local)
    
    print(f'Archivo {tipo_archivo} subido en el bucket {bucket_documents}.')
