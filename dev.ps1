Param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("setup", "backend", "frontend", "dev", "init-db")]
    [string]$Command = "setup"
)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"

if (-not $env:DATABASE_URL) {
    $env:DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/architecture_intelligence"
    Write-Host "INFO: DATABASE_URL war nicht gesetzt. Verwende Default:"
    Write-Host "      $env:DATABASE_URL"
}

if (-not $env:GROQ_API_KEY) {
    $env:GROQ_API_KEY = "gsk_..."
    Write-Host "INFO: GROQ_API_KEY war nicht gesetzt. Verwende lokalen Default."
}

function Ensure-DockerUp {
    if (Get-Command "docker" -ErrorAction SilentlyContinue) {
        try {
            docker compose up -d
        } catch {
            docker-compose up -d
        }
    } else {
        Write-Host "WARN: Docker wurde nicht gefunden. Bitte Docker Desktop starten/installieren."
    }
}

switch ($Command) {
    "setup" {
        Write-Host "=== Setup: Backend-venv und Abhängigkeiten installieren ==="
        Set-Location $BackendDir

        if (-not (Test-Path "venv")) {
            Write-Host "Erstelle Python venv..."
            python -m venv venv
        } else {
            Write-Host "venv existiert bereits, verwende bestehende Umgebung."
        }

        & ".\venv\Scripts\python.exe" -m pip install --upgrade pip
        & ".\venv\Scripts\python.exe" -m pip install -r requirements.txt

        Set-Location $ProjectRoot
        Write-Host "=== Setup: Docker-Datenbank starten ==="
        Ensure-DockerUp

        Write-Host "=== Setup: Frontend-Dependencies installieren (Yarn) ==="
        Set-Location $FrontendDir
        corepack enable 2>$null
        corepack prepare yarn@1.22.22 --activate 2>$null
        yarn install

        Write-Host "Setup abgeschlossen."
    }

    "backend" {
        Write-Host "=== Starte Backend ==="
        if (-not (Test-Path (Join-Path $BackendDir "venv"))) {
            Write-Host "ERROR: venv nicht gefunden. Bitte zuerst '.\dev.ps1 -Command setup' ausführen."
            exit 1
        }

        Set-Location $ProjectRoot
        Ensure-DockerUp

        Write-Host "[Backend] Starte uvicorn..."
        & (Join-Path $BackendDir "venv\Scripts\python.exe") -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
    }

    "frontend" {
        Write-Host "=== Starte Frontend ==="
        Set-Location $FrontendDir
        corepack enable 2>$null
        corepack prepare yarn@1.22.22 --activate 2>$null

        if (-not (Test-Path "node_modules")) {
            Write-Host "[Frontend] node_modules fehlt, führe yarn install aus..."
            yarn install
        }

        yarn dev
    }

    "dev" {
        Write-Host "=== Starte Backend & Frontend im Dev-Modus ==="
        Set-Location $ProjectRoot
        Ensure-DockerUp

        $backendJob = Start-Job -ScriptBlock {
            param($ProjectRoot, $BackendDir)
            Set-Location $ProjectRoot
            & (Join-Path $BackendDir "venv\Scripts\python.exe") -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
        } -ArgumentList $ProjectRoot, $BackendDir

        Set-Location $FrontendDir
        corepack enable 2>$null
        corepack prepare yarn@1.22.22 --activate 2>$null

        if (-not (Test-Path "node_modules")) {
            Write-Host "[Frontend] node_modules fehlt, führe yarn install aus..."
            yarn install
        }

        Write-Host "[Frontend] Starte yarn dev..."
        yarn dev

        if ($backendJob -ne $null) {
            Receive-Job $backendJob -Wait -AutoRemoveJob | Out-Null
        }
    }

    "init-db" {
        Write-Host "=== Fülle Datenbank mit Initial-/Testdaten (backend.core.init_db) ==="

        Set-Location $ProjectRoot
        Ensure-DockerUp

        if (-not (Test-Path (Join-Path $BackendDir "venv"))) {
            Write-Host "ERROR: venv nicht gefunden. Bitte zuerst '.\dev.ps1 -Command setup' ausführen."
            exit 1
        }

        & (Join-Path $BackendDir "venv\Scripts\python.exe") -m backend.core.init_db

        Write-Host "Init-DB abgeschlossen."
    }
}