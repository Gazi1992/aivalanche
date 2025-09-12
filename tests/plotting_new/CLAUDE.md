# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Frontend
```bash
cd frontend
npm install               # Install dependencies
npm run dev               # Start development server (Vite) on port 5173
npm run build             # Build for production
npm run preview           # Preview production build
npm run lint              # Run ESLint
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
npm install               # Install dependencies
npm run dev               # Run in development mode
npm run pack              # Build desktop application
```

## Architecture Overview

This is a metadata-driven visualization application with Python execution and AI-powered assistance:

### Core Data Flow
1. **Python Execution**: Python scripts create Plotly figures via `execution_service.py`
2. **Metadata System**: Fixed metadata structure controls ALL visual properties
3. **Figure Management**: `figureManager.js` creates managed figures with embedded metadata
4. **Data Processing**: `data_handler.py` loads data files (CSV, Excel, JSON) into pandas DataFrames
5. **AI Processing**: Natural language requests processed by Google Gemini AI via `ai_service.py`
6. **Plot Rendering**: Metadata-driven rendering via `generateLayoutFromMetadata()`
7. **API Layer**: FastAPI server (`api/server.py`) serves plots and handles frontend requests
8. **Frontend**: React app renders interactive Plotly visualizations using metadata
9. **Desktop**: Electron wrapper creates standalone desktop application

### Metadata Architecture (NEW)

**Key Principle**: Metadata is the single source of truth for all visual properties.

#### Metadata Structure
```javascript
{
  appearance: {
    title: { text, visible, fontSize, color, bold, italic, alignment },
    axes: {
      x: { label, scale, range, ticks, grid },
      y: { label, scale, range, ticks, grid }
    },
    legend: { 
      visible, position: {x, y, xanchor, yanchor},
      backgroundColor, borderColor, items 
    },
    grid: { x, y },
    background: { figure, plot },
    text: { title, axisLabel, axisTick, legend }
  },
  data: { traces: [], selectedTraceIndex: 0 },
  capabilities: { hasAxes, hasLegend, ... },
  customization: { userModified: Set(), pythonModified: Set() }
}
```

#### Key Components
- **metadataStructure.js**: Defines fixed metadata structure
- **figureManager.js**: Manages figures with embedded metadata
  - `createManagedFigure()`: Creates figure with complete metadata
  - `generateLayoutFromMetadata()`: Renders using metadata only
  - `syncFigureWithDOM()`: Captures zoom/pan state
- **useFixedMetadata.js**: Hook for EditPane metadata management

### Key Backend Components

- **config_schema.py**: Master definition of all plot types, properties, validators, and defaults
- **config_loader.py**: Validates JSON configs, applies defaults, ensures data integrity
- **data_handler.py**: Handles file I/O, data transformations, fitting operations
- **plot_factory.py**: Creates individual Plotly figures
- **dashboard_builder.py**: Manages layout and composition of multiple plots
- **execution_service.py**: Python code execution with sandboxed environment
  - `ExecutionSession`: Maintains persistent Python namespace
  - `PlotRegistry`: Collects plots created during execution
  - `register_plot()`: Function injected to capture plots with metadata
- **ai/ai_service.py**: Orchestrates AI-powered visualization generation
- **utils/**: Helper modules for colors, data fitting, layout, messaging

### Frontend Structure

- **App.jsx**: Main React application, manages state and API communication
- **themes.css**: Centralized theming system with CSS variables
  - Plot margins: `--plot-margin-left/right/top/bottom/pad`
  - Grid spacing: `--grid-horizontal-spacing`, `--grid-vertical-spacing`
- **components/EditPane/**: Interactive plot editing controls
  - Reads/writes directly to figure.metadata
  - All subsections mapped to metadata structure
- **components/Sidebar/**: Chat interface and AI interaction
- **utils/figureManager.js**: Core figure management with metadata
- **utils/metadataStructure.js**: Fixed metadata structure definition

### Python Execution & Metadata

Python can control plots through metadata in two ways:

1. **Via register_plot()**:
```python
register_plot(fig, 
  plot_id='scatter_1',
  metadata={
    'appearance': {
      'title': {'text': 'My Title', 'fontSize': 24}
    }
  }
)
```

2. **Via Plotly layout** (extracted automatically):
```python
fig.update_layout(
  title="Extracted to metadata.appearance.title.text",
  xaxis_title="Extracted to metadata.appearance.axes.x.label.text"
)
```

### Important Development Notes

1. **Metadata is Single Source of Truth**: All rendering decisions come from metadata
2. **Fixed Structure**: Metadata structure never changes, only values
3. **Python Only Updates Values**: Can't add/remove properties
4. **Theme Integration**: Margins, colors, spacing from CSS variables
5. **Hot Reload Active**: Both frontend and backend auto-reload on file changes
6. **API Documentation**: Available at http://localhost:8000/docs when backend is running

### Default Plot Settings

- **Margins**: Defined in `themes.css` as CSS variables
- **Legend**: Positioned inside plot (top-left) with semi-transparent background
- **Grid**: 1 column for single plot, configurable columns for multiple
- **Title**: Center-aligned with proper x positioning

### Data Pipeline

1. Python code executes in ExecutionSession
2. register_plot() captures figure + metadata
3. API returns: `{ plots: [{figure, metadata}, ...] }`
4. Frontend creates managed figures with embedded metadata
5. Plots render using metadata-driven layout
6. EditPane reads/writes figure.metadata directly

### AI Integration

The application integrates Google Gemini AI for:
- Natural language to visualization conversion
- Data analysis and plot suggestions
- Interactive chat-based configuration generation
- System prompts defined in `ai/visualization_prompts.py`