@echo off
setlocal EnableExtensions

cd /d "%~dp0.."

set "CONDA_ROOT="
if exist "%USERPROFILE%\Documents\Miniconda\Scripts\conda.exe" set "CONDA_ROOT=%USERPROFILE%\Documents\Miniconda"
if not defined CONDA_ROOT if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" set "CONDA_ROOT=%USERPROFILE%\miniconda3"
if not defined CONDA_ROOT if exist "%USERPROFILE%\Miniconda3\Scripts\conda.exe" set "CONDA_ROOT=%USERPROFILE%\Miniconda3"

if defined CONDA_ROOT (
    set "PATH=%CONDA_ROOT%;%CONDA_ROOT%\Scripts;%CONDA_ROOT%\Library\bin;%PATH%"
)

set FLASK_APP=app
echo API Flask en http://localhost:8000
flask --app app run --host 0.0.0.0 --port 8000
