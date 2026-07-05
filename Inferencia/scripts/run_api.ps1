# Levanta la API Flask con Miniconda base (sin necesitar conda en PATH)
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

$candidates = @(
    (Join-Path $env:USERPROFILE "Documents\Miniconda"),
    (Join-Path $env:USERPROFILE "miniconda3"),
    (Join-Path $env:USERPROFILE "Miniconda3"),
    (Join-Path $env:LOCALAPPDATA "miniconda3")
)

$condaRoot = $null
foreach ($path in $candidates) {
    if (Test-Path (Join-Path $path "python.exe")) {
        $condaRoot = $path
        break
    }
}

if ($condaRoot) {
    $pythonExe = Join-Path $condaRoot "python.exe"
} elseif (Get-Command conda -ErrorAction SilentlyContinue) {
    conda activate base
    if ($LASTEXITCODE -ne 0) { throw "No se pudo activar conda base." }
    $pythonExe = "python"
} else {
    throw @"
No se encontro Miniconda. Rutas buscadas:
  $($candidates -join "`n  ")

Solucion: agrega conda al PATH ejecutando una vez:
  & `"$env:USERPROFILE\Documents\Miniconda\Scripts\conda.exe`" init powershell
Luego reinicia la terminal.
"@
}

Write-Host "Usando Python: $pythonExe"
& $pythonExe --version
Write-Host ""
Write-Host "API en http://localhost:8000"
& $pythonExe scripts/run_api.py
