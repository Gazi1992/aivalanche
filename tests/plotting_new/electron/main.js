const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let pyProc = null;

function createPythonBackend() {
  const isWin = process.platform === 'win32';
  // In dev mode expect `python -m uvicorn` already running; skip spawning.
  if (process.env.SKIP_BACKEND === '1') {
    console.log('Skipping backend spawn (SKIP_BACKEND=1)');
    return;
  }

  const backendExecutable = isWin ? 'aivalanche_backend.exe' : 'aivalanche_backend';
  const exePath = path.join(__dirname, backendExecutable);
  console.log('Spawning backend:', exePath);

  pyProc = spawn(exePath, []);
  pyProc.stdout.on('data', data => console.log(`[backend] ${data}`));
  pyProc.stderr.on('data', data => console.error(`[backend] ${data}`));
  pyProc.on('close', code => console.log(`Backend exited with code ${code}`));
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      contextIsolation: true,
    },
    autoHideMenuBar: true, // hide the default menu bar
  });
  // Fully disable menu bar (even when Alt is pressed)
  win.setMenuBarVisibility(false);

  // In development load Vite dev server, else load built files.
  const devURL = process.env.FRONTEND_DEV_URL || 'http://localhost:5173';
  if (process.env.NODE_ENV === 'development') {
    win.loadURL(devURL);
  } else {
    win.loadFile(path.join(__dirname, '..', 'frontend', 'dist', 'index.html'));
  }
}

app.whenReady().then(() => {
  createPythonBackend();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', () => {
  if (pyProc) {
    pyProc.kill();
  }
}); 