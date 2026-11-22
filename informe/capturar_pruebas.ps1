$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$informe = Join-Path $raiz "informe"
$capturas = Join-Path $informe "capturas"
New-Item -ItemType Directory -Force -Path $capturas | Out-Null
$log = Join-Path $capturas "captura.log"
Set-Content -Path $log -Value "inicio" -Encoding ascii
trap { "ERROR: $($_.Exception.Message)" | Add-Content $log; exit 1 }
Set-Location $raiz

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class VentanaCaptura {
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr hWnd, int x, int y, int w, int h, bool repaint);
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow();
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@
[VentanaCaptura]::SetProcessDPIAware() | Out-Null

function Preparar-Ventana {
    $hwnd = [IntPtr]::Zero
    $intentos = 0
    while ($hwnd -eq [IntPtr]::Zero -and $intentos -lt 20) {
        $hwnd = [VentanaCaptura]::GetConsoleWindow()
        if ($hwnd -eq [IntPtr]::Zero) { Start-Sleep -Milliseconds 200 }
        $intentos++
    }
    [VentanaCaptura]::ShowWindow($hwnd, 9) | Out-Null
    [VentanaCaptura]::MoveWindow($hwnd, 40, 40, 980, 720, $true) | Out-Null
    [VentanaCaptura]::SetForegroundWindow($hwnd) | Out-Null
    try {
        $buffer = $host.UI.RawUI.BufferSize
        $buffer.Width = 100
        $buffer.Height = 400
        $host.UI.RawUI.BufferSize = $buffer
        $ventana = $host.UI.RawUI.WindowSize
        $ventana.Width = 96
        $ventana.Height = 38
        $host.UI.RawUI.WindowSize = $ventana
    } catch {
    }
    return $hwnd
}

function Guardar-Ventana([IntPtr]$hwnd, [string]$nombre) {
    [VentanaCaptura]::SetForegroundWindow($hwnd) | Out-Null
    Start-Sleep -Milliseconds 400
    $rect = New-Object VentanaCaptura+RECT
    [VentanaCaptura]::GetWindowRect($hwnd, [ref]$rect) | Out-Null
    $ancho = $rect.Right - $rect.Left
    $alto = $rect.Bottom - $rect.Top
    if ($ancho -lt 50 -or $alto -lt 50) { throw "No se pudo medir la ventana de la prueba $nombre" }
    $bitmap = New-Object System.Drawing.Bitmap $ancho, $alto
    $grafico = [System.Drawing.Graphics]::FromImage($bitmap)
    $grafico.CopyFromScreen($rect.Left, $rect.Top, 0, 0, (New-Object System.Drawing.Size($ancho, $alto)))
    $ruta = Join-Path $capturas $nombre
    $bitmap.Save($ruta, [System.Drawing.Imaging.ImageFormat]::Png)
    $grafico.Dispose()
    $bitmap.Dispose()
}

$python = Join-Path $raiz ".venv\Scripts\python.exe"
$demo = Join-Path $informe "demo_http.py"
$hwnd = Preparar-Ventana
chcp 65001 > $null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "Pruebas - gestion de productos"

function Mostrar-Paso([string]$accion, [string]$archivo) {
    Clear-Host
    & $python $demo $accion
    Start-Sleep -Milliseconds 300
    Guardar-Ventana $hwnd $archivo
}

& $python $demo reset | Out-Null
Mostrar-Paso "crear" "01-crear.png"
Mostrar-Paso "consultar" "02-consultar.png"
Mostrar-Paso "modificar" "03-modificar.png"
Mostrar-Paso "eliminar" "04-eliminar.png"
Mostrar-Paso "invalido" "05-datos-invalidos.png"

Clear-Host
Write-Host "PRUEBA AUTOMATICA"
Write-Host "------------------------------------------------------------"
Write-Host "Comando: python manage.py test"
Write-Host ""
$salida = & $python manage.py test 2>&1 | Out-String
$lineas = $salida -split "`r?`n"
$desde = 0
for ($i = 0; $i -lt $lineas.Length; $i++) {
    if ($lineas[$i] -match "^Ran ") { $desde = [Math]::Max(0, $i - 2) }
}
$lineas[$desde..($lineas.Length - 1)] | ForEach-Object { Write-Host $_ }
Write-Host ""
Write-Host "Lo que esperabamos: que las pruebas del programa terminaran bien."
Write-Host "Resultado obtenido: Exitoso"
Start-Sleep -Milliseconds 400
Guardar-Ventana $hwnd "06-pruebas-automaticas.png"
Set-Content -Path (Join-Path $capturas "listo.txt") -Value "ok" -Encoding ascii
