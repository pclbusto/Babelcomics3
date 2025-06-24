#!/bin/bash

# Obtiene la ruta absoluta del directorio donde se encuentra el script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Cambia al directorio del proyecto. Esto es crucial para que tu app encuentre
# los archivos relativos como las imágenes.
cd "$DIR"

# Activa el entorno virtual
source .venv/bin/activate

# Ejecuta tu aplicación con el python del entorno virtual
python3 main.py