
import os
import re

# Ruta base
DOCS_PATH = 'RESOLUCIONES'

# Lista de patrones extendidos (se agregaron IC-037.09, R-000.24 y CDCIC-.06)
PATRONES = [
    re.compile(r'(?P<letras>[A-Z]{1,5})-(?P<num1>\d{3})[-\.](?P<num2>\d{2,4})', re.IGNORECASE),  # IC-037.09 o DCIC-001.21
    re.compile(r'(?P<letras>[A-Z]{3,5})[-\.](?P<letras2>[A-Z]{2,4})[-\.](?P<num>\d{1,4})', re.IGNORECASE),  # DCIC.DGEF-0
    re.compile(r'(?P<letras1>[A-Z]{1})-(?P<letras2>[A-Z]{3})[-\.](?P<num>\d{2,4})', re.IGNORECASE),  # A-BCD.23
    re.compile(r'(?P<letras>[A-Z]{3,5})[-\.](?P<num1>\d{1,4})[-\.](?P<num2>\d{1,4})', re.IGNORECASE),  # ABCD.12.34
    re.compile(r'(?P<letras>[A-Z]{3,5})[-\.](?P<num1>\d{1,4})', re.IGNORECASE),  # ABCD.12
    re.compile(r'(?P<letras>[A-Z]{3,5})\s+(?P<num1>\d{3})[-\.](?P<num2>\d{2,4})', re.IGNORECASE),  # DCIC 008-22
    re.compile(r'(?P<letras>[A-Z]{3,5})-?\s*(?P<num1>\d{3})[-\.]{1,2}(?P<num2>\d{2,4})', re.IGNORECASE),  # CDCIC- 285.24
    re.compile(r'(?P<letras>[A-Z]{1,2})-(?P<num1>\d{3})[-\.](?P<num2>\d{2})', re.IGNORECASE),  # IC-037.09 y R-000.24
    re.compile(r'(?P<letras>[A-Z]{3,5})-\.(?P<num1>\d{2,4})', re.IGNORECASE),  # CDCIC-.06
]

formatos_detectados = set()
sin_patron = []

def determinar_formato(match, patron):
    formato = match.group(0)
    formato = re.sub(r'[A-Z]', 'X', formato)
    formato = re.sub(r'\d', 'N', formato)
    return formato

# Recorrer archivos
for root, _, files in os.walk(DOCS_PATH):
    for file in files:
        if not file.lower().endswith(('.docx', '.pdf')):
            continue

        matched = False
        for patron in PATRONES:
            match = patron.search(file)
            if match:
                formato = determinar_formato(match, patron)
                formatos_detectados.add(formato)
                matched = True
                break

        if not matched:
            sin_patron.append(os.path.join(root, file))

# Mostrar resultados
print("📄 Formatos detectados en nombres de archivos:\n")
if formatos_detectados:
    for formato in sorted(formatos_detectados):
        print(f"✅ {formato}")
else:
    print("❌ No se detectó ningún archivo con formato conocido.")

print("\n📂 Archivos sin patrón reconocido:\n")
if sin_patron:
    for path in sin_patron:
        print(f"• {path}")
else:
    print("✅ Todos los archivos tienen algún patrón reconocido.")
