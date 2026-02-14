#!/bin/bash
set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/Arivu/Backend"
FRONTEND_DIR="$PROJECT_ROOT/Arivu/Frontend/vue-project"
ELECTRON_DIR="$PROJECT_ROOT/electron-app"
DIST_DIR="$ELECTRON_DIR/dist"
RENDERER_DIR="$ELECTRON_DIR/renderer"
BACKEND_RESOURCE_DIR="$ELECTRON_DIR/resources/backend"

echo "=========================================="
echo "      Building Arivu Electron App"
echo "=========================================="

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed."
    exit 1
fi

# Check for Node.js
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed."
    exit 1
fi

# 1. Clean Previous Builds
echo "------------------------------------------"
echo "Cleaning previous builds..."
rm -rf "$DIST_DIR"
rm -rf "$RENDERER_DIR"
rm -rf "$ELECTRON_DIR/release"
rm -rf "$BACKEND_RESOURCE_DIR"
mkdir -p "$DIST_DIR"
mkdir -p "$RENDERER_DIR"
mkdir -p "$BACKEND_RESOURCE_DIR"

# 2. Build Backend Executable
echo "------------------------------------------"
echo "Building Python Backend..."
cd "$BACKEND_DIR"

# Check if build-backend.sh exists and use it, otherwise inline build
if [ -f "$PROJECT_ROOT/build-backend.sh" ]; then
    "$PROJECT_ROOT/build-backend.sh"
else
    echo "Running inline backend build..."
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    source .venv/bin/activate
    pip install -r requirements.txt
    pyinstaller arivu-backend.spec --clean --noconfirm
fi

# Locate the built executable
if [ -f "$BACKEND_DIR/dist/arivu-backend" ]; then
    BACKEND_EXE="$BACKEND_DIR/dist/arivu-backend"
elif [ -f "$BACKEND_DIR/dist/arivu-backend.exe" ]; then
    BACKEND_EXE="$BACKEND_DIR/dist/arivu-backend.exe"
else
    echo "Error: Backend executable not found!"
    exit 1
fi

echo "Copying backend executable to Electron resources..."
cp "$BACKEND_EXE" "$BACKEND_RESOURCE_DIR/"

# 3. Build Frontend
echo "------------------------------------------"
echo "Building Vue Frontend..."
cd "$FRONTEND_DIR"
npm install
npm run build

echo "Copying frontend build to Electron renderer..."
cp -r dist/* "$RENDERER_DIR/"

# 4. Build Electron Main Process
echo "------------------------------------------"
echo "Building Electron Main Process..."
cd "$ELECTRON_DIR"
npm install
npm run build

# 5. Package Electron App
echo "------------------------------------------"
echo "Packaging Electron App..."
npm run dist:mac

echo "=========================================="
echo "      Build Successful!"
echo "=========================================="
echo "Artifacts are in: $ELECTRON_DIR/release"
