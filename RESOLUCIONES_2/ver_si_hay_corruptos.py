import os
from docx import Document
from PyPDF2 import PdfReader

DOCS_PATH = 'RESOLUCIONES'

def es_docx_valido(filepath):
    try:
        _ = Document(filepath)
        return True
    except Exception:
        return False

def es_pdf_valido(filepath):
    try:
        with open(filepath, 'rb') as f:
            reader = PdfReader(f)
            _ = reader.pages[0]  # intenta acceder a la primera página
        return True
    except Exception:
        return False

corruptos = []

for root, _, files in os.walk(DOCS_PATH):
    for file in files:
        if file.lower().endswith('.docx'):
            full_path = os.path.join(root, file)
            if not es_docx_valido(full_path):
                corruptos.append(full_path)
        elif file.lower().endswith('.pdf'):
            full_path = os.path.join(root, file)
            if not es_pdf_valido(full_path):
                corruptos.append(full_path)

# Mostrar resultados
if corruptos:
    print("❌ Archivos corruptos o ilegibles encontrados:\n")
    for path in corruptos:
        print(f"• {path}")
else:
    print("✅ Todos los archivos .docx y .pdf se pudieron abrir correctamente.")
