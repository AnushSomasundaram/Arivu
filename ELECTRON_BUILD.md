# Arivu Electron Application - Build & Distribution Guide

This guide covers how to build, test, and distribute the Arivu desktop application as a standalone Electron app.

## Overview

The Arivu Electron app is a self-contained desktop application that includes:
- **Frontend**: Vue.js application (built with Vite)
- **Backend**: Python FastAPI server (packaged as standalone executable with PyInstaller)
- **Electron**: Wrapper that manages both components

### Key Features
- ✅ Fully standalone - no external dependencies needed
- ✅ Automatic backend startup with the app
- ✅ Dynamic port allocation (no conflicts on different machines)
- ✅ Native desktop experience on macOS, Windows, and Linux
- ✅ Single DMG/installer for easy distribution

---

## Directory Structure

```
Arivu/
├── Backend/
│   ├── app/                    # Python FastAPI application
│   ├── arivu-backend.spec      # PyInstaller configuration
│   └── dist/                   # Built backend executable
│       └── arivu-backend       # Standalone backend binary
│
└── Frontend/vue-project/
    ├── electron/               # Electron source files
    │   ├── main.ts            # Main process (app lifecycle, backend management)
    │   ├── preload.ts         # Preload script (secure IPC bridge)
    │   └── dist/              # Compiled Electron scripts
    ├── src/                   # Vue application source
    ├── dist/                  # Built frontend files
    ├── electron-builder.json5 # Packaging configuration
    └── release/               # Final DMG/installers
```

---

## Prerequisites

### macOS Requirements
- **Node.js**: 20.19.0+ or 22.12.0+
- **Python**: 3.9+ (3.11 recommended)
- **PyInstaller**: Installed in backend venv
- **Xcode Command Line Tools**: `xcode-select --install`

### Install Dependencies

```bash
# Backend dependencies
cd Arivu/Backend
source .venv/bin/activate
pip install pyinstaller

# Frontend dependencies
cd ../Frontend/vue-project
npm install
```

---

## Development Workflow

### Testing in Electron Dev Mode

Before packaging, test the app in development mode:

```bash
# From project root
./test-electron-dev.sh
```

This script:
1. Builds the Electron main/preload scripts
2. Starts Vite dev server (hot reload enabled)
3. Launches Electron with backend auto-start
4. Opens DevTools for debugging

**What to test:**
- ✅ Backend starts automatically (check console logs)
- ✅ Frontend loads and connects to backend
- ✅ API calls work (check Network tab)
- ✅ No CORS errors
- ✅ App window opens and is responsive

### Manual Dev Mode

```bash
cd Arivu/Frontend/vue-project

# Terminal 1: Build Electron scripts
npm run build-electron

# Terminal 2: Start Vite dev server
npm run dev -- --port 5173

# Terminal 3: Launch Electron
VITE_DEV_SERVER_URL=http://localhost:5173 npx electron .
```

---

## Building for Distribution

### Automatic Build (Recommended)

Use the unified build script that handles everything:

```bash
# From project root
./build-electron-app.sh
```

This script:
1. **Builds Backend**: PyInstaller creates standalone executable
2. **Builds Electron Scripts**: TypeScript → JavaScript
3. **Builds Frontend**: Vite production build
4. **Packages App**: electron-builder creates DMG

Output: `Arivu/Frontend/vue-project/release/*.dmg`

### Manual Build Steps

If you prefer to build step-by-step:

#### Step 1: Build Backend Executable

```bash
cd Arivu/Backend
source .venv/bin/activate
pyinstaller arivu-backend.spec --clean --noconfirm
chmod +x dist/arivu-backend

# Test the executable
./dist/arivu-backend --port 8000
# Should start server on http://127.0.0.1:8000
```

#### Step 2: Build Frontend & Electron

```bash
cd ../Frontend/vue-project

# Build Electron scripts (main.ts, preload.ts)
npm run build-electron

# Build Vue frontend for production
npm run build
```

#### Step 3: Package with electron-builder

```bash
# macOS DMG
npm run electron:build:mac

# Windows installer
npm run electron:build:win

# Linux AppImage
npm run electron:build:linux
```

---

## Configuration

### Backend Configuration

The backend executable accepts these arguments:
```bash
arivu-backend --host 127.0.0.1 --port 8000
```

Environment variables (optional):
```bash
ARIVU_BACKEND_HOST=127.0.0.1
ARIVU_BACKEND_PORT=8000
ARIVU_CORS_ORIGINS=*
```

### Electron Builder Configuration

Edit `electron-builder.json5` to customize:

```json5
{
  "appId": "com.arivu.app",
  "productName": "Arivu",
  "mac": {
    "category": "public.app-category.productivity",
    "target": ["dmg"],
    "icon": "build/icon.icns"
  }
}
```

### App Icons

Place icons in `Arivu/Frontend/vue-project/build/`:
- `icon.icns` - macOS (512x512 PNG → convert with `iconutil`)
- `icon.ico` - Windows
- `icon.png` - Linux (512x512 PNG)

---

## Distribution

### Testing the DMG

After building, test the DMG on your machine:

```bash
# Mount and install
open Arivu/Frontend/vue-project/release/*.dmg

# Drag to Applications
# Launch from Applications folder
```

### Distributing to Other Machines

The DMG is fully self-contained and can be distributed to other macOS machines:

1. **Share the DMG file**: Email, cloud storage, USB drive
2. **Users install**: Drag to Applications folder
3. **First launch**: Right-click → Open (to bypass Gatekeeper on unsigned apps)

**No dependencies required** - the app includes:
- Python runtime
- All Python packages
- Node.js libraries (bundled in Electron)
- Backend executable

### Code Signing (Optional)

For distribution outside your organization, consider code signing:

```bash
# Get Apple Developer ID certificate
# Then build with signing:
export CSC_NAME="Developer ID Application: Your Name"
npm run electron:build:mac
```

---

## Troubleshooting

### Backend Doesn't Start

**Symptoms**: Electron window opens but shows connection errors

**Debug steps**:
1. Open DevTools (View → Toggle Developer Tools)
2. Check Console for error messages
3. Look for backend startup logs
4. Check if port 8000-9000 range is available

**Solution**:
- Check `~/.arivu/` directory exists
- Ensure backend executable has execute permissions
- Try running backend manually: `./Arivu/Backend/dist/arivu-backend --port 8000`

### Frontend Shows Blank Page

**Symptoms**: Electron window opens but is blank

**Debug steps**:
1. Check DevTools Console for errors
2. Verify `dist/index.html` exists
3. Check DevTools Network tab for failed requests

**Solution**:
- Rebuild frontend: `npm run build`
- Check `vite.config.ts` base path is `'./'`
- Ensure all assets are in `dist/`

### "Damaged App" Warning on macOS

**Symptoms**: macOS blocks app from opening

**Solution**:
```bash
# Remove quarantine attribute
xattr -cr /Applications/Arivu.app

# Or right-click → Open (bypass Gatekeeper)
```

### Build Fails

**Common issues**:

1. **PyInstaller errors**: Missing Python dependencies
   ```bash
   pip install -e . --force-reinstall
   ```

2. **electron-builder errors**: Backend executable not found
   ```bash
   # Check path in electron-builder.json5
   ls -la ../../Backend/dist/arivu-backend
   ```

3. **TypeScript errors**: Type mismatches
   ```bash
   npm run type-check
   ```

---

## Performance

### App Size

Typical sizes:
- **Backend executable**: ~150-300 MB (includes Python + ML models)
- **Frontend bundle**: ~5-10 MB
- **Electron runtime**: ~100-150 MB
- **Total DMG**: ~250-450 MB

### Startup Time

- **Cold start**: 5-15 seconds (backend initialization)
- **Warm start**: 2-5 seconds
- **Backend ready**: Check health endpoint at `http://127.0.0.1:{port}/api/health`

### Optimization

To reduce size:
1. **Backend**: Exclude unnecessary ML models in `arivu-backend.spec`
2. **Frontend**: Enable tree-shaking in `vite.config.ts`
3. **Electron**: Use `asar` archive (electron-builder does this automatically)

---

## Development Tips

### Hot Reload During Development

Use dev mode for fast iteration:
```bash
./test-electron-dev.sh
```

Changes to Vue components auto-reload, but changes to Electron main/preload require rebuild:
```bash
npm run build-electron
# Then restart Electron
```

### Debugging Backend in Electron

Add logging to see backend output:
```typescript
// electron/main.ts
backendProcess.stdout?.on('data', (data) => {
  console.log(`[Backend] ${data}`)
})
```

Check logs in Electron DevTools Console.

### Testing on Different Ports

Set environment variable before launching:
```bash
ARIVU_BACKEND_PORT=9000 npx electron .
```

The app will automatically use port 9000 instead of 8000.

---

## Scripts Reference

| Script | Description |
|--------|-------------|
| `./test-electron-dev.sh` | Test in Electron dev mode |
| `./build-electron-app.sh` | Build complete app + DMG |
| `npm run build-electron` | Build Electron scripts only |
| `npm run electron:dev` | Launch in dev mode (manual) |
| `npm run electron:build:mac` | Package macOS DMG |
| `npm run electron:build:win` | Package Windows installer |
| `npm run electron:build:linux` | Package Linux AppImage |

---

## Architecture

### Process Flow

```
User launches Arivu.app
  ↓
Electron Main Process starts
  ↓
Main process spawns Backend subprocess (arivu-backend)
  ↓
Backend starts on available port (8000-9000 range)
  ↓
Main process creates BrowserWindow
  ↓
Frontend loads from dist/index.html
  ↓
Frontend requests API config via IPC (electronAPI.getApiConfig())
  ↓
Main process returns backend URL
  ↓
Frontend connects to backend API
  ↓
App is ready! 🎉
```

### IPC Communication

```typescript
// Renderer (Frontend)
const config = await window.electronAPI.getApiConfig()
// { baseUrl: "http://127.0.0.1:8000" }

// Main Process (Backend)
ipcMain.handle('get-api-config', () => {
  return { baseUrl: backendUrl }
})
```

---

## Next Steps

1. **Test thoroughly** in dev mode: `./test-electron-dev.sh`
2. **Build DMG**: `./build-electron-app.sh`
3. **Test DMG** on your machine
4. **Test on another macOS machine** to ensure portability
5. **Distribute** to users

---

## Support

For issues or questions:
- Check logs in DevTools Console
- Review backend logs in app console
- Check `~/.arivu/` directory for data/logs
- Open issue at: https://github.com/your-repo/arivu/issues

---

**Last Updated**: 2026-02-13
