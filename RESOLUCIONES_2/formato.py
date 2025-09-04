import os
import re

# Ruta base
DOCS_PATH = 'RESOLUCIONES'

# Patrón: letras (3, 4 o 5), guion, 3 números, punto, 2 números (ej. DCIC-005.11 o CDCIC-015.13)
pattern = re.compile(r'[A-Z]{3,5}-\d{3}\.\d{2}')

# Recorrer todos los archivos .docx y .pdf dentro de RESOLUCIONES
for root, _, files in os.walk(DOCS_PATH):
    for filename in files:
        if filename.lower().endswith(('.pdf', '.docx')):
            if not pattern.search(filename):
                # Si el nombre del archivo NO contiene el patrón deseado, imprimir
                print("❌ Sin patrón esperado:", os.path.join(root, filename))
