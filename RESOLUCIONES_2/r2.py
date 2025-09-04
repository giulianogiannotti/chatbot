import os
import re
import traceback
import win32com.client as win32
from win32com.client import constants

# Configuraciones
LOG_EVERY_N = 10          # Cada cuántos archivos mostrar progreso
ENABLE_FILE_LOG = False   # Cambiar a True para guardar log a archivo

DOC_PATTERN = re.compile(r'\.doc$', re.IGNORECASE)
LOG_FILE_PATH = "conversion_log.txt"

def log(message):
    print(message)
    if ENABLE_FILE_LOG:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(message + "\n")

def convertir_todos_doc_a_docx():
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'RESOLUCIONES')
    converted_count = 0
    error_count = 0

    try:
        word = win32.gencache.EnsureDispatch('Word.Application')
        word.Visible = False

        for root, _, files in os.walk(base_dir):
            for file in files:
                if DOC_PATTERN.search(file) and not file.lower().endswith('.docx'):
                    path_doc = os.path.join(root, file)
                    try:
                        new_file = DOC_PATTERN.sub('.docx', path_doc)
                        doc = word.Documents.Open(path_doc)
                        doc.SaveAs(new_file, FileFormat=constants.wdFormatXMLDocument)
                        doc.Close(False)

                        os.remove(path_doc)
                        converted_count += 1

                        if converted_count % LOG_EVERY_N == 0:
                            log(f"✅ {converted_count} archivos convertidos...")

                    except Exception as e:
                        error_count += 1
                        log(f"❌ Error al convertir '{path_doc}': {e}")
                        traceback.print_exc()
        
        log(f"\n🎉 Conversión finalizada. Total convertidos: {converted_count}, con errores: {error_count}")

    except Exception as e:
        log(f"🚨 Error al inicializar Word: {e}")
        traceback.print_exc()

    finally:
        try:
            word.Quit()
        except:
            pass  # En caso de que fallara antes de inicializar Word

if __name__ == "__main__":
    convertir_todos_doc_a_docx()
