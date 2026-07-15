# Verifie que tout ce dont ThreatFusion a besoin est installe sur la machine.
# Usage : powershell -ExecutionPolicy Bypass -File scripts/check_dependencies.ps1

$ErrorActionPreference = "SilentlyContinue"
$fail = $false

function Check-Command {
    param($Name, $Command)
    try {
        $result = Invoke-Expression $Command 2>&1
        if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq $null) {
            Write-Host "[OK]   $Name" -ForegroundColor Green
        } else {
            Write-Host "[MANQUANT] $Name" -ForegroundColor Red
            $script:fail = $true
        }
    } catch {
        Write-Host "[MANQUANT] $Name" -ForegroundColor Red
        $script:fail = $true
    }
}

Write-Host "== Outils systeme =="
Check-Command "Docker installe"           "docker --version"
Check-Command "Docker daemon actif"       "docker info"
Check-Command "Docker Compose disponible" "docker compose version"
Check-Command "Node.js installe"          "node --version"
Check-Command "npm installe"              "npm --version"

$pyVersion = python --version 2>&1
if ($pyVersion -match "Python 3\.(1[0-9]|[2-9][0-9])") {
    Write-Host "[OK]   Python >= 3.10 ($pyVersion)" -ForegroundColor Green
} else {
    Write-Host "[ATTENTION] Version Python detectee : $pyVersion (3.10+ recommande)" -ForegroundColor Yellow
    $fail = $true
}

Write-Host ""
Write-Host "== Dependances Python (backend) =="
if (Test-Path "backend\requirements.txt") {
    Write-Host "[OK]   backend/requirements.txt trouve"
    Write-Host "       -> pour installer : cd backend; pip install -r requirements-dev.txt"
} else {
    Write-Host "[MANQUANT] backend/requirements.txt introuvable" -ForegroundColor Red
    $fail = $true
}

Write-Host ""
Write-Host "== Dependances Node (frontend) =="
if (Test-Path "frontend\package.json") {
    Write-Host "[OK]   frontend/package.json trouve"
    Write-Host "       -> pour installer : cd frontend; npm install"
} else {
    Write-Host "[MANQUANT] frontend/package.json introuvable" -ForegroundColor Red
    $fail = $true
}

Write-Host ""
if (-not $fail) {
    Write-Host "Tout est pret." -ForegroundColor Green
} else {
    Write-Host "Certains elements manquent - installe-les avant de lancer 'docker compose up'." -ForegroundColor Yellow
}
