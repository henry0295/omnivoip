@echo off
echo ========================================
echo OmniVoIP Frontend - Instalacion Rapida
echo ========================================
echo.

REM Verificar si Node.js esta instalado
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js no esta instalado.
    echo.
    echo Por favor descarga e instala Node.js desde:
    echo https://nodejs.org/
    echo.
    echo Recomendado: Node.js 18 LTS o superior
    pause
    exit /b 1
)

echo [OK] Node.js version:
node --version
echo.

echo [OK] npm version:
npm --version
echo.

echo ========================================
echo Paso 1: Instalando dependencias...
echo ========================================
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Error al instalar dependencias
    pause
    exit /b 1
)

echo.
echo ========================================
echo Paso 2: Configurando variables de entorno...
echo ========================================

if not exist .env (
    copy .env.example .env
    echo [OK] Archivo .env creado desde .env.example
    echo.
    echo IMPORTANTE: Edita el archivo .env con tu configuracion
    echo Por defecto apunta a:
    echo   - API: http://localhost:8000
    echo   - WebSocket: ws://localhost:8000
    echo.
) else (
    echo [INFO] El archivo .env ya existe
)

echo.
echo ========================================
echo Instalacion completada con exito!
echo ========================================
echo.
echo Para iniciar el servidor de desarrollo:
echo   npm run dev
echo.
echo Para compilar para produccion:
echo   npm run build
echo.
echo Asegurate de que el backend Django este ejecutandose en:
echo   http://localhost:8000
echo.
pause
