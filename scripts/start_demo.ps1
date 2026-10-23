Write-Host ""
Write-Host "=== Starting IoT Fleet Stream Engine ===" `
-ForegroundColor Yellow

Write-Host ""
Write-Host "Starting Docker services..." `
-ForegroundColor Cyan

docker compose up -d

Write-Host ""
Write-Host "Waiting for containers..." `
-ForegroundColor Cyan

Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Starting FastAPI..." `
-ForegroundColor Cyan

Start-Process powershell `
-ArgumentList '-NoExit', `
'-Command', `
'.\.venv\Scripts\Activate.ps1; uvicorn src.main:app --reload'

Write-Host ""
Write-Host "Starting Consumer..." `
-ForegroundColor Cyan

Start-Process powershell `
-ArgumentList '-NoExit', `
'-Command', `
'.\.venv\Scripts\Activate.ps1; py -m src.consumer'

Write-Host ""
Write-Host "Waiting for API startup..." `
-ForegroundColor Cyan

Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Starting Producer..." `
-ForegroundColor Cyan

Start-Process powershell `
-ArgumentList '-NoExit', `
'-Command', `
'.\.venv\Scripts\Activate.ps1; py -m src.producer'

Write-Host ""
Write-Host "Waiting for telemetry generation..." `
-ForegroundColor Cyan

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Starting Streamlit..." `
-ForegroundColor Cyan

Start-Process powershell `
-ArgumentList '-NoExit', `
'-Command', `
'.\.venv\Scripts\Activate.ps1; streamlit run src/dashboard.py'

Write-Host ""
Write-Host "======================================" `
-ForegroundColor Green
Write-Host "Project started successfully." `
-ForegroundColor Green
Write-Host ""
Write-Host "Dashboard : http://localhost:8501"
Write-Host "Swagger   : http://localhost:8000/docs"
Write-Host ""
