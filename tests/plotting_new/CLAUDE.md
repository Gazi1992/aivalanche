# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Frontend
```bash
cd frontend
npm run dev       # Start development server (Vite) on port 5173
npm run build     # Build for production
npm run preview   # Preview production build
npm run lint      # Run ESLint
```

### Backend
```bash
cd backend
pip install -r requirements.txt    # Install Python dependencies
python -m uvicorn api.server:app --reload --port 8000    # Run backend server
```

### Electron Desktop App
```bash
cd electron
npm run dev    # Run in development mode
npm run pack   # Build desktop application
```

## Architecture Overview

This is a three-tier visualization application with JSON-driven configuration and AI-powered assistance:

### Core Data Flow
1. **Configuration Input**: JSON config files define all plot specifications
2. **Validation**: `config_loader.py` reads and validates configs against `config_schema.py`
3. **Data Processing**: `data_handler.py` loads data files (CSV, Excel, JSON) into pandas DataFrames
4. **AI Processing**: Natural language requests processed by Google Gemini AI via `ai_service.py`
5. **Plot Generation**: `plot_factory.py` creates Plotly figures, `dashboard_builder.py` assembles the dashboard
6. **API Layer**: FastAPI server (`api/server.py`) serves plots and handles frontend requests
7. **Frontend**: React app renders interactive Plotly visualizations
8. **Desktop**: Electron wrapper creates standalone desktop application

### Key Backend Components

- **config_schema.py**: Master definition of all plot types, properties, validators, and defaults. Dynamically reads available themes from `frontend/src/themes.css`
- **config_loader.py**: Validates JSON configs, applies defaults, ensures data integrity
- **data_handler.py**: Handles file I/O, data transformations, fitting operations
- **plot_factory.py**: Creates individual Plotly figures (line, scatter, histogram, bar, scatter matrix, parallel coordinates)
- **dashboard_builder.py**: Manages layout and composition of multiple plots
- **ai/ai_service.py**: Orchestrates AI-powered visualization generation using Google Gemini
- **utils/**: Helper modules for colors, data fitting, layout, messaging, schema validation

### Frontend Structure

- **App.jsx**: Main React application, manages state and API communication
- **themes.css**: Centralized theming system using CSS variables and data-theme selectors
- **components/Sidebar/**: Chat interface and AI interaction components
- **components/EditPane/**: Interactive plot editing controls
- **components/Chat/**: AI chat components for natural language visualization

### Important Development Notes

1. **Hot Reload Active**: Both frontend and backend auto-reload on file changes - DO NOT manually restart servers
2. **Schema Documentation**: Changes to `config_schema.py` must be reflected in `docs/config_reference.md`
3. **Debugging**: Check `backend_debug.log` and `frontend_payload.log` for errors
4. **Theme Discovery**: Valid themes are automatically extracted from `frontend/src/themes.css`
5. **API Documentation**: Available at http://localhost:8000/docs when backend is running

### Configuration Schema

The config JSON structure follows this hierarchy:
- Top level: app settings (title, theme, margins, grid_layout)
- `figures[]`: Array of plot containers with axes settings
- `figures[].items[]`: Individual plot items (line, scatter, bar, etc.) with data source and styling

### AI Integration

The application integrates Google Gemini AI for:
- Natural language to visualization conversion
- Data analysis and plot suggestions
- Interactive chat-based configuration generation
- System prompts defined in `ai/visualization_prompts.py`

### Data Pipeline

1. Config specifies data source files and column mappings
2. `data_handler.py` loads and preprocesses data
3. Optional fitting/transformation operations applied
4. `data/data_analyzer.py` analyzes data for AI suggestions
5. Data passed to Plotly for visualization
6. Frontend receives Plotly JSON and renders interactive plots