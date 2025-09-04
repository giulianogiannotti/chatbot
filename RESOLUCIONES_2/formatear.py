import os
import re

# Ruta base
DOCS_PATH = 'RESOLUCIONES'

# Tabla de reemplazo de símbolos por letras
REEMPLAZOS = {
    '¢': 'o',
    'Ç': 'e',
    '°': 'i',
    '†': 'a',
    '§': 'ñ',
    '‡': 'o',
    '¯': '',
    '÷': 'i',
    '£': 'u'
}

def reemplazar_simbolos(texto):
    for simbolo, letra in REEMPLAZOS.items():
        texto = texto.replace(simbolo, letra)
    return texto

def corregir_errores_numericos_comunes(texto):
    # Corrige errores como OO7 → 007, O01 → 001, etc.
    return re.sub(r'(?<=[A-Z]-)O{2}(\d)', r'00\1', texto)

# Lista de patrones extendidos que queremos detectar
PATRONES = [
    re.compile(r'([A-Z]{1,5})[_\-\.\s]?(\d{3,4})[-\.]{1,2}(\d{2,4})', re.IGNORECASE),  # DCIC_032.21, DCIC-032.21, etc.
    re.compile(r'([A-Z]{1,5})\s(\d{3})[-\.](\d{2,4})', re.IGNORECASE),
    re.compile(r'~\$([A-Z]{2,5})-(\d{3})[.-](\d{2})', re.IGNORECASE),  # casos con ~$ al inicio
]

renamed_count = 0
folder_renamed_count = 0

# Paso 1: Renombrar archivos
for root, _, files in os.walk(DOCS_PATH):
    for original_filename in files:
        if original_filename.lower().endswith(('.pdf', '.docx')):
            old_path = os.path.join(root, original_filename)

        # --- Paso 1.1: Reemplazar símbolos
        clean_filename = reemplazar_simbolos(original_filename)

        # --- Paso 1.2: Corregir errores numéricos (como OO7 → 007)
        fixed_filename = corregir_errores_numericos_comunes(clean_filename)

        # Renombrar si hubo cambios en alguna de las dos etapas
        if fixed_filename != original_filename:
            fixed_path = os.path.join(root, fixed_filename)
            try:
                os.rename(old_path, fixed_path)
                old_path = fixed_path  # actualizamos la ruta para el siguiente paso
                print(f"🔤 Corrección:\n→ {original_filename}\n→ {fixed_filename}\n")
            except Exception as e:
                print(f"❌ Error al renombrar (símbolos o números) {original_filename}: {e}")
                continue

        new_filename = fixed_filename

        # Paso 1.3: Normalizar patrones en el nombre del archivo
        for patron in PATRONES:
            match = patron.search(new_filename)
            if match:
                letras = match.group(1).upper()
                parte1 = match.group(2).zfill(3)
                parte2 = match.group(3).zfill(2)

                nuevo_prefijo = f"{letras}-{parte1}.{parte2}"

                resto = patron.sub('', new_filename, count=1).strip(" -_.")

                separador = " - " if resto else ""
                nuevo_nombre = f"{nuevo_prefijo}{separador}{resto}"
                new_path = os.path.join(root, nuevo_nombre)

                try:
                    os.rename(old_path, new_path)
                    renamed_count += 1
                    print(f"✅ Renombrado final:\n→ {new_filename}\n→ {nuevo_nombre}\n")
                    break
                except Exception as e:
                    print(f"❌ Error al renombrar final {new_filename}: {e}")
                    break

# Paso 2: Renombrar carpetas
for current_root, dirs, _ in os.walk(DOCS_PATH, topdown=False):
    for dirname in dirs:
        new_dirname = reemplazar_simbolos(dirname)
        old_dir_path = os.path.join(current_root, dirname)
        new_dir_path = os.path.join(current_root, new_dirname)
        if new_dirname != dirname:
            try:
                os.rename(old_dir_path, new_dir_path)
                folder_renamed_count += 1
                print(f"📁 Carpeta renombrada:\n→ {dirname}\n→ {new_dirname}\n")
            except Exception as e:
                print(f"❌ Error al renombrar carpeta {dirname}: {e}")

# Paso 3: Eliminar carpetas vacías
empty_deleted = 0
for current_root, dirs, files in os.walk(DOCS_PATH, topdown=False):
    for dirname in dirs:
        dir_path = os.path.join(current_root, dirname)
        if not os.listdir(dir_path):
            try:
                os.rmdir(dir_path)
                empty_deleted += 1
                print(f"🗑️ Carpeta vacía eliminada: {dir_path}")
            except Exception as e:
                print(f"❌ Error al eliminar carpeta vacía {dir_path}: {e}")


# Paso 4: Corregir nombre de archivos con extensiones:
for root, _, files in os.walk(DOCS_PATH):
    for filename in files:
        # Buscar patrón de extensión precedida por ' - '
        match = re.search(r' - (docx|pdf|txt)$', filename, re.IGNORECASE)
        if match:
            ext = match.group(1).lower()
            nuevo_nombre = re.sub(r' - (docx|pdf|txt)$', f'.{ext}', filename, flags=re.IGNORECASE)
            old_path = os.path.join(root, filename)
            new_path = os.path.join(root, nuevo_nombre)
            try:
                os.rename(old_path, new_path)
                print(f"🔄 Cambiado nombre:\nAntes: {filename}\nDespués: {nuevo_nombre}\n")
            except Exception as e:
                print(f"❌ Error renombrando '{filename}': {e}")


print(f"\n🔁 Archivos renombrados: {renamed_count}")
print(f"📁 Carpetas renombradas: {folder_renamed_count}")
print(f"🗑️ Carpetas vacías eliminadas: {empty_deleted}")
