$ErrorActionPreference = "Stop"

Write-Host "Uruchamianie PostgreSQL..."
docker compose up -d --wait db
if ($LASTEXITCODE -ne 0) {
    throw "Nie udalo sie uruchomic PostgreSQL."
}

Write-Host "Uruchamianie backendu..."
python .\run.py
