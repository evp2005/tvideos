import os
import uuid
import streamlit as st
from CorteVideos import ProcesadorVideo
from Administrar_archivos import CrearDocumentos, vaciar_documento, vaciar_audios, vaciar_videos

if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())
user_id = st.session_state["user_id"]

bucket_documents = st.secrets["BUCKET_DOCUMENTS"]

def __main__():
    st.set_page_config(
    page_title="Transcripcion de Videos",
    page_icon="📺",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/evp2005',
        'Report a bug': 'https://github.com/evp2005',
        'About': "# Transcripcion de Videos y Audios con IA\n\nEsta aplicación permite transcribir videos o audios a texto utilizando inteligencia artificial. Puedes subir tus archivos y generar transcripciones en diferentes formatos como PDF, Word y Texto.",
    })
    st.title("Transcripcion de Videos 📼", False)
    st.write("Esta aplicación permite transcribir videos a texto.")
    st.divider()
    
    def tipo_archivo(filename):
        ext = os.path.splitext(filename)[1].lower()
        if ext in [".mp3", ".wav", ".flac"]:
            return "audio"
        elif ext in [".mp4", ".avi", ".mov", ".mkv"]:
            return "video"
        else:
            return "desconocido"
    
    # Subir el archivo de video o audio
    st.header("1. Primero", False)
    print("Servidor Abierto")
    
    # archivo = st.file_uploader("Sube tu video aqui", accept_multiple_files=False, type=["mp4", "avi", "mov", "mkv"]) 

    # if archivo is not None:
    #     # Especifica la carpeta donde deseas guardar el archivo
    #     save_folder = "archivos_subidos"
    #     os.makedirs(save_folder, exist_ok=True)
    #     save_path = os.path.join(save_folder, archivo.name)
    #     # Guarda el archivo en el disco
    #     with open(save_path, "wb") as f:
    #         f.write(archivo.getbuffer())
    #     nombre_limpio  = re.sub(r'[^\w\s.]', '', archivo.name)  # Elimina caracteres especiales
    #     nombre_espacio = nombre_limpio.replace(" ", "_")
    #     nombre_minisculas = nombre_espacio.lower()
    #     destino = f"archivos_subidos/video_{nombre_minisculas}"
    #     if os.path.exists(destino):
    #         os.remove(destino)
    #     os.rename(save_path, destino)
    #     st.success(f"Archivo guardado en: {destino}")
    
    archivo = st.file_uploader("Sube tu video aqui", accept_multiple_files=False, type=["mp4", "avi", "mov", "mkv"])  
    if archivo is not None:
        # Especifica la carpeta donde deseas guardar el archivo
        save_folder = "archivos_subidos"
        os.makedirs(save_folder, exist_ok=True)
        save_path = os.path.join(save_folder, archivo.name)
        # Guarda el archivo en el disco
        with open(save_path, "wb") as f:
            f.write(archivo.getbuffer())
        destino = f"archivos_subidos/video_{user_id}.mp4"
        if os.path.exists(destino):
            os.remove(destino)
        os.rename(save_path, destino)
        st.success(f"Archivo guardado en: {destino}")
        
        tipo = tipo_archivo(archivo.name)
        
        if tipo == "audio":
            st.audio(archivo)
        else:
            st.video(archivo)
    st.divider()
    
    # Transcribir el video o audio
    st.header("2. Segundo", False)
    st.write("Genera tu transcripcion aqui ✅.")
    if archivo is not None:
        if os.path.exists(destino):
            if st.button("Generar Transcripcion", icon="📝"):
                with st.chat_message("ai"):
                    spinner = st.spinner("Generando transcripcion...", show_time=True)
                    with spinner:
                        vaciar_documento(user_id=user_id)
                        procesador = ProcesadorVideo(base_filename=destino, user_id=user_id)
                        procesador.procesar_y_subir()
                        texto = procesador.send_transcripcion_gemini()
                        respuesta = {
                            "user_id": user_id,
                            "contenido": texto,
                        }
                        CrearDocumentos(texto_md=respuesta["contenido"], user_id=respuesta["user_id"])
                        # Guardar en session_state para persistencia
                        vaciar_audios(user_id=user_id)
                        vaciar_videos(user_id=user_id)
                        st.session_state["texto_transcripcion"] = respuesta
                        st.session_state["transcripcion_generada"] = True
                    st.success("Video transcrito con exito! 💪🦁")
            
            # Mostrar tabs si la transcripción ya fue generada
            if st.session_state.get("transcripcion_generada"):
                respuesta = st.session_state.get("texto_transcripcion", "")
                tab1, tab2, tab3 = st.tabs(["📕 PDF", "📘 WORD", "📄 TEXTO"])

                tab1.subheader("La transcripcion en formato PDF", False)
                tab2.subheader("La transcripcion en formato WORD", False)
                tab3.subheader("La transcripcion en formato TEXTO", False)

                path_docs = f"documents/{user_id}/Transcripcion_{user_id}"
                url_pdf = f"https://storage.googleapis.com/{bucket_documents}/documents/{user_id}/Transcripcion.pdf"
                url_docx = f"https://storage.googleapis.com/{bucket_documents}/documents/{user_id}/Transcripcion.docx"
                if os.path.exists(f"{path_docs}.md"):
                    vaciar_documento(user_id=user_id)
                    # Mostrar PDF en el tab1
                    pdf_mostrar = f'<iframe src="{url_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                    
                    tab1.markdown(pdf_mostrar, unsafe_allow_html=True)

                    tab2.link_button("Descargar Docx 📘", url=url_docx, icon=":material/download:")
                    
                    tab3.code(respuesta["contenido"], language="markdown")
if '__main__' == __name__:
    __main__()
