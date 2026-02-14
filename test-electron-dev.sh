#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Arivu Electron Development Mode Test Script
# ═══════════════════════════════════════════════════════════════════════════
# Tests the Electron app in development mode before packaging
# ═══════════════════════════════════════════════════════════════════════════

set -e

cd "$(dirname "$0")"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}  Testing Arivu in Electron Dev Mode   ${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

# ── Step 1: Build Electron Scripts ───────────────────────────────────────────
echo -e "${YELLOW}[1/3] Building Electron scripts...${NC}"
cd Arivu/Frontend/vue-project

npx vite build --config vite.config.electron.ts

if [ ! -d "electron/dist" ]; then
    echo -e "${RED}ERROR: Electron dist not found${NC}"
    exit 1
fi

echo -e "${GREEN}  ✓ Electron scripts built${NC}"
echo ""

# ── Step 2: Start Vite Dev Server in Background ──────────────────────────────
echo -e "${YELLOW}[2/3] Starting Vite dev server...${NC}"

# Kill any existing Vite server on port 5173
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

# Start Vite in background
npm run dev -- --port 5173 &
VITE_PID=$!

# Wait for Vite to be ready
echo "  Waiting for Vite dev server..."
sleep 5

if ! lsof -i:5173 > /dev/null; then
    echo -e "${RED}ERROR: Vite dev server failed to start${NC}"
    kill $VITE_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}  ✓ Vite dev server running on http://localhost:5173${NC}"
echo ""

# ── Step 3: Launch Electron ──────────────────────────────────────────────────
echo -e "${YELLOW}[3/3] Launching Electron app...${NC}"
echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  🚀 Starting Electron Application      ${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo "The Electron window should open shortly..."
echo "Backend will start automatically and may take 10-30 seconds to be ready."
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the app and clean up${NC}"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"
    kill $VITE_PID 2>/dev/null || true
    echo -e "${GREEN}Cleanup complete${NC}"
    exit 0
}

trap cleanup EXIT INT TERM

# Launch Electron with Vite dev server URL
VITE_DEV_SERVER_URL=http://localhost:5173 npx electron .

# Keep script alive
wait
