import os
from collections import Counter

# Ruta a la carpeta "Resoluciones" (asegúrate de que esté en el mismo directorio que este script o cambia el path)
CARPETA_BASE = "RESOLUCIONES"

# Contador de extensiones
extensiones = Counter()

# Recorrer todos los archivos dentro de la carpeta y subcarpetas
for root, _, files in os.walk(CARPETA_BASE):
    for archivo in files:
        _, extension = os.path.splitext(archivo)
        if extension:
            extension = extension.lower()
            extensiones[extension] += 1
        else:
            extensiones["(sin extensión)"] += 1

# Mostrar resultados
print(f"Análisis de tipos de archivo en la carpeta '{CARPETA_BASE}':\n")
for extension, cantidad in extensiones.most_common():
    print(f"{extension}: {cantidad} archivo(s)")