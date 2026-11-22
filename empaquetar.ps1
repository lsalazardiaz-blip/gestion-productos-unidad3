$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $MyInvocation.MyCommand.Path
$entregas = Join-Path $raiz "entregas"
New-Item -ItemType Directory -Force -Path $entregas | Out-Null
$anterior = Join-Path $entregas "gestion_productos_unidad3.zip"
if (Test-Path $anterior) {
    Remove-Item $anterior -Force
}
$zip = Join-Path $entregas "Salazar_Luis_Proyecto_Unidad3.zip"
if (Test-Path $zip) {
    Remove-Item $zip -Force
}
$informe = Join-Path (Split-Path -Parent $raiz) "Salazar_Luis_Trabajo_Unidad3.docx"
if (-not (Test-Path $informe)) {
    throw "No está el informe: $informe"
}
Copy-Item $informe (Join-Path $entregas "Salazar_Luis_Trabajo_Unidad3.docx") -Force

Push-Location $raiz
try {
    tar -a -c -f $zip `
        --exclude .venv `
        --exclude entregas `
        --exclude __pycache__ `
        --exclude db.sqlite3 `
        --exclude .env `
        --exclude Apellido_Nombre_Trabajo_Unidad3.docx `
        --exclude INFORME.md `
        --exclude captura.log `
        --exclude estado.json `
        .
}
finally {
    Pop-Location
}

Write-Output "Informe: $(Join-Path $entregas 'Salazar_Luis_Trabajo_Unidad3.docx')"
Write-Output "Proyecto: $zip"
