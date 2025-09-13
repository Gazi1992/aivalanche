# Data Visualization Studio

A modern, metadata-driven visualization application built with React, Plotly, and Python. Features AI-powered natural language visualization generation, interactive plot editing, and comprehensive export capabilities.

## Core Features

### Metadata-Driven Architecture
- **Single Source of Truth**: All visual properties controlled through a fixed metadata structure
- **Python Integration**: Execute Python code to generate Plotly figures with custom metadata
- **Real-time Editing**: Interactive edit pane that modifies metadata and updates plots instantly

### AI-Powered Visualization
- **Natural Language Interface**: Chat with Google Gemini AI to create visualizations
- **Smart Plot Suggestions**: AI analyzes your data and suggests appropriate visualizations
- **Interactive Refinement**: Iterate on plots through conversational interface

### Advanced Plot Management
- **Grid Layout System**: Configurable multi-column grid for multiple plots
- **Expanded View**: Full-screen mode for detailed plot examination
- **Theme Support**: Multiple built-in themes with comprehensive CSS variable system
- **Export Options**: PNG, SVG, CSV, and JSON export formats

### Interactive Editing
- **Edit Pane**: Comprehensive controls for all plot properties
  - Title, axes, legend, grid settings
  - Color customization for all elements
  - Text formatting and sizing
  - Data trace management
- **Grid Controls**: Main grid, minor grid, and zero line styling
- **Background Customization**: Figure and plot area backgrounds

## Architecture Overview

### Frontend (React + Vite)
```
frontend/
├── src/
│   ├── App.jsx                 # Main application
│   ├── components/
│   │   ├── EditPane/           # Plot editing interface
│   │   ├── PlotGrid/           # Plot container and grid
│   │   ├── Sidebar/            # Chat and controls
│   │   └── icons/              # Custom icon components
│   ├── hooks/                  # Custom React hooks
│   ├── utils/
│   │   ├── figureManager.js    # Core metadata management
│   │   ├── plotExport.js       # Export functionality
│   │   ├── plotTheme.js        # Theme management
│   │   ├── plotLayout.js       # Layout calculations
│   │   └── index.js            # Central export point
│   └── themes.css              # CSS variables and themes
```

### Backend (FastAPI + Python)
```
backend/
├── api/
│   └── server.py               # FastAPI server
├── core/
│   ├── execution_service.py    # Python code execution
│   ├── plot_factory.py         # Plotly figure creation
│   └── dashboard_builder.py    # Dashboard composition
├── data/
│   └── data_handler.py         # Data loading and processing
└── ai/
    └── ai_service.py           # Google Gemini integration
```

## Installation

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- Google Gemini API key (for AI features)

### Frontend Setup
```bash
cd frontend
npm install
npm run dev  # Starts on http://localhost:5173
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Set your Gemini API key
export GOOGLE_API_KEY="your-api-key-here"  # Linux/Mac
# or
set GOOGLE_API_KEY=your-api-key-here  # Windows

# Run the server (currently on port 8001)
python -m uvicorn api.server:app --reload --port 8001
```

## Quick Start

1. **Start Both Servers**: Run frontend and backend as described above

2. **Load Demo Visualization**:
   - Click "Load Demo Visualizations" on the welcome screen
   - A sample scatter plot will appear

3. **Edit the Plot**:
   - Click the edit icon on any plot
   - Modify properties in the edit pane
   - Changes apply instantly

4. **Use AI Assistant**:
   - Upload a data file using the 📎 button in chat
   - Ask the AI to create visualizations
   - Example: "Create a line chart showing trends over time"

5. **Export Your Work**:
   - Click the download icon to export as PNG
   - Use the edit pane for more export options

## Key Features in Detail

### Metadata Structure
Every plot has a fixed metadata structure controlling all visual properties:
```javascript
{
  appearance: {
    title: { text, visible, fontSize, color, ... },
    axes: { x: {...}, y: {...} },
    legend: { visible, position, colors, ... },
    grid: { main, minor, zero lines },
    background: { figure, plot }
  },
  data: { traces, selectedTraceIndex },
  capabilities: { hasAxes, hasLegend, ... }
}
```

### Python Execution
Execute Python code to generate plots:
```python
import plotly.graph_objects as go

fig = go.Figure(data=[go.Scatter(x=[1,2,3], y=[4,5,6])])
register_plot(fig, plot_id='my_plot', metadata={...})
```

### Grid System
- Automatic layout calculation based on plot count
- Configurable columns (1-4)
- Responsive sizing with proper height calculations
- Minor grid and zero line support

### Export Capabilities
- **Images**: PNG, SVG, JPEG, WebP
- **Data**: CSV format with all traces
- **Configuration**: JSON with complete plot setup
- **Clipboard**: Copy plot as image (where supported)

## Recent Updates

### Latest Features
- Fixed minor grid visibility toggling
- Grid colors now apply to all grid elements
- Added comprehensive plot utility modules
- Improved axis type detection (numeric vs categorical)
- Single plot demo to avoid Plotly DOM conflicts

### Known Limitations
- Multi-plot support temporarily limited due to Plotly DOM state sharing
- Currently using port 8001 for backend (configurable)

## Documentation

- [Frontend Utilities Guide](./frontend_utilities.md)
- [AI Visualization Guide](./ai_visualization_guide.md)
- [Development Setup](./DEV_SETUP.md)
- [API Documentation](./API_SETUP.md)

## Development Notes

1. **Hot Reload**: Both frontend and backend auto-reload on changes
2. **Port Configuration**: Backend currently on 8001, frontend on 5173
3. **Metadata First**: All rendering decisions come from metadata
4. **Fixed Structure**: Metadata structure never changes, only values
5. **Theme Integration**: All styling through CSS variables

## Troubleshooting

### Common Issues

**Grid not updating**: 
- Ensure metadata changes trigger re-render
- Check that grid color is applied to all elements

**Plot not displaying**:
- Verify backend is running on correct port (8001)
- Check browser console for errors
- Ensure data format is correct

**AI not responding**:
- Verify GOOGLE_API_KEY is set
- Check API quota limits
- Review error messages in backend logs

## Contributing

See [CLAUDE.md](../CLAUDE.md) for development guidelines when using Claude Code.

## License

[Your License Here]