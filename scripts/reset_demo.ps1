Write-Host ""
Write-Host "=== Reset Demo Data ===" -ForegroundColor Yellow

docker exec timescaledb psql -U postgres -d fleetdb `
-c "TRUNCATE TABLE alerts; TRUNCATE TABLE telemetry;"

if (Test-Path "last_ws_alert.json") {
    Remove-Item "last_ws_alert.json"
    Write-Host "Deleted last_ws_alert.json" -ForegroundColor Green
}

Write-Host "Database cleaned." -ForegroundColor Green
Write-Host ""