#!/bin/bash

echo "========================================"
echo "OmniVoIP Frontend - Instalación Rápida"
echo "========================================"
echo ""

# Verificar si Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js no está instalado."
    echo ""
    echo "Por favor descarga e instala Node.js desde:"
    echo "https://nodejs.org/"
    echo ""
    echo "Recomendado: Node.js 18 LTS o superior"
    exit 1
fi

echo "[OK] Node.js version:"
node --version
echo ""

echo "[OK] npm version:"
npm --version
echo ""

echo "========================================"
echo "Paso 1: Instalando dependencias..."
echo "========================================"
npm install
if [ $? -ne 0 ]; then
    echo "[ERROR] Error al instalar dependencias"
    exit 1
fi

echo ""
echo "========================================"
echo "Paso 2: Configurando variables de entorno..."
echo "========================================"

if [ ! -f .env ]; then
    cp .env.example .env
    echo "[OK] Archivo .env creado desde .env.example"
    echo ""
    echo "IMPORTANTE: Edita el archivo .env con tu configuración"
    echo "Por defecto apunta a:"
    echo "  - API: http://localhost:8000"
    echo "  - WebSocket: ws://localhost:8000"
    echo ""
else
    echo "[INFO] El archivo .env ya existe"
fi

echo ""
echo "========================================"
echo "Instalación completada con éxito!"
echo "========================================"
echo ""
echo "Para iniciar el servidor de desarrollo:"
echo "  npm run dev"
echo ""
echo "Para compilar para producción:"
echo "  npm run build"
echo ""
echo "Asegúrate de que el backend Django esté ejecutándose en:"
echo "  http://localhost:8000"
echo ""
