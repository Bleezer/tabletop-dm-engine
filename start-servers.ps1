# MAGUS DM Engine — szerverek indítása / újraindítása
# Használat: jobbklikk → "Run with PowerShell"
#            vagy terminálból: .\start-servers.ps1

$PYTHON = "C:\Users\Eylon\AppData\Local\Programs\Python\Python312\python.exe"
$ROOT   = $PSScriptRoot

Write-Host "Leállítom a régi folyamatokat..." -ForegroundColor Yellow
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

Write-Host "Backend indítása (port 8000)..." -ForegroundColor Cyan
Start-Process -FilePath $PYTHON `
    -ArgumentList "-m", "uvicorn", "api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" `
    -WorkingDirectory $ROOT `
    -RedirectStandardOutput "$ROOT\backend.log" `
    -RedirectStandardError  "$ROOT\backend.err" `
    -WindowStyle Hidden

Write-Host "Frontend indítása (port 5173)..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" `
    -ArgumentList "/c", "cd /d `"$ROOT\frontend`" && npm run dev >> `"$ROOT\frontend.log`" 2>&1" `
    -WindowStyle Hidden

Write-Host "Várakozás..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Ellenőrzés
try {
    $r = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "Backend: OK ($($r.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "Backend: NEM VÁLASZOL — nézd meg a backend.err fájlt" -ForegroundColor Red
}

try {
    $r = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 5 -UseBasicParsing
    Write-Host "Frontend: OK ($($r.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "Frontend: NEM VÁLASZOL — nézd meg a frontend.log fájlt" -ForegroundColor Red
}

Write-Host ""
Write-Host "Backend log:  $ROOT\backend.err" -ForegroundColor Gray
Write-Host "App log:      $ROOT\logs\app.log" -ForegroundColor Gray
Write-Host "Claude log:   $ROOT\logs\claude.log" -ForegroundColor Gray
Write-Host ""
Write-Host "Nyomj Entert a bezáráshoz..."
Read-Host
