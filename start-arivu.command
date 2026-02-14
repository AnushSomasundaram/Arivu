#!/bin/bash
# ─── Arivu Launcher ──────────────────────────────────────────────────────────
# Double-click this file or run it from terminal.
# Starts the backend + frontend, opens the app, and cleans up on close.
# ─────────────────────────────────────────────────────────────────────────────

cd "$(dirname "$0")"

BACKEND_DIR="./Arivu/Backend"
FRONTEND_DIR="./Arivu/Frontend/vue-project"
PYTHON="$BACKEND_DIR/.venv/bin/python"

# Port configuration (can be overridden by environment variables)
BACKEND_PORT="${ARIVU_BACKEND_PORT:-8000}"
BACKEND_HOST="${ARIVU_BACKEND_HOST:-127.0.0.1}"
FRONTEND_PORT="${VITE_PORT:-5173}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down Arivu...${NC}"
    [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null && echo "  ✓ Backend stopped"
    [ -n "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null && echo "  ✓ Frontend stopped"
    # Kill any child processes
    jobs -p | xargs kill 2>/dev/null
    echo -e "${GREEN}Arivu stopped.${NC}"
    exit 0
}

trap cleanup EXIT INT TERM

echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}         🧠 Arivu - Starting Up        ${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""

# ── Check prerequisites ──────────────────────────────────────────────────────
if [ ! -f "$PYTHON" ]; then
    echo -e "${RED}ERROR: Python venv not found at $PYTHON${NC}"
    echo "Run: cd $BACKEND_DIR && python3 -m venv .venv && .venv/bin/pip install -e ."
    read -p "Press Enter to exit..."
    exit 1
fi

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${RED}ERROR: Frontend node_modules not found${NC}"
    echo "Run: cd $FRONTEND_DIR && npm install"
    read -p "Press Enter to exit..."
    exit 1
fi

# ── Start Backend ────────────────────────────────────────────────────────────
echo -e "${YELLOW}Starting backend server on ${BACKEND_HOST}:${BACKEND_PORT}...${NC}"
cd "$BACKEND_DIR"
.venv/bin/python -m uvicorn app.main:app --host "$BACKEND_HOST" --port "$BACKEND_PORT" &
BACKEND_PID=$!
cd - > /dev/null
echo -e "  Backend PID: $BACKEND_PID"

# ── Start Frontend ───────────────────────────────────────────────────────────
echo -e "${YELLOW}Starting frontend server on port ${FRONTEND_PORT}...${NC}"
cd "$FRONTEND_DIR"
npm run dev -- --port "$FRONTEND_PORT" &
FRONTEND_PID=$!
cd - > /dev/null
echo -e "  Frontend PID: $FRONTEND_PID"

# ── Wait for servers ─────────────────────────────────────────────────────────
echo ""
echo -e "${YELLOW}Waiting for servers to start...${NC}"
sleep 3

# ── Open in browser ──────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  ✓ Arivu is running!                  ${NC}"
echo -e "${GREEN}  Frontend: http://localhost:${FRONTEND_PORT}       ${NC}"
echo -e "${GREEN}  Backend:  http://${BACKEND_HOST}:${BACKEND_PORT}       ${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers.${NC}"
echo ""

open "http://localhost:${FRONTEND_PORT}"

# Keep script alive until user closes it
wait
