import os
import docx
import fitz  # PyMuPDF
import difflib
from collections import defaultdict
import re

def limpiar_firmas_y_basura(texto):
    """Limpia firmas digitales comunes y líneas vacías excesivas."""
    patrones = [
        r"firmado digitalmente por.*", 
        r"firma.*digital", 
        r"este documento ha sido firmado.*", 
        r"certificado.*digital",
        r"firma.*electrónica",
    ]
    for patron in patrones:
        texto = re.sub(patron, '', texto, flags=re.IGNORECASE)

    lineas = [line.strip() for line in texto.splitlines() if line.strip()]
    return "\n".join(lineas)

def extract_text_docx(path):
    try:
        doc = docx.Document(path)
        return '\n'.join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
    except Exception as e:
        print(f"[ERROR .docx] {path}: {e}")
        return ''

def extract_text_pdf(path):
    try:
        doc = fitz.open(path)
        return '\n'.join([page.get_text().strip() for page in doc])
    except Exception as e:
        print(f"[ERROR .pdf] {path}: {e}")
        return ''

def collect_files_by_basename(root_folder):
    docx_map = defaultdict(list)
    pdf_map = defaultdict(list)

    for root, _, files in os.walk(root_folder):
        for f in files:
            base, ext = os.path.splitext(f)
            full_path = os.path.join(root, f)
            ext = ext.lower()

            if ext == ".docx":
                docx_map[base].append(full_path)
            elif ext == ".pdf":
                pdf_map[base].append(full_path)

    return docx_map, pdf_map

def find_and_compare_all(root_folder):
    docx_map, pdf_map = collect_files_by_basename(root_folder)
    shared_basenames = sorted(set(docx_map.keys()) & set(pdf_map.keys()))

    for base in shared_basenames:
        for docx_path in docx_map[base]:
            for pdf_path in pdf_map[base]:
                text_docx = limpiar_firmas_y_basura(extract_text_docx(docx_path))
                text_pdf = limpiar_firmas_y_basura(extract_text_pdf(pdf_path))

                if not text_docx or not text_pdf:
                    continue  # Si uno no se pudo leer, lo ignoramos

                docx_lines = text_docx.splitlines()
                pdf_lines = text_pdf.splitlines()

                diff = list(difflib.unified_diff(docx_lines, pdf_lines, fromfile='docx', tofile='pdf', lineterm=''))
                cambios = [line for line in diff if line.startswith('+ ') or line.startswith('- ')]

                if cambios:
                    print(f"• '{base}'")
                    print(f"  - DOCX: {docx_path}")
                    print(f"  - PDF : {pdf_path}")
                    print(f"  → ⚠️ DIFERENCIAS REALES DETECTADAS:")
                    for line in cambios:
                        print("    " + line)
                    print()

# USO
FOLDER_PATH = "RESOLUCIONES"  # Reemplazá por tu ruta principal
find_and_compare_all(FOLDER_PATH)
