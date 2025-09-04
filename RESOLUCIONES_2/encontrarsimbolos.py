import os
import unicodedata

# --- Ruta raíz de búsqueda ---
ROOT_FOLDER = 'RESOLUCIONES'  # Cambiá esta ruta si hace falta

# --- Set para no repetir símbolos ---
simbolos_encontrados = {}

# --- Función para identificar caracteres raros ---
def es_simbolo_raro(c):
    return not (
        c.isalnum() or c in [' ', '.', '-', '_']
    )

# --- Recorrido recursivo ---
for dirpath, _, filenames in os.walk(ROOT_FOLDER):
    for filename in filenames:
        nombre_mayus = filename.upper()
        for char in nombre_mayus:
            if es_simbolo_raro(char) and char not in simbolos_encontrados:
                simbolos_encontrados[char] = os.path.join(dirpath, filename)

# --- Imprimir resultados ---
if simbolos_encontrados:
    print("Símbolos raros encontrados:")
    for simbolo, archivo in simbolos_encontrados.items():
        nombre_unicode = unicodedata.name(simbolo, "NOMBRE DESCONOCIDO")
        print(f"'{simbolo}' (U+{ord(simbolo):04X}) - {nombre_unicode} → en: {archivo}")
else:
    print("✅ No se encontraron símbolos raros en los nombres de archivo.")
