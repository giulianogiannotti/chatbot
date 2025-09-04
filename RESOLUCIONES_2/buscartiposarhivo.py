import os
from collections import defaultdict

# Ruta base
DOCS_PATH = '/content/drive/My Drive/RESOLUCIONES_2/RESOLUCIONES'

# Extensiones permitidas
permitidas = ['.docx', '.pdf']

# Diccionario para agrupar archivos por extensión
archivos_a_borrar = defaultdict(list)

# Recorrer archivos
for root, _, files in os.walk(DOCS_PATH):
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext and ext not in permitidas:
            full_path = os.path.join(root, file)
            archivos_a_borrar[ext].append(full_path)

# Mostrar y borrar
if archivos_a_borrar:
    print("🗑️ Archivos a borrar por extensión no permitida:\n")
    for ext in sorted(archivos_a_borrar):
        print(f"🔸 Extensión: {ext} ({len(archivos_a_borrar[ext])} archivos)")
        for file_path in archivos_a_borrar[ext]:
            print(f"    → Borrando: {file_path}")
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"    ❌ Error al borrar {file_path}: {e}")
        print()
    print("✅ Eliminación finalizada.")
else:
    print("✅ No se encontraron archivos con extensiones distintas de .docx y .pdf.")
