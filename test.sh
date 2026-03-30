#!/bin/bash
# Unified Test Script for Architecture Intelligence

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
PYTHON_EXE="$BACKEND_DIR/venv/bin/python"

# Colors
CYAN='\033[0;36m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Track exit codes
BACKEND_EXIT=0
FRONTEND_EXIT=0

echo -e "\n${CYAN}=== [1/3] Running Backend & AI Tests ===${NC}"
if [ -f "$PYTHON_EXE" ]; then
    cd "$BACKEND_DIR"
    "$PYTHON_EXE" -m pytest tests/ -v || BACKEND_EXIT=$?
else
    echo -e "${RED}ERROR: Backend venv not found! Run ./dev.sh setup first.${NC}"
    BACKEND_EXIT=1
fi

echo -e "\n${CYAN}=== [2/3] Running Frontend Tests ===${NC}"
cd "$FRONTEND_DIR"
if [ -d "node_modules" ]; then
    npm run test -- --run || FRONTEND_EXIT=$?
else
    echo -e "${RED}ERROR: Frontend node_modules not found! Run npm install first.${NC}"
    FRONTEND_EXIT=1
fi

echo -e "\n${GREEN}=== [3/3] Testing Complete ===${NC}"
cd "$PROJECT_ROOT"
