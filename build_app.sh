#!/bin/bash
set -e

echo "🚀 Starting Arivu Build Process..."

# 1. Build Vue Frontend
echo "📦 Building Frontend..."
cd Arivu/Frontend/vue-project
npm install
npm run build
cd ../../../

# 2. Build Python Backend
echo "🐍 Building Backend..."
cd Arivu/Backend
# Ensure virtual env is active or pyinstaller is available
# Assuming pyinstaller is in path or venv
python3 -m PyInstaller --clean --noconfirm arivu-backend.spec
cd ../../

# 3. Prepare Electron Resources
echo "📂 Preparing Electron Resources..."
mkdir -p electron-app/resources/backend

# Copy Vue dist to electron-app/dist
echo "📂 Copying Frontend assets..."
rm -rf electron-app/dist
cp -r Arivu/Frontend/vue-project/dist electron-app/dist

# PyInstaller created a single file executable 'arivu-backend' in 'dist'
# We need to copy this file to 'electron-app/resources/backend/'
cp Arivu/Backend/dist/arivu-backend electron-app/resources/backend/

# 4. Build Electron App
echo "⚡ Building Electron App..."
cd electron-app
npm install
npm run dist

echo "✅ Build Complete! artifacts are in electron-app/dist"
