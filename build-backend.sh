#!/bin/bash
# ─── Build Arivu Backend (Optimized) ─────────────────────────────────────────
# This script:
#   1. Installs CPU-only PyTorch (~150MB vs ~800MB default)
#   2. Builds the backend executable with PyInstaller
#   3. Copies the result to the electron-app resources
# ─────────────────────────────────────────────────────────────────────────────

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

BACKEND_DIR="$(cd "$(dirname "$0")/Arivu/Backend" && pwd)"
ELECTRON_DIR="$(cd "$(dirname "$0")/electron-app" && pwd)"
VENV="$BACKEND_DIR/.venv"
PYTHON="$VENV/bin/python"
PIP="$VENV/bin/pip"

echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Arivu Backend — Optimized Build          ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""

# ── Step 1: Switch to CPU-only PyTorch ──────────────────────────────────────
echo -e "${YELLOW}Step 1/4: Installing CPU-only PyTorch...${NC}"
cd "$BACKEND_DIR"

# Uninstall existing torch first to avoid conflicts
$PIP uninstall -y torch torchvision torchaudio 2>/dev/null || true

# Install CPU-only torch
$PIP install torch --index-url https://download.pytorch.org/whl/cpu

echo -e "${GREEN}  ✓ CPU-only PyTorch installed${NC}"
echo ""

# ── Step 2: Ensure PyInstaller is installed ─────────────────────────────────
echo -e "${YELLOW}Step 2/4: Checking PyInstaller...${NC}"
$PIP install pyinstaller 2>/dev/null
echo -e "${GREEN}  ✓ PyInstaller ready${NC}"
echo ""

# ── Step 3: Build the executable ────────────────────────────────────────────
echo -e "${YELLOW}Step 3/4: Building optimized executable...${NC}"
echo "  (This may take a few minutes)"
cd "$BACKEND_DIR"

# Clean previous build
rm -rf build/ dist/

$PYTHON -m PyInstaller arivu-backend.spec --clean --noconfirm

# Check the result
if [ -f "dist/arivu-backend" ]; then
    SIZE=$(du -sh dist/arivu-backend | cut -f1)
    echo -e "${GREEN}  ✓ Build complete! Size: ${SIZE}${NC}"
else
    echo -e "${RED}  ✗ Build failed — check output above${NC}"
    exit 1
fi
echo ""

# ── Step 4: Copy to electron-app resources ──────────────────────────────────
echo -e "${YELLOW}Step 4/4: Copying to electron-app...${NC}"
mkdir -p "$ELECTRON_DIR/resources/backend"
cp dist/arivu-backend "$ELECTRON_DIR/resources/backend/arivu-backend"
echo -e "${GREEN}  ✓ Copied to electron-app/resources/backend/${NC}"
echo ""

# ── Done ────────────────────────────────────────────────────────────────────
FINAL_SIZE=$(du -sh "$ELECTRON_DIR/resources/backend/arivu-backend" | cut -f1)
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Build complete!                          ${NC}"
echo -e "${GREEN}  Backend executable: ${FINAL_SIZE}             ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""
echo "Next: cd $ELECTRON_DIR && npm run dist"
