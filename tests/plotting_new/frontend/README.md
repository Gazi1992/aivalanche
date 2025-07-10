# Aivalanche Frontend

## Setup

```bash
cd frontend
npm install  # or yarn / pnpm
npm run dev
```

The development server expects the backend FastAPI API to be running on `http://127.0.0.1:8000` (see `vite.config.js`).

## Environment variables

Create a file named `.env.local` (ignored by git) and set:

```
VITE_API=http://127.0.0.1:8000
```

For production deployments, set `VITE_API` to the publicly reachable URL of your backend, e.g.:

```
VITE_API=https://aivalanche.example.com/api
``` 