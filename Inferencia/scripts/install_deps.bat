@echo off
REM Instala dependencias de Inferencia en Miniconda base (una sola vez)
setlocal

set "CONDA_ROOT=%USERPROFILE%\Documents\Miniconda"
if not exist "%CONDA_ROOT%\python.exe" (
    echo [ERROR] No se encontro Miniconda en %CONDA_ROOT%
    exit /b 1
)

echo Instalando en: %CONDA_ROOT%
"%CONDA_ROOT%\python.exe" -m pip install -r "%~dp0..\requirements.txt"
echo.
echo Listo. Ejecuta: scripts\run_api.bat
