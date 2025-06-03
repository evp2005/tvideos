import os
import shutil
from SubirArchivos import subir_archivo
from pdf2docx import parse
from markdown_pdf import MarkdownPdf, Section

# def vaciar_videos_audios(user_id:str):
#     carpeta_audios = f"audio_segments_{user_id}"
#     carpeta_videos = f"archivos_subidos_{user_id}"
#     if os.path.isdir(carpeta_videos):
#         if os.listdir(carpeta_videos):
#             print("🗑️ Eliminando archivos videos temporales...")
#             shutil.rmtree(carpeta_audios)
#             os.makedirs(carpeta_audios)
#             print("🗑️ Audios temporales eliminados.")
#             shutil.rmtree(carpeta_videos)
#             os.makedirs(carpeta_videos)
#             print("🗑️ Videos temporales eliminados.")
#         else:
#             print("🗑️ No hay videos o audios temporales para borrar.")
#     else:
#         print("La ruta especificada no es una carpeta.")

def vaciar_audios(user_id:str):
        if os.path.exists(f"./audio_segments/{user_id}/video_{user_id}.mp4_part_1.mp3"):
            print("🗑️ Eliminando archivos videos temporales...")
            carpeta = f"audio_segments/{user_id}"
            shutil.rmtree(carpeta)
            print("🗑️ Audios temporales eliminados.")
        else:
            print("🗑️ No hay Audios temporales para borrar.")

def vaciar_videos(user_id:str):
    if os.path.isdir("archivos_subidos"):
        print("🗑️ Carpeta encontrada...")
        if os.listdir("archivos_subidos"):
            os.remove(f"archivos_subidos/video_{user_id}.mp4")
            print("🗑️ Videos temporales eliminados.")
    else:
        print("Carpeta no encontrada.")
    
def vaciar_documento(user_id:str):
    if os.path.exists(f"documents/{user_id}/Transcripcion_{user_id}.md"):
        print("🗑️ Eliminando Documentos temporales...")
        shutil.rmtree(f"documents/{user_id}")
    else:
        print("🗑️ No hay documentos temporales para eliminar.")

def CrearDocumentos(texto_md:str, user_id:str):
    # Crear la carpeta 'documents' si no existe
    documents_dir = f"documents/{user_id}"
    os.makedirs(documents_dir, exist_ok=True)

    md_path = os.path.join(documents_dir, f"Transcripcion_{user_id}.md")
    pdf_path = os.path.join(documents_dir, f"Transcripcion_{user_id}.pdf")
    docx_path = os.path.join(documents_dir, f"Transcripcion_{user_id}.docx")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(texto_md)
    print("✅ MD generado exitosamente.")
    
    # Crear una instancia de MarkdownPdf
    pdf = MarkdownPdf(toc_level=0, optimize=True)

    # Leer el contenido del archivo Markdown
    with open(md_path, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Agregar el contenido como una sección al PDF
    pdf.add_section(Section(contenido))

    # Guardar el PDF resultante
    pdf.save(pdf_path)
    subir_archivo(user_id, pdf_path, "pdf")
    print("✅ PDF generado y subido exitosamente.")
    
    # Conversión
    parse(pdf_path, docx_path)
    subir_archivo(user_id, docx_path, "docx")
    print("✅ DOCX generado y subido exitosamente.")