#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Uso: $0 URL [directorio_salida]"
    exit 1
fi

URL=$1
OUTPUT_DIR=${2:-"website"}

# Crear directorio si no existe
mkdir -p "$OUTPUT_DIR"

# Descargar el sitio web
wget \
    --recursive \
    --no-clobber \
    --page-requisites \
    --html-extension \
    --convert-links \
    --restrict-file-names=windows \
    --domains $(echo "$URL" | awk -F/ '{print $3}') \
    --no-parent \
    -P "$OUTPUT_DIR" \
    "$URL"

echo "Sitio web descargado en $OUTPUT_DIR"