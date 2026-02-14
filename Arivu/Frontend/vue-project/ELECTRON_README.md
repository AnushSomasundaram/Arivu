# Arivu Electron App

This directory contains the Electron desktop application wrapper for Arivu.

## Prerequisites

- Node.js ^20.19.0 || >=22.12.0
- npm or yarn

## Installation

First, install the dependencies:

```bash
npm install
```

## Development

To run the Electron app in development mode:

```bash
# Terminal 1: Start the Vite dev server
npm run dev

# Terminal 2: Build electron files and start Electron
npm run electron:dev
```

The app will open with the development server and hot-reload enabled.

## Building for Production

Build the Electron app for your current platform:

```bash
npm run electron:build
```

Or build for specific platforms:

```bash
# macOS
npm run electron:build:mac

# Windows
npm run electron:build:win

# Linux
npm run electron:build:linux
```

The built applications will be in the `dist-electron` directory.

## Project Structure

```
electron/
├── main.ts       # Main process (Electron entry point)
├── preload.ts    # Preload script (bridge between main and renderer)
└── dist/         # Compiled Electron files (generated)

dist/             # Vue app build output
dist-electron/    # Final packaged applications
```

## Backend Integration

The Electron app expects the Python backend to be running on `http://127.0.0.1:8000`. Make sure to start your FastAPI backend before using the app:

```bash
cd ../../Backend
# Start your FastAPI server
python -m uvicorn app.main:app --reload
```

## Icon Setup

To customize the app icon, place your icon files in the `build/` directory:

- macOS: `build/icon.icns`
- Windows: `build/icon.ico`
- Linux: `build/icon.png` (512x512 recommended)

You can use tools like:
- [electron-icon-builder](https://www.npmjs.com/package/electron-icon-builder)
- [electron-icon-maker](https://www.npmjs.com/package/electron-icon-maker)

## Security

The Electron app is configured with:
- Context isolation enabled
- Node integration disabled
- Preload script for secure IPC communication

## Troubleshooting

### App doesn't connect to backend

Make sure:
1. The backend is running on port 8000
2. CORS is properly configured in the FastAPI backend
3. Check the console for any network errors

### Build fails

1. Clear the build directories:
   ```bash
   rm -rf dist dist-electron electron/dist
   ```
2. Reinstall dependencies:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```
3. Try building again

## Notes

- The app uses Vite for building both the Vue app and Electron files
- electron-builder is used for packaging the final application
- Development builds include DevTools for debugging
