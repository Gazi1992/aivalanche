# Aivalanche – Monorepo Dev Setup

This document explains how to run the new **Python backend**, **React front-end**, and **Electron desktop wrapper**.

---
## Prerequisites

* Python 3.9+
* Node.js 18+
* pnpm *(recommended)* or npm / yarn

---
## 1. Backend (FastAPI)

```bash
# Create & activate a virtualenv
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

pip install -r backend/requirements.txt

# Run with auto-reload
cd backend
uvicorn api.server:app --reload --port 8000
```

Visit <http://127.0.0.1:8000/docs> to see automatic Swagger UI.

---
## 2. Front-end (React + Vite)

```bash
cd frontend
pnpm install          # or npm install / yarn
pnpm run dev          # open http://localhost:5173
```

The front-end talks to the backend at `http://127.0.0.1:8000` (see `vite.config.js`).

---
## 3. Desktop wrapper (Electron)

During development we **don’t** spawn the Python backend from Electron – we assume it’s already running.

```bash
cd electron
# Ensure env var so Electron knows not to spawn backend
SKIP_BACKEND=1 npm run dev
```

The Electron window loads the Vite dev server.

---
## Production build

1. **Freeze backend** into a single executable (PyInstaller):

   ```bash
   cd backend
   pyinstaller api/server.py --onefile --name aivalanche_backend \
     --add-data "../data:./data"
   ```

2. **Build front-end** static files:

   ```bash
   cd frontend && pnpm run build
   ```

3. **Package Electron** installer:

   ```bash
   cd electron && npm run pack
   ```

   You’ll find platform-specific installers under `electron/dist/`.

---
## CI Tips

* Use GitHub Actions with a **matrix** over `windows-latest`, `macos-latest`, `ubuntu-latest` to build installers.
* Cache `~/.cache/pip` and `~/.pnpm-store` for speed.
* Sign executables on macOS (`codesign`) and Windows (EV certificate) if distributing publicly. 