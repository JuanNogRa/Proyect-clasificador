@echo off
setlocal EnableExtensions

cd /d "%~dp0.."

set "CONDA_ROOT="
if exist "%USERPROFILE%\Documents\Miniconda\Scripts\conda.exe" set "CONDA_ROOT=%USERPROFILE%\Documents\Miniconda"
if not defined CONDA_ROOT if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" set "CONDA_ROOT=%USERPROFILE%\miniconda3"
if not defined CONDA_ROOT if exist "%USERPROFILE%\Miniconda3\Scripts\conda.exe" set "CONDA_ROOT=%USERPROFILE%\Miniconda3"
if not defined CONDA_ROOT if exist "%LOCALAPPDATA%\miniconda3\Scripts\conda.exe" set "CONDA_ROOT=%LOCALAPPDATA%\miniconda3"

if not defined CONDA_ROOT (
    where conda >nul 2>nul
    if not errorlevel 1 (
        for /f "delims=" %%i in ('where conda') do set "CONDA_EXE=%%i" & goto :found_conda_in_path
    )
    echo [ERROR] No se encontro Miniconda/Anaconda.
    echo Instala Miniconda o agrega conda al PATH con: conda init powershell
    exit /b 1
)

set "PYTHON_EXE=%CONDA_ROOT%\python.exe"
goto :run

:found_conda_in_path
call conda activate base
if errorlevel 1 exit /b 1
set "PYTHON_EXE=python"
goto :run

:run
echo Usando Python:
"%PYTHON_EXE%" --version
echo.
echo API en http://localhost:8000
"%PYTHON_EXE%" scripts\run_api.py
