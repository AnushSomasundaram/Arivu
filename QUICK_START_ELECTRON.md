# Quick Start - Arivu Electron App

## Clean Databases (Optional but Recommended)

Before building or testing, clean old data for a fresh start:

```bash
cd /Users/software/development/arivu
./clean-databases.sh
```

This removes:
- Development databases
- User data (~/.arivu/)
- ChromaDB vector stores
- Build artifacts

## Test in Development Mode

```bash
cd /Users/software/development/arivu

# Option 1: Use the automated test script
./test-electron-dev.sh

# Option 2: Manual testing
cd Arivu/Frontend/vue-project

# Step 1: Build Electron scripts
npm run build-electron

# Step 2: Start Vite dev server (in one terminal)
npm run dev -- --port 5173

# Step 3: Launch Electron (in another terminal)
VITE_DEV_SERVER_URL=http://localhost:5173 npx electron .
```

## What Should Happen

1. **Electron window opens** (may take a few seconds)
2. **DevTools open automatically** (for debugging)
3. **Backend starts in background**:
   - Check console logs: `[Main] Starting backend server...`
   - Wait 10-30 seconds for backend to be ready
   - Look for: `[Main] Backend is ready!`
4. **Frontend loads** and shows the Arivu interface
5. **API calls work** - you should be able to use all features

## Troubleshooting

### Backend fails to start

Check console logs for errors. Common issues:
- Python venv not found → Make sure `.venv` exists in `Arivu/Backend/`
- Port in use → Kill processes on port 8000-8010

### Blank window

Check DevTools console for errors. Try:
- Rebuild: `npm run build-electron`
- Clear cache and restart

## Build Production DMG

Once testing works:

```bash
cd /Users/software/development/arivu
./build-electron-app.sh
```

**Note:** This script automatically cleans databases and old data before building!

Output: `Arivu/Frontend/vue-project/release/*.dmg`

## Current Status

✅ Electron scripts built successfully
✅ Configuration complete
⏳ Ready for testing

**Next:** Run `./test-electron-dev.sh` to test the app!
