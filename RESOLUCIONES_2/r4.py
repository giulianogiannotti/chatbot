import os
import re
import traceback
import win32com.client as win32
from win32com.client import constants

# Configuraciones
LOG_EVERY_N = 10          # Mostrar log cada N archivos
ENABLE_FILE_LOG = False
LOG_FILE_PATH = "conversion_log.txt"

SUPPORTED_INPUTS = ['.doc', '.docm']

def log(message):
    print(message)
    if ENABLE_FILE_LOG:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(message + "\n")

def convertir_doc_y_docm_a_docx():
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'RESOLUCIONES')
    converted_count = 0
    skipped_count = 0
    error_count = 0

    try:
        word = win32.gencache.EnsureDispatch('Word.Application')
        word.Visible = False

        for root, _, files in os.walk(base_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()

                if ext in SUPPORTED_INPUTS:
                    path_in = os.path.join(root, file)
                    path_out = os.path.splitext(path_in)[0] + '.docx'

                    if os.path.exists(path_out):
                        skipped_count += 1
                        continue

                    try:
                        doc = word.Documents.Open(path_in)
                        doc.SaveAs(path_out, FileFormat=constants.wdFormatXMLDocument)
                        doc.Close(False)
                        os.remove(path_in)

                        converted_count += 1
                        if converted_count % LOG_EVERY_N == 0:
                            log(f"✅ {converted_count} archivos convertidos...")

                    except Exception as e:
                        error_count += 1
                        log(f"❌ Error al convertir '{path_in}': {e}")
                        traceback.print_exc()

        log(f"\n🎉 Conversión finalizada. Total convertidos: {converted_count}, salteados: {skipped_count}, con errores: {error_count}")

    except Exception as e:
        log(f"🚨 Error al inicializar Word: {e}")
        traceback.print_exc()

    finally:
        try:
            word.Quit()
        except:
            pass

if __name__ == "__main__":
    convertir_doc_y_docm_a_docx()