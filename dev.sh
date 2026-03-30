#!/usr/bin/env bash
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

DB_URL_DEFAULT="postgresql://postgres:postgres@localhost:5432/architecture_intelligence"
GROQ_API_KEY_DEFAULT="gsk_..."

usage() {
  echo "Usage: $0 {setup|backend|frontend|dev|init-db}"
  echo
  echo "  setup    - Backend-venv + pip install, Docker-DB und Frontend-Dependencies vorbereiten"
  echo "  backend  - Backend-Server (FastAPI/uvicorn) starten"
  echo "  frontend - Frontend (Nuxt) starten"
  echo "  dev      - Backend und Frontend gemeinsam im Dev-Modus starten"
  echo "  init-db  - Datenbank mit Test-/Initialdaten befüllen (backend.init_db)"
}

ensure_db_url() {
  if [ -z "$DATABASE_URL" ]; then
    export DATABASE_URL="$DB_URL_DEFAULT"
    echo "INFO: DATABASE_URL war nicht gesetzt, verwende Default:"
    echo "      $DATABASE_URL"
  fi
}

ensure_groq_api_key() {
  if [ -z "$GROQ_API_KEY" ]; then
    export GROQ_API_KEY="$GROQ_API_KEY_DEFAULT"
    echo "INFO: GROQ_API_KEY war nicht gesetzt, verwende lokalen Default."
  fi
}

ensure_docker_up() {
  if command -v docker >/dev/null 2>&1; then
    if command -v docker compose >/dev/null 2>&1; then
      docker compose up -d
    else
      docker-compose up -d
    fi
  else
    echo "WARN: Docker wurde nicht gefunden. Bitte Docker Desktop starten/installieren."
  fi
}

case "$1" in
  setup)
    echo "=== Setup: Backend-venv und Abhängigkeiten installieren ==="
    cd "$BACKEND_DIR"

    if [ ! -d "venv" ]; then
      echo "Erstelle Python-venv..."
      python3 -m venv venv
    else
      echo "venv existiert bereits, verwende bestehende Umgebung."
    fi

    ./venv/bin/python -m pip install --upgrade pip
    ./venv/bin/python -m pip install -r requirements.txt

    cd "$PROJECT_ROOT"
    echo "=== Setup: Docker-Datenbank starten ==="
    ensure_db_url
    ensure_docker_up

    echo "=== Setup: Frontend-Dependencies installieren (Yarn) ==="
    cd "$FRONTEND_DIR"
    corepack enable || true
    corepack.prepare() { :; }
    corepack prepare yarn@1.22.22 --activate || true
    yarn install

    echo "Setup abgeschlossen."
    ;;

  backend)
    echo "=== Starte Backend ==="
    if [ ! -d "$BACKEND_DIR/venv" ]; then
      echo "ERROR: venv nicht gefunden. Bitte zuerst '$0 setup' ausführen."
      exit 1
    fi

    ensure_db_url
    ensure_groq_api_key
    cd "$PROJECT_ROOT"
    ensure_docker_up

    echo "[Backend] Starte uvicorn..."
    "$BACKEND_DIR/venv/bin/python" -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
    ;;

  frontend)
    echo "=== Starte Frontend ==="
    cd "$FRONTEND_DIR"

    corepack enable || true
    corepack prepare yarn@1.22.22 --activate || true

    if [ ! -d "node_modules" ]; then
      echo "[Frontend] node_modules fehlt, führe yarn install aus..."
      yarn install
    fi

    yarn dev
    ;;

  dev)
    echo "=== Starte Backend & Frontend im Dev-Modus ==="
    ensure_db_url
    ensure_groq_api_key
    cd "$PROJECT_ROOT"
    ensure_docker_up

    (
      cd "$PROJECT_ROOT"
      echo "[Backend] Starte uvicorn..."
      "$BACKEND_DIR/venv/bin/python" -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
    ) &
    BACKEND_PID=$!

    (
      cd "$FRONTEND_DIR"
      corepack.enable() { :; }
      corepack enable || true
      corepack prepare yarn@1.22.22 --activate || true
      if [ ! -d "node_modules" ]; then
        echo "[Frontend] node_modules fehlt, führe yarn install aus..."
        yarn install
      fi
      echo "[Frontend] Starte yarn dev..."
      yarn dev
    ) &
    FRONTEND_PID=$!

    echo "Backend PID:  $BACKEND_PID"
    echo "Frontend PID: $FRONTEND_PID"
    echo "Zum Beenden: STRG+C drücken."

    wait $BACKEND_PID $FRONTEND_PID
    ;;

  init-db)
    echo "=== Fülle Datenbank mit Initial-/Testdaten (backend.core.init_db) ==="
    ensure_db_url
    ensure_groq_api_key
    cd "$PROJECT_ROOT"
    ensure_docker_up

    if [ ! -d "$BACKEND_DIR/venv" ]; then
      echo "ERROR: venv nicht gefunden. Bitte zuerst '$0 setup' ausführen."
      exit 1
    fi

    "$BACKEND_DIR/venv/bin/python" -m backend.core.init_db
    echo "Init-DB abgeschlossen."
    ;;

  *)
    usage
    exit 1
    ;;
esac