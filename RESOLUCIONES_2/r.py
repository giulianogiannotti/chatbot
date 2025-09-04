import os
import re
import win32com.client as win32
from win32com.client import constants

def save_as_docx(path_doc):
    word = win32.gencache.EnsureDispatch('Word.Application')
    word.Visible = False

    doc = word.Documents.Open(path_doc)
    doc.Activate()

    new_file = re.sub(r'\.doc$', '.docx', path_doc, flags=re.IGNORECASE)
    doc.SaveAs(new_file, FileFormat=constants.wdFormatXMLDocument)
    doc.Close(False)
    word.Quit()

    # Eliminar el archivo .doc original después de convertir
    os.remove(path_doc)
    print(f"✔️ Convertido y eliminado: {path_doc}")

def convertir_todos_doc_a_docx():
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'RESOLUCIONES')

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith('.doc') and not file.lower().endswith('.docx'):
                path_doc = os.path.join(root, file)
                try:
                    print(f"🔄 Convirtiendo: {path_doc}")
                    save_as_docx(path_doc)
                except Exception as e:
                    print(f"❌ Error al convertir {path_doc}: {e}")

if __name__ == "__main__":
    convertir_todos_doc_a_docx()
