import os
import chardet
import fitz  # PyMuPDF
from docx import Document
from collections import defaultdict
import string

# Configuración
RUTA_BASE = 'RESOLUCIONES'
MIN_CARACTERES = 100
EXTENSIONES_VALIDAS = {'.pdf', '.docx', '.txt'}

resultados_por_tipo = defaultdict(list)

def es_legible(texto):
    if not texto or texto.strip() == '':
        return False

    total = len(texto)
    if total < 50:
        return False  # muy corto, sospechoso

    imprimibles = sum(1 for c in texto if c in string.printable or c in string.whitespace)
    proporcion = imprimibles / total

    # si menos del 85% del texto son caracteres "normales", lo marcamos como ilegible
    return proporcion > 0.85

def extraer_texto_pdf(path):
    try:
        doc = fitz.open(path)
        texto = ""
        for page in doc:
            texto += page.get_text()
        return texto
    except Exception:
        return None

def extraer_texto_docx(path):
    try:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        return None

def extraer_texto_txt(path):
    try:
        with open(path, 'rb') as f:
            raw = f.read()
        result = chardet.detect(raw)
        encoding = result['encoding'] or 'utf-8'
        return raw.decode(encoding, errors='replace')
    except Exception:
        return None

def deducir_tipo(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in EXTENSIONES_VALIDAS:
        return ext.lstrip('.')
    
    nombre = os.path.basename(path).lower()
    for tipo in ['pdf', 'docx', 'txt']:
        if f'- {tipo}' in nombre or f'_{tipo}' in nombre:
            return tipo
    return 'desconocido'

def analizar_archivo(path):
    defectos = []
    texto = ""
    tipo = deducir_tipo(path)

    if tipo == 'pdf':
        texto = extraer_texto_pdf(path)
        if texto is None:
            defectos.append("no se pudo extraer texto del PDF")
            return tipo, defectos, texto
    elif tipo == 'docx':
        texto = extraer_texto_docx(path)
        if texto is None:
            defectos.append("no se pudo extraer texto del DOCX")
            return tipo, defectos, texto
    else:
        texto = extraer_texto_txt(path)
        if texto is None:
            defectos.append("no se pudo abrir o decodificar como texto")
            return tipo, defectos, texto

    if not texto.strip():
        defectos.append('vacío o solo espacios')
    if len(texto) < MIN_CARACTERES:
        defectos.append(f'muy corto (<{MIN_CARACTERES} caracteres)')
    if not es_legible(texto):
        defectos.append('texto ilegible (muchos caracteres no imprimibles)')

    return tipo, defectos, texto

# Recorrido
print("📂 Analizando archivos en RESOLUCIONES...\n")
for root, _, files in os.walk(RUTA_BASE):
    for file in files:
        path = os.path.join(root, file)
        
        # Eliminar archivos .DS_Store directamente
        if file == '.DS_Store':
            try:
                os.remove(path)
                print(f"🗑️  Eliminado archivo oculto: {path}")
            except Exception as e:
                print(f"❌ Error al eliminar {path}: {e}")
            continue  # saltar al siguiente archivo
        
        tipo, defectos, texto = analizar_archivo(path)
        if defectos:
            resultados_por_tipo[tipo].append((path, defectos, texto[:1000]))  # mostramos hasta 1000 caracteres para revisar
            # Aquí eliminamos solo los .docx ilegibles (o con defectos)
            if tipo == 'docx':
                try:
                    os.remove(path)
                    print(f"🗑️  Eliminado archivo DOCX ilegible: {path}")
                except Exception as e:
                    print(f"❌ Error al eliminar {path}: {e}")


# Mostrar resultados
for tipo in sorted(resultados_por_tipo):
    print(f"\n📄 Archivos con errores (tipo: {tipo}):")
    for path, defectos, preview in resultados_por_tipo[tipo]:
        print(f'⚠️  {path}')
        for d in defectos:
            print(f'   - {d}')
        print("   ↪ Vista previa del texto extraído:")
        print("   --------------------------------------------------")
        print(preview.replace('\n', '\n   '))
        print("   --------------------------------------------------\n")
