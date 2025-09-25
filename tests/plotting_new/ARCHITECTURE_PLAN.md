# LLM-Orchestrated Data Analysis Platform - Complete Architecture Plan

## Executive Summary

This document outlines the complete architecture for a next-generation data analysis and visualization platform where an LLM (Large Language Model) serves as the **sole intelligent orchestrator**. The system provides minimal communication bridges while giving the LLM complete freedom to implement any logic, workflow, or pattern it deems appropriate.

## Philosophy First: The LLM-Centric Architecture

### Fundamental Philosophy
**"Provide bridges, not implementations. The LLM writes everything."**

This architecture is built on a radical premise: the LLM is not just a code generator following patterns - it's the intelligent orchestrator that decides:
- **WHAT** to do (explore, analyze, visualize)
- **HOW** to do it (write actual implementation)
- **WHEN** to do it (natural workflow decisions)
- **WHY** to do it (understanding context and intent)

### Core Principles

1. **Zero Hardcoding**: No forced patterns, no hardcoded limits, no prescribed workflows
2. **Bridges Only**: System provides only communication bridges to frontend/user
3. **LLM Writes Everything**: All logic, all decisions, all implementations come from LLM
4. **Natural Intelligence**: LLM decides workflows based on context, not rules
5. **Complete Freedom**: LLM can implement any approach it finds appropriate
6. **Semantic Understanding**: Intent understood through meaning, not string matching

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION LAYER                          │
│                  (Simple login/user management)                  │
├─────────────────────────────────────────────────────────────────┤
│                     SESSION MANAGEMENT                           │
│           (Create/Delete/Switch Analysis Sessions)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                    SESSION WORKSPACE                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Each session is an isolated LLM environment with:       │   │
│  │  • Persistent memory (survives logout/login)             │   │
│  │  • Saved Python namespace                                │   │
│  │  • Output history                                        │   │
│  │  • Learning context                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↕                                   │
│                     MINIMAL BRIDGE LAYER                         │
│           show() | send_status() | save_to_memory()             │
│           recall_from_memory() | get_session_info()             │
│                              ↕                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                 LLM ORCHESTRATOR (Per Session)                   │
│                  (Complete autonomous control)                   │
│                                                                  │
│     User Input → LLM → Python Code → Execution → Output         │
│                   ↑                      ↓                       │
│                   └──── Decides Everything ────┘                 │
│                          ↓              ↑                        │
│                   Session Memory & Context                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

User Flow:
1. Login → 2. Select/Create Session → 3. Work with LLM → 4. Auto-save state
         → 5. Logout → 6. Return later → 7. Continue where left off

Architecture Benefits:
• Complete session isolation (users don't affect each other)
• Persistent context (LLM remembers everything within session)
• Resumable work (close browser, come back days later)
• Multiple parallel analyses (different sessions for different projects)
• LLM has full freedom within its session sandbox
```

## Component Specifications

### 1. LLM Orchestrator with Explicit Type System

```python
class LLMOrchestrator:
    """
    Main orchestrator that interprets user intent and generates code
    with explicit output type declarations.
    """

    def __init__(self, llm_provider='openai', model='gpt-4'):
        self.llm = LLMProvider(provider=llm_provider, model=model)
        self.execution_service = ExecutionService()

    async def process_request(self, user_input: str, context: dict = None):
        """
        Process user request with automatic error recovery.
        """
        # Generate code with explicit type hints
        code = await self.generate_code_with_types(user_input, context)

        # Execute code - LLM decides if/how to handle errors
        result = await self.execution_service.execute(
            code,
            context.get('session_id', 'default')
        )

        return result

    async def generate_code_with_types(self, user_input: str, context: dict):
        """
        Generate Python code that explicitly declares output types.
        """
        prompt = f"""
        Generate Python code for: {user_input}

        You have complete freedom to implement the solution.

        Available bridges to communicate with frontend:
        - show(data, **metadata): Send any output to frontend with optional metadata
        - send_status(message): Update user on progress
        - send_output(data): Direct output sending

        The show() function accepts anything and any metadata you want to include.
        You decide what metadata is relevant.

        Common patterns (these are examples, not requirements):

        For plots:
        fig = px.scatter(df, x='x', y='y')
        show(fig, plot_type='scatter')

        For tables:
        show(df)  # or show(df, sortable=True, filterable=True)

        For metrics/HTML:
        show('<div class="metric">{{value}}</div>')

        Available functions:
        - load_data(filename): Load CSV/Excel/JSON
        - show(obj, plot_type=None, **options): Display output
        - pandas as pd, numpy as np
        - plotly.express as px, plotly.graph_objects as go

        Context: {context}
        """

        code = await self.llm.generate(prompt)
        return code
```

### 2. Simplified Execution Service with show()

```python
class ExecutionService:
    """
    Executes Python code and collects outputs through show() function.
    """

    def __init__(self):
        self.sessions = {}

    async def execute(self, code: str, session_id: str):
        """
        Execute code and return results.
        LLM decides how to handle any errors in subsequent executions.
        """
        session = self.get_or_create_session(session_id)
        outputs = []

        # Execute the code
        result = await self._run_code(code, session, outputs)

        # Return results - LLM interprets and decides next steps
        return {
            'success': result.get('success', True),
            'outputs': outputs,
            'error': result.get('error') if not result.get('success') else None,
            'session_id': session_id
        }

    async def execute(self, code: str, session_id: str):
        """
        Execute code with show() function for output collection.
        """
        session = self.get_or_create_session(session_id)
        outputs = []

        def show(obj, **metadata):
            """
            Minimal bridge to send any output to frontend.
            LLM decides what to send and what metadata to include.
            """
            # Create output with LLM-provided metadata
            output = {
                'data': obj,
                'id': f"output_{len(outputs)}",
                **metadata  # LLM decides all metadata
            }

            # Send to frontend - frontend interprets based on metadata
            outputs.append(output)

            # The LLM can send ANY metadata it wants:
            # - type: 'plot', 'table', 'html', 'custom', anything...
            # - plot_type: if relevant
            # - controls: what controls to show
            # - intent: 'new', 'update', 'replace', or anything
            # - literally any key-value pairs the LLM finds useful

        # Create namespace
        namespace = {
            'pd': pd,
            'np': np,
            'px': px,
            'go': go,
            'show': show,
            'load_data': self.load_data,
            **session.user_namespace
        }

        try:
            exec(code, namespace)
            session.update_namespace(namespace)

            return {
                'success': True,
                'outputs': outputs,
                'session_id': session_id
            }

        except Exception as e:
            return {
                'success': False,
                'error': self.analyze_error(e),
                'outputs': outputs  # Partial outputs
            }

        # Minimal namespace - just bridges
        namespace = {
            # Standard Python libraries
            'pd': pd, 'np': np, 'px': px, 'go': go,
            'os': os, 'glob': glob, 'pathlib': Path,
            'json': json, 'datetime': datetime,
            'requests': requests,  # For web fetching

            # Communication bridges only
            'show': show,
            'send_status': send_status,
            'send_output': lambda data: outputs.append(data),

            # Session state
            **session.user_namespace
        }

        # LLM handles its own error recovery
        # No prescriptive error patterns
```

### 3. Frontend Interpretation Layer

```javascript
// The frontend interprets whatever the LLM sends
// No rigid capability system - LLM decides what's needed

function interpretOutput(output) {
    // The LLM sent this output with its chosen metadata
    // We interpret it as best we can

    const { data, type, ...metadata } = output;

    // If LLM specified how to handle it, use that
    if (metadata.render_as) {
        return renderCustom(data, metadata);
    }

    // Otherwise, make intelligent guesses
    if (type === 'plot' || hasPlotlyStructure(data)) {
        return renderPlot(data, metadata);
    } else if (type === 'table' || isDataFrame(data)) {
        return renderTable(data, metadata);
    } else {
        return renderGeneric(data, metadata);
    }
}

// Example: LLM can specify ANY controls it wants
// Not from a predefined list, but whatever makes sense
/*
LLM sends:
show(fig,
     type='plot',
     controls=['zoom', 'reset', 'my-custom-control'],
     custom_actions=[{'name': 'Analyze', 'action': 'analyze_data'}],
     message='Hover for details'
)
*/

    'line': {
        zoomable: true,
        pannable: true,
        selectable: false,
        hoverable: true,
        exportable: true,
        editable: true,
        showTable: true,
        controls: ['zoom', 'pan', 'reset', 'export', 'edit', 'table']
    },

    'bar': {
        zoomable: true,
        pannable: true,
        selectable: true,
        hoverable: true,
        exportable: true,
        editable: true,
        showTable: true,
        controls: ['zoom-x', 'pan-x', 'reset', 'export', 'edit', 'table']
    },

    'pie': {
        zoomable: false,  // Pie charts don't zoom
        pannable: false,
        selectable: true,
        hoverable: true,
        exportable: true,
        editable: true,
        showTable: true,
        controls: ['export', 'edit', 'table']  // No zoom/pan
    },

    'parcoords': {
        zoomable: false,  // Has brush selection instead
        pannable: false,
        selectable: true,
        hoverable: true,
        exportable: true,
        editable: false,
        showTable: true,
        controls: ['clear-brushes', 'export', 'table'],
        customInteractions: ['brush', 'reorder-axes']
    },

    'heatmap': {
        zoomable: true,
        pannable: true,
        selectable: true,
        hoverable: true,
        exportable: true,
        editable: true,
        showTable: true,
        controls: ['zoom', 'pan', 'reset', 'colorscale', 'export', 'edit', 'table']
    },

    'scatter3d': {
        zoomable: true,
        pannable: true,
        selectable: false,
        hoverable: true,
        exportable: true,
        editable: true,
        showTable: true,
        controls: ['orbital', 'reset-camera', 'export', 'edit', 'table'],
        customInteractions: ['rotate', 'orbital-control']
    },

    'indicator': {
        zoomable: false,
        pannable: false,
        selectable: false,
        hoverable: false,
        exportable: true,
        editable: true,
        showTable: false,
        controls: ['export', 'edit']  // Minimal
    }
};

// Get capabilities for unknown types
export const DEFAULT_CAPABILITIES = {
    zoomable: true,
    pannable: true,
    selectable: true,
    hoverable: true,
    exportable: true,
    editable: true,
    showTable: true,
    controls: ['zoom', 'pan', 'reset', 'export', 'edit', 'table']
};
```

### 4. Frontend Components

#### Universal Output Renderer

```jsx
function OutputRenderer({ output }) {
    switch(output.type) {
        case 'plot':
            return <PlotContainer output={output} />;

        case 'table':
            return <DataTable {...output} />;

        case 'html':
            return <HTMLContent content={output.content} />;

        default:
            return <pre>{JSON.stringify(output, null, 2)}</pre>;
    }
}
```

#### Intelligent Plot Container

```jsx
function PlotContainer({ output }) {
    const plotType = output.plot_type;  // LLM explicitly told us
    const capabilities = output.capabilities || PLOT_CAPABILITIES[plotType];
    const [isHovered, setIsHovered] = useState(false);

    // Event handlers based on plot type
    const eventHandlers = useEventHandlers(plotType, capabilities);

    return (
        <div
            className="plot-container"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            {/* Only show relevant controls based on plot type */}
            <PlotControls
                visible={isHovered}
                controls={capabilities.controls}
                plotId={output.id}
            />

            {/* Render plot with appropriate interactions */}
            <PlotlyPlot
                data={output.figure.data}
                layout={output.figure.layout}
                frames={output.figure.frames}  // For animations
                {...eventHandlers}
            />

            {/* Status bar only if hoverable */}
            {capabilities.hoverable && (
                <PlotStatusBar cursorInfo={eventHandlers.hoverData} />
            )}
        </div>
    );
}
```

#### Plot Controls Component

```jsx
function PlotControls({ visible, controls, plotId }) {
    return (
        <div className={`plot-controls ${visible ? 'visible' : ''}`}>
            {/* Only render controls specified for this plot type */}

            {controls.includes('zoom') && (
                <button title="Zoom" onClick={() => handleZoom(plotId)}>
                    <ZoomIcon />
                </button>
            )}

            {controls.includes('pan') && (
                <button title="Pan" onClick={() => handlePan(plotId)}>
                    <PanIcon />
                </button>
            )}

            {controls.includes('reset') && (
                <button title="Reset" onClick={() => handleReset(plotId)}>
                    <ResetIcon />
                </button>
            )}

            {controls.includes('clear-brushes') && (
                <button title="Clear Selection" onClick={() => clearBrushes(plotId)}>
                    <ClearIcon />
                </button>
            )}

            {controls.includes('orbital') && (
                <button title="Orbital Control" onClick={() => toggleOrbital(plotId)}>
                    <OrbitalIcon />
                </button>
            )}

            {controls.includes('export') && (
                <ExportDropdown plotId={plotId} />
            )}

            {controls.includes('edit') && (
                <button title="Edit" onClick={() => openEditPanel(plotId)}>
                    <EditIcon />
                </button>
            )}

            {controls.includes('table') && (
                <button title="View as Table" onClick={() => showAsTable(plotId)}>
                    <TableIcon />
                </button>
            )}
        </div>
    );
}
```

#### Event Handlers Hook

```jsx
function useEventHandlers(plotType, capabilities) {
    const [hoverData, setHoverData] = useState(null);
    const [clickData, setClickData] = useState(null);
    const [selection, setSelection] = useState(null);

    const handlers = {};

    // Only attach handlers based on capabilities
    if (capabilities.hoverable) {
        handlers.onHover = (data) => {
            setHoverData(data);
            // Custom hover logic based on plot type
        };
    }

    if (capabilities.selectable) {
        if (plotType === 'parcoords') {
            // Special handling for parallel coordinates
            handlers.onBrush = (data) => {
                // Handle brush selection
            };
        } else {
            handlers.onSelection = (data) => {
                setSelection(data);
                // Handle box/lasso selection
            };
        }
    }

    if (capabilities.zoomable) {
        if (plotType === 'scatter3d') {
            // 3D plots have camera controls
            handlers.onCameraChange = (camera) => {
                // Handle 3D rotation/zoom
            };
        } else {
            handlers.onRelayout = (layout) => {
                // Handle 2D zoom/pan
            };
        }
    }

    handlers.hoverData = hoverData;
    handlers.clickData = clickData;
    handlers.selection = selection;

    return handlers;
}
```

### 5. UI Layout Architecture

#### Split Panel Design

```jsx
function App() {
    const [messages, setMessages] = useState([]);
    const [outputs, setOutputs] = useState([]);
    const ws = useWebSocket(`ws://localhost:8000/ws/${sessionId}`);

    return (
        <div className="app-container">
            {/* Left Panel - Chat (30%) */}
            <ChatPanel className="chat-panel">
                <MessageStream>
                    {messages.map(msg => (
                        <Message
                            type={msg.type}  // user, status, error, code, result
                            content={msg.content}
                        />
                    ))}
                </MessageStream>
                <ChatInput onSubmit={handleSubmit} />
            </ChatPanel>

            {/* Right Panel - Results (70%) */}
            <ResultsCanvas className="results-canvas">
                <ResultsToolbar>
                    <LayoutToggle options={['grid', 'stack', 'tabs']} />
                    <ClearButton />
                    <ExportAllButton />
                </ResultsToolbar>

                <OutputContainer layout={layoutMode}>
                    {outputs.map(output => (
                        <OutputRenderer
                            key={output.id}
                            output={output}
                        />
                    ))}
                </OutputContainer>
            </ResultsCanvas>
        </div>
    );
}
```

#### Status Messages in Chat

```jsx
function StatusMessage({ type, text }) {
    const icons = {
        'loading': '📊',
        'analyzing': '🔍',
        'generating': '⚡',
        'executing': '▶️',
        'fixing': '🔧',
        'success': '✅',
        'error': '❌'
    };

    return (
        <div className={`status-message ${type}`}>
            <span>{icons[type]}</span>
            <span>{text}</span>
        </div>
    );
}
```

### 6. CSS Layout

```css
.app-container {
    display: grid;
    grid-template-columns: minmax(350px, 30%) 1fr;
    height: 100vh;
}

.chat-panel {
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    overflow-y: auto;
}

.results-canvas {
    display: flex;
    flex-direction: column;
    background: var(--canvas-bg);
    overflow-y: auto;
}

.plot-container {
    position: relative;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 1rem;
}

.plot-controls {
    position: absolute;
    top: 10px;
    right: 10px;
    display: flex;
    gap: 8px;
    opacity: 0;
    transition: opacity 0.2s;
    z-index: 100;
}

.plot-controls.visible {
    opacity: 1;
}

.output-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
    gap: 1rem;
    padding: 1rem;
}
```

## LLM Freedom in Action

### Example: LLM Chooses Its Own Approach

These are examples of what an LLM *might* generate, not patterns it must follow:

```python
# User: "Visualize the data"
# LLM decides everything:

send_status("Analyzing data structure...")
df = pd.read_csv('data.csv')

# LLM decides what visualization makes sense
if df.select_dtypes(include='number').shape[1] == 2:
    fig = px.scatter(df, x=df.columns[0], y=df.columns[1])
    show(fig, type='plot', message='Found 2 numeric columns, showing correlation')
elif 'date' in df.columns:
    # Time series approach
    numeric_cols = df.select_dtypes(include='number').columns
    for col in numeric_cols:
        fig = px.line(df, x='date', y=col)
        show(fig, type='plot', title=f'{col} over time')

# Bar chart
fig = px.bar(df, x='category', y='value')
show(fig, plot_type='bar')

# Pie chart (no zoom controls)
fig = px.pie(df, values='count', names='category')
show(fig, plot_type='pie')

# Heatmap
fig = px.imshow(correlation_matrix)
show(fig, plot_type='heatmap')

# 3D scatter (orbital controls)
fig = px.scatter_3d(df, x='x', y='y', z='z')
show(fig, plot_type='scatter3d')

# Parallel coordinates (special brushing)
fig = go.Figure(data=go.Parcoords(
    dimensions=[
        dict(label='A', values=df['A']),
        dict(label='B', values=df['B'])
    ]
))
show(fig, plot_type='parcoords')
```

### Animated Visualizations

```python
# Animation with Plotly Express
fig = px.scatter(df, x='x', y='y',
                animation_frame='year',
                animation_group='country',
                size='population',
                color='continent',
                title='Evolution Over Time')
show(fig, plot_type='scatter')  # Frontend detects frames

# Custom animation frames
frames = []
for t in range(100):
    frames.append(go.Frame(
        data=[go.Scatter(x=df['x'], y=df['y']*t)]
    ))

fig = go.Figure(
    data=[go.Scatter(x=df['x'], y=df['y'])],
    frames=frames,
    layout=go.Layout(
        updatemenus=[{
            'type': 'buttons',
            'buttons': [
                {'label': 'Play', 'method': 'animate',
                 'args': [None, {'frame': {'duration': 50}}]}
            ]
        }]
    )
)
show(fig, plot_type='scatter')
```

### Tables and Metrics

```python
# Interactive table
show(df.head(100), sortable=True, filterable=True)

# Metrics/KPIs as HTML
revenue = df['revenue'].sum()
growth = 23.5

show(f'''
<div class="metrics-row">
    <div class="metric">
        <div class="value">${revenue:,.0f}</div>
        <div class="label">Total Revenue</div>
    </div>
    <div class="metric">
        <div class="value">{growth:.1f}%</div>
        <div class="label">Growth Rate</div>
    </div>
</div>
''')

# Text insights
show('''
<div class="insight">
    <h3>Key Findings</h3>
    <p>Sales increased 23% in Q3</p>
    <p class="warning">⚠️ West region declining</p>
</div>
''')
```

### Multiple Outputs

```python
# Multiple visualizations
df = load_data('sales.csv')

# Plot 1
fig1 = px.line(df, x='date', y='revenue')
show(fig1, plot_type='line', plot_id='revenue_trend')

# Plot 2 - linked to plot 1
fig2 = px.bar(df, x='month', y='revenue')
show(fig2, plot_type='bar', linked_to=['revenue_trend'])

# Table
top_products = df.nlargest(10, 'revenue')
show(top_products)

# Metrics
show(f'<div class="metric">{len(df)} Total Records</div>')
```

## Error Recovery Examples

### LLM Handles Errors Its Way

```python
# User request leads to an error
# LLM decides how to handle it:

try:
    fig = px.scatter(df, x='Date', y='Sales')
    show(fig)
except KeyError as e:
    send_status(f"Column not found: {e}")
    send_status("Let me check the actual column names...")
    print(df.columns.tolist())
    # LLM discovers columns are lowercase
    fig = px.scatter(df, x='date', y='sales')
    show(fig, note='Fixed column names to lowercase')

# Or LLM might choose a different approach:
send_status("Checking data types...")
for col in df.columns:
    if df[col].dtype == 'object':
        try:
            df[col] = pd.to_numeric(df[col])
            send_status(f"Converted {col} to numeric")
        except:
            pass  # Keep as string

# LLM decides recovery strategy, not the system
```

## Non-Blocking UI Architecture

### Core Principle: UI Never Freezes

The system uses async execution, progressive rendering, and Web Workers to ensure the UI remains responsive even with large datasets or complex computations.

### Backend: Async Execution with Streaming

```python
class ExecutionService:
    async def execute_streaming(self, code: str, session_id: str):
        """
        Execute code with streaming updates to prevent UI freezing.
        """
        async def run_in_thread():
            loop = asyncio.get_event_loop()

            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Stream status updates while executing
                await self.send_status("Starting execution...")

                # Load data in background
                if 'load_data' in code:
                    await self.send_status("Loading data...")
                    future = loop.run_in_executor(executor, self.load_data_with_progress)

                    # Send progress updates while loading
                    while not future.done():
                        progress = getattr(future, 'progress', 0)
                        await self.send_progress("Loading", progress)
                        await asyncio.sleep(0.1)

                    data = await future

                # Execute code in chunks
                await self.send_status("Processing...")
                result = await loop.run_in_executor(executor, exec, code, namespace)

                # For large visualizations, render progressively
                for output in outputs:
                    if output['type'] == 'plot' and self.is_large_plot(output):
                        await self.send_status(f"Rendering {output['plot_type']} plot...")
                        await self.render_progressive(output)
                    else:
                        await self.send_output(output)

                return result

    async def render_progressive(self, plot_data):
        """
        Render large plots progressively to avoid freezing.
        """
        # Send loading state immediately
        await self.send_output({
            'id': plot_data['id'],
            'type': 'plot_loading',
            'plot_type': plot_data['plot_type'],
            'message': 'Rendering visualization...'
        })

        # Stream data in chunks for very large datasets
        if len(plot_data['figure']['data'][0]['x']) > 10000:
            chunks = self.chunk_data(plot_data['figure']['data'])
            for i, chunk in enumerate(chunks):
                await self.send_partial_update({
                    'id': plot_data['id'],
                    'chunk': chunk,
                    'progress': (i + 1) / len(chunks) * 100
                })
                await asyncio.sleep(0.01)  # Yield to event loop

        # Send final plot
        await self.send_output(plot_data)
```

### Frontend: Web Workers & Progressive Rendering

```jsx
// Use Web Worker for heavy computations
class PlotWorker {
    constructor() {
        this.worker = new Worker('/plotWorker.js');
        this.worker.onmessage = this.handleMessage.bind(this);
    }

    async renderLargePlot(plotData) {
        return new Promise((resolve) => {
            this.worker.postMessage({
                type: 'render',
                data: plotData
            });

            this.worker.onmessage = (e) => {
                if (e.data.type === 'progress') {
                    this.onProgress?.(e.data.progress);
                } else if (e.data.type === 'complete') {
                    resolve(e.data.result);
                }
            };
        });
    }
}

// Progressive plot rendering with loading states
function PlotContainer({ output }) {
    const [isLoading, setIsLoading] = useState(true);
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        if (output.type === 'plot_loading') {
            return; // Show skeleton
        }

        // For large plots, render progressively
        if (isLargePlot(output)) {
            renderProgressive();
        } else {
            renderImmediate();
        }
    }, [output]);

    if (isLoading) {
        return (
            <div className="plot-skeleton">
                <div className="loading-message">
                    {output.message || 'Rendering visualization...'}
                </div>
                {progress > 0 && <ProgressBar value={progress} />}
            </div>
        );
    }

    return <PlotlyPlot data={plotData} />;
}
```

### Table Virtualization

```jsx
function DataTable({ data, columns }) {
    return (
        <AgGridReact
            rowData={data}
            columnDefs={columns}

            // Virtual scrolling - only render visible rows
            rowBuffer={10}
            rowModelType='infinite'

            // Lazy loading for huge datasets
            datasource={{
                getRows: async (params) => {
                    const response = await fetchRows(
                        params.startRow,
                        params.endRow
                    );
                    params.successCallback(
                        response.rows,
                        response.totalCount
                    );
                }
            }}

            // Non-blocking operations
            animateRows={true}
            asyncTransactionWaitMillis={50}
        />
    );
}
```

## Smart Result Management System

### LLM Natural Intent Understanding

The LLM understands intent naturally, without any prescribed patterns.

```python
class LLMOrchestrator:
    async def generate_code(self, user_request: str, context: dict):
        """
        LLM interprets request naturally and decides approach.
        """

        prompt = f"""
        User request: {user_request}
        Context: {context}

        You understand the user's intent naturally.
        Generate appropriate Python code.

        You can include any metadata with show() that helps convey your intent.
        Examples (not requirements):
        - show(fig, intent='update')  # If updating existing
        - show(fig, new_window=True)  # If user wants separate view
        - show(fig)  # If straightforward display

        You decide what makes sense based on the conversation flow.

        'update' - When user is refining or adjusting:
          - Visual properties (colors, sizes, labels)
          - Minor modifications (legend, axes)
          - Corrections ("actually", "wait", "oops")

        'replace' - When changing approach:
          - Different visualization type for same data
          - "instead", "rather", "switch to" semantics
          - Complete change in approach

        'new' - When adding or exploring:
          - Different data or analysis
          - Complementary views ("also", "additionally")
          - Comparisons needed
          - New questions

        IMPORTANT: Understand intent through meaning, not keywords!
        Consider conversation flow and context.
        """

        code = await self.llm.generate(prompt)
        return code
```

### Frontend Handles LLM Intent

```javascript
function handleOutput(output) {
    // The LLM expressed its intent through metadata
    // We interpret and act accordingly

    const intent = output.intent || output.action || 'new';

    // The frontend interprets the LLM's intent
    // Not through rigid rules, but understanding
    switch(intent) {
        case 'update':
        case 'modify':
        case 'refine':
            updateLastResult(output);
            break;

        case 'replace':
        case 'instead':
            replaceLastResult(output);
            break;

        default:
            // When in doubt, create new
            addNewResult(output);
    }

    // But the LLM can also be explicit:
    if (output.target_id) {
        // LLM specified exact target
        updateSpecificResult(output.target_id, output);
    }
}
```

### Frontend: Result History Navigation

```jsx
function ResultsCanvas() {
    const [results, setResults] = useState([]);
    const [visibleResults, setVisibleResults] = useState(new Set());
    const [historyOpen, setHistoryOpen] = useState(false);

    return (
        <div className="results-canvas">
            {/* Results History Sidebar */}
            <ResultsHistory
                isOpen={historyOpen}
                results={results}
                visibleResults={visibleResults}
                onToggleVisibility={(id) => {
                    setVisibleResults(prev => {
                        const next = new Set(prev);
                        if (next.has(id)) {
                            next.delete(id);
                        } else {
                            next.add(id);
                        }
                        return next;
                    });
                }}
            />

            {/* Main Results Area */}
            <div className="results-main">
                <ResultsToolbar>
                    <button onClick={() => setHistoryOpen(!historyOpen)}>
                        <HistoryIcon /> History ({results.length})
                    </button>
                </ResultsToolbar>

                <OutputContainer>
                    {results
                        .filter(r => visibleResults.has(r.id))
                        .map(result => (
                            <ResultCard
                                key={result.id}
                                result={result}
                                onClose={() => {
                                    // Hide but don't delete
                                    setVisibleResults(prev => {
                                        const next = new Set(prev);
                                        next.delete(result.id);
                                        return next;
                                    });
                                }}
                            />
                        ))}
                </OutputContainer>
            </div>
        </div>
    );
}

// Result History Component
function ResultsHistory({ isOpen, results, visibleResults, onToggleVisibility }) {
    const groupedResults = useMemo(() => {
        // Group by type and time
        return results.reduce((groups, result) => {
            const type = result.type;
            if (!groups[type]) groups[type] = [];
            groups[type].push(result);
            return groups;
        }, {});
    }, [results]);

    return (
        <div className={`results-history ${isOpen ? 'open' : ''}`}>
            <h3>Result History</h3>

            {Object.entries(groupedResults).map(([type, items]) => (
                <div key={type} className="history-group">
                    <h4>{type} ({items.length})</h4>
                    {items.map((item, idx) => (
                        <div
                            key={item.id}
                            className={`history-item ${visibleResults.has(item.id) ? 'visible' : ''}`}
                            onClick={() => onToggleVisibility(item.id)}
                        >
                            <span>{item.title || `${type} ${idx + 1}`}</span>
                            <span>{formatTime(item.timestamp)}</span>
                            {visibleResults.has(item.id) && <EyeIcon />}
                        </div>
                    ))}
                </div>
            ))}
        </div>
    );
}
```

### Intent Examples (Natural Understanding)

```python
# User: "Make the points bigger"
# LLM understands: Modifying existing visualization
fig = px.scatter(df, x='x', y='y', size_max=20)
show(fig, plot_type='scatter', intent='update')

# User: "Actually, show me a heatmap instead"
# LLM understands: Different visualization approach
fig = px.imshow(correlation_matrix)
show(fig, plot_type='heatmap', intent='replace')

# User: "Can you also break it down by category?"
# LLM understands: Additional analysis needed
fig2 = px.bar(df.groupby('category')['value'].sum())
show(fig2, plot_type='bar', intent='new')

# User: "Hmm, remove the gridlines, they're distracting"
# LLM understands: Minor refinement to current plot
fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
show(fig, plot_type='scatter', intent='update')

# User: "Compare Q1 and Q2 side by side"
# LLM understands: Multiple views for comparison
fig1 = px.bar(df_q1, x='region', y='sales', title='Q1')
show(fig1, plot_type='bar', intent='new')
fig2 = px.bar(df_q2, x='region', y='sales', title='Q2')
show(fig2, plot_type='bar', intent='new')
```

## WebSocket Communication Protocol

## LLM Planning and Task Management

### Core Principle: LLM Decides Everything

The LLM acts as a true orchestrator like Claude Code - it decides when to plan, when to show todos, and how to communicate progress. No hardcoded patterns or forced workflows.

### Minimal Execution Environment

```python
class ExecutionService:
    """
    Minimal execution environment - just Python + communication bridges.
    NO hardcoded file operations, NO forced patterns.
    LLM writes ALL the actual logic.
    """

    def create_namespace(self, session):
        """
        Provide only essential communication bridges to frontend.
        """

        # Bridge to frontend for status updates (LLM decides when/what)
        def send_status(message: str):
            """Send status to UI - LLM decides the message."""
            self.websocket.send_json({
                'type': 'status',
                'message': message,
                'timestamp': datetime.now()
            })

        # Bridge for todo management (optional - LLM decides if needed)
        def send_todos(todos: list):
            """Send todo list to UI - only if LLM wants to."""
            self.websocket.send_json({
                'type': 'todos',
                'items': todos
            })

        # That's it! Just bridges. LLM writes everything else.
        namespace = {
            # Standard Python libraries
            'pd': pd, 'np': np, 'px': px, 'go': go,
            'os': os, 'glob': glob, 'pathlib': Path, 're': re,
            'json': json, 'datetime': datetime,

            # Communication bridges only
            'show': show,
            'send_status': send_status,
            'send_todos': send_todos,

            # Figure management (see Figure Persistence section)
            'get_current_figure': get_current_figure,
            'update_figure': update_figure,

            # Session state
            **session.user_namespace
        }

        return namespace
```

### LLM System Prompt - Full Awareness

```python
LLM_SYSTEM_PROMPT = """
You are an autonomous, intelligent orchestrator with complete freedom.

## Your Power:
You have full Python execution capabilities and decide everything:
- What to do
- How to do it
- When to do it
- How to communicate it

## Available Bridges:
```python
show(anything, **any_metadata)  # Send output with any metadata you choose
send_status(message)  # Communicate with user
send_output(data)  # Direct output
```

## Your Freedom:
- Write ANY Python code
- Use ANY libraries available
- Implement ANY approach
- Create ANY workflow
- Handle errors YOUR way
- Organize tasks YOUR way

There are no required patterns. You decide based on context.

## Examples of Your Autonomy:

You might choose to:
- Explore first, then act
- Act immediately if you have enough info
- Create a plan with todos (if complex)
- Jump straight to implementation (if simple)
- Handle errors by trying alternatives
- Ask for clarification
- Provide multiple options

You are not following a script. You are thinking and deciding.

### When to send status updates:
- Starting significant operations
- Found something interesting
- Completed major steps
- Encountered issues
- Use your judgment - keep user informed naturally

### Status messages should be:
- Natural: "Looking for data files in your project..."
- Informative: "Found 3 CSV files, examining their structure..."
- Contextual: "Interesting! The sales data shows a seasonal pattern"
NOT robotic: ❌ "EXECUTING STEP 1" ❌ "FILE SEARCH COMPLETE"

## Examples:

### Simple request (no todos):
User: "Remove the legend"
```python
send_status("Removing the legend...")
update_figure(layout={'showlegend': False})
```

### Complex request (with todos):
User: "Analyze all CSV files and find correlations"
```python
send_status("I'll analyze all CSV files in your project. Let me start by finding them...")

todos = [
    "Search for CSV files",
    "Examine file structures",
    "Find correlations",
    "Create visualizations"
]
send_todos(todos)

send_status("Searching for CSV files...")
import glob
csv_files = glob.glob('**/*.csv', recursive=True)
send_status(f"Found {len(csv_files)} CSV files")

# Update todo
todos[0] = "✓ Search for CSV files"
send_todos(todos)
# ... continue
```

IMPORTANT:
- YOU decide when todos are needed
- YOU write the file operations code
- YOU choose when to update status
- YOU determine the workflow
- Write actual Python code, not pseudo-code
"""
```

### Frontend Todo & Status Display

```jsx
function ChatPanel() {
    const [todos, setTodos] = useState(null);  // null = no todos
    const [currentStatus, setCurrentStatus] = useState(null);

    return (
        <div className="chat-panel">
            {/* Only show todos if LLM created them */}
            {todos && <TodoList todos={todos} />}

            {/* Show status messages from LLM */}
            {currentStatus && (
                <StatusMessage message={currentStatus.message} />
            )}

            <MessageStream messages={messages} />
        </div>
    );
}
```

## Figure Persistence and Direct Updates

### Core Principle: Update Don't Recreate

Figures are stored as persistent objects that can be updated directly without recreation. This preserves zoom, pan, and selection states.

### Backend Figure Store

```python
class FigureStore:
    """
    Stores actual Plotly figure objects for direct updates.
    """
    def __init__(self):
        self.figures = {}  # fig_id -> actual figure object
        self.current_figures = []  # Stack of visible figure IDs

    def store_figure(self, fig, fig_id):
        """Store the actual figure object."""
        self.figures[fig_id] = fig
        self.current_figures.append(fig_id)
        return fig_id

    def get_figure(self, fig_id=None):
        """Get figure by ID or most recent."""
        if fig_id:
            return self.figures.get(fig_id)
        elif self.current_figures:
            return self.figures.get(self.current_figures[-1])
        return None

    def update_figure(self, fig_id, updates):
        """Apply updates to existing figure."""
        fig = self.get_figure(fig_id)
        if fig:
            if 'layout' in updates:
                fig.update_layout(**updates['layout'])
            if 'traces' in updates:
                fig.update_traces(**updates['traces'])
            return fig
        return None
```

### Enhanced Execution Namespace

```python
def create_namespace(self, session):
    figure_store = self.figure_store

    def get_current_figure():
        """Get the most recent figure for updates."""
        return figure_store.get_figure()

    def update_figure(fig_id=None, **updates):
        """Update existing figure without recreating."""
        if fig_id is None and figure_store.current_figures:
            fig_id = figure_store.current_figures[-1]

        if fig_id:
            fig = figure_store.get_figure(fig_id)
            if fig:
                # Apply updates directly
                if 'layout' in updates:
                    fig.update_layout(**updates['layout'])
                if 'traces' in updates:
                    fig.update_traces(**updates['traces'])

                # Send incremental update to frontend
                self.websocket.send_json({
                    'type': 'figure_update',
                    'fig_id': fig_id,
                    'updates': updates  # Only send changes!
                })

                send_status(f"Updated figure")
                return fig

        send_status("No figure to update")
        return None

    def show(obj, plot_type=None, fig_id=None, **options):
        """Enhanced show that stores figures."""
        if hasattr(obj, 'to_dict'):  # Plotly figure
            if fig_id is None:
                fig_id = f"fig_{len(figure_store.figures)}"

            # Store the actual figure object
            figure_store.store_figure(obj, fig_id)

            # Send to frontend with ID
            output = {
                'type': 'plot',
                'fig_id': fig_id,  # Track for updates
                'plot_type': plot_type,
                'figure': obj.to_dict(),
                **options
            }
            self.send_output(output)
        # ... handle other types
```

### LLM Update Patterns

```python
# User: "Remove the legend"
# LLM generates:
send_status("Removing the legend...")
update_figure(layout={'showlegend': False})  # Direct update!

# User: "Make points bigger"
# LLM generates:
send_status("Increasing point size...")
fig = get_current_figure()
if fig:
    fig.update_traces(marker_size=12)
    update_figure()  # Sends update to frontend

# User: "Add trend line"
# LLM generates:
send_status("Adding trend line to the plot...")
fig = get_current_figure()
if fig:
    # Calculate trend
    x = fig.data[0]['x']
    y = fig.data[0]['y']
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)

    # Add as new trace
    fig.add_scatter(
        x=x, y=p(x),
        mode='lines',
        name='Trend',
        line=dict(color='red', dash='dash')
    )
    update_figure()  # Sends update with new trace
```

### Frontend Efficient Updates

```jsx
function PlotContainer({ output }) {
    const plotRef = useRef(null);
    const figId = output.fig_id;

    // Listen for updates to this figure
    useEffect(() => {
        const handleUpdate = (event) => {
            if (event.detail.fig_id === figId) {
                // Use Plotly.react() for efficient updates!
                if (event.detail.updates) {
                    // Incremental update
                    if (event.detail.updates.layout) {
                        Plotly.relayout(plotRef.current, event.detail.updates.layout);
                    }
                    if (event.detail.updates.traces) {
                        Plotly.restyle(plotRef.current, event.detail.updates.traces);
                    }
                } else {
                    // Full update
                    Plotly.react(
                        plotRef.current,
                        event.detail.figure.data,
                        event.detail.figure.layout
                    );
                }
            }
        };

        window.addEventListener('figure-update', handleUpdate);
        return () => window.removeEventListener('figure-update', handleUpdate);
    }, [figId]);

    // Initial render
    useEffect(() => {
        Plotly.newPlot(plotRef.current, output.figure.data, output.figure.layout);
    }, []);

    return <div ref={plotRef} />;
}
```

### Update Decision Matrix

```python
LLM_UPDATE_GUIDANCE = """
## When to Update vs Recreate:

### Direct Update (Preferred):
- Visual properties: colors, sizes, fonts
- Show/hide elements: legend, grid, axes
- Add annotations or shapes
- Add new traces to existing plot
```python
update_figure(layout={'showlegend': False})
update_figure(traces={'marker_color': 'blue'})
```

### Recreate (Only when necessary):
- Completely different visualization type
- Different data source
- Major structural changes
```python
fig = px.scatter(new_df, x='new_x', y='new_y')
show(fig, intent='replace')
```

ALWAYS prefer updating when possible - it preserves user interactions!
"""
```

### Flexible Communication Protocol

```javascript
// The protocol is simple and flexible
// LLM decides what messages to send

class WebSocketHandler {
    handleMessage(message) {
        // The LLM sent this message
        // We handle whatever it contains

        if (message.type) {
            // LLM specified a type
            this.handleTypedMessage(message);
        } else if (message.output) {
            // Direct output
            this.displayOutput(message.output);
        } else if (message.status) {
            // Status update
            this.showStatus(message.status);
        } else {
            // LLM sent something custom
            this.handleCustom(message);
        }
    }

    // The protocol adapts to what the LLM sends
    // Not the other way around
}

// Example flow with progress
ws.send({ type: 'execute', code: userRequest });

// Detailed status with progress
ws.onmessage = (msg) => {
    switch(msg.type) {
        case 'status_detailed':
            showStatus({
                text: msg.text,
                progress: msg.progress,
                operation: msg.operation,  // 'loading', 'processing', 'rendering'
                eta: msg.eta
            });
            break;

        case 'output_update':
            // Respect LLM's intent decision
            updateExistingResult(msg.targetId, msg.data);
            break;

        case 'output_new':
            // Create new result
            addNewResult(msg.data);
            break;

        case 'progress':
            updateProgressBar(msg.progress, msg.message);
            break;
    }
};
```

## Migration Strategy

### Phase 1: Core Infrastructure (Week 1)
1. Implement `show()` function in execution service
2. Set up WebSocket communication
3. Create output collector system
4. Test with basic visualizations

### Phase 2: LLM Integration (Week 2)
1. Update prompts to use `show()` with plot types
2. Implement error recovery system
3. Add automatic fix generation
4. Test error recovery with common mistakes

### Phase 3: Frontend Components (Week 3)
1. Build split-panel UI layout
2. Implement PlotContainer with type-based controls
3. Add OutputRenderer for all types
4. Create status message system

### Phase 4: Plot Capabilities (Week 4)
1. Implement plot type detection
2. Add capability-based controls
3. Implement special handlers (PCP, 3D, etc.)
4. Test with all plot types

### Phase 5: Polish & Testing (Week 5)
1. Add animations support
2. Implement table interactions
3. Add export functionality
4. Comprehensive testing

## Key Design Decisions

### Why Explicit Plot Types?
- **LLM knows what it's creating** - no guessing needed
- **Predictable behavior** - correct controls for each type
- **Simple patterns** - `show(fig, plot_type='scatter')`
- **Fallback available** - can still auto-detect if needed

### Why show() Method?
- **Universal interface** - one function for all outputs
- **Clean code** - no complex registration
- **Flexible** - can add options without breaking changes
- **LLM-friendly** - simple pattern to learn

### Why Split Panel UI?
- **Clear separation** - chat vs results
- **Professional** - similar to Jupyter Lab
- **Persistent results** - outputs don't disappear
- **Status visibility** - see what's happening

### Why Automatic Error Recovery?
- **Better UX** - users get results, not errors
- **Learning opportunity** - LLM improves from errors
- **Common mistakes** - most errors are trivial (column names)
- **Transparent** - users see fixing attempts

## Success Metrics

1. **Simplicity**: Single `show()` function for all outputs
2. **Consistency**: Every plot gets appropriate controls
3. **Reliability**: 80%+ errors fixed automatically
4. **Performance**: <100ms to display outputs
5. **Flexibility**: Support for static, animated, and interactive content

## Technology Stack

### Backend
- **FastAPI**: Web framework with WebSocket support
- **Python 3.11+**: Execution environment
- **Pandas/NumPy**: Data manipulation
- **Plotly**: Primary visualization library

### Frontend
- **React 18**: UI framework
- **react-plotly.js**: Plotly rendering
- **AG-Grid**: Data tables
- **WebSocket**: Real-time communication

### LLM
- **OpenAI GPT-4**: Primary LLM
- **Claude**: Alternative LLM
- **Temperature**: 0.3 for code fixes, 0.7 for generation

## Session Management & Authentication

### Core Concept: Session Isolation

Each user has isolated sessions where the LLM operates independently. The LLM doesn't know about other sessions - it has its own persistent context within each session.

### Authentication Layer (Simple, Separate)

```python
# Simple auth - not LLM's concern
class AuthService:
    async def login(username, password) -> user_id
    async def create_user(username, password) -> user_id
    async def validate_token(token) -> user_id
```

### Session Management UI

```jsx
// Sessions Page - User manages their analysis sessions
function SessionsPage({ userId }) {
    const [sessions, setSessions] = useState([]);

    return (
        <div className="sessions-container">
            <button onClick={createNewSession}>
                + New Analysis Session
            </button>

            {sessions.map(session => (
                <SessionCard
                    key={session.id}
                    session={session}
                    onOpen={() => navigate(`/session/${session.id}`)}
                    onDelete={() => deleteSession(session.id)}
                    onRename={(name) => renameSession(session.id, name)}
                >
                    <h3>{session.name || `Session ${session.created_date}`}</h3>
                    <p>Last active: {session.last_active}</p>
                    <p>{session.description}</p>
                </SessionCard>
            ))}
        </div>
    );
}
```

### Session Persistence Architecture

```python
class SessionManager:
    """
    Manages isolated LLM sessions with full persistence.
    Each session is a complete workspace with memory.
    """

    def __init__(self):
        self.active_sessions = {}

    async def create_session(self, user_id: str, name: str = None):
        session_id = generate_id()
        session = {
            'id': session_id,
            'user_id': user_id,
            'name': name or f"Session {datetime.now()}",
            'created': datetime.now(),
            'last_active': datetime.now(),

            # LLM's persistent memory for this session
            'llm_memory': {
                'conversation_history': [],
                'learned_context': {},
                'discovered_files': {},
                'created_figures': {},
                'user_preferences': {},
                'custom_functions': {},
                'execution_history': []
            },

            # Python namespace persistence
            'python_namespace': {},

            # All outputs created in this session
            'outputs': [],

            # Session-specific storage
            'storage_path': f"/sessions/{user_id}/{session_id}/"
        }

        # Persist to database
        await self.save_session(session)
        return session_id

    async def load_session(self, session_id: str):
        """
        Load complete session state from storage.
        Reconstructs entire LLM context and workspace.
        """
        session = await self.db.get_session(session_id)

        # Restore Python namespace
        namespace = self.restore_namespace(session['python_namespace'])

        # Restore LLM memory
        llm_context = session['llm_memory']

        # Session is ready to continue exactly where it left off
        return {
            'session': session,
            'namespace': namespace,
            'context': llm_context
        }

    async def save_session_state(self, session_id: str, state: dict):
        """
        Save current session state for later continuation.
        Called periodically or on-demand.
        """
        await self.db.update_session(session_id, {
            'last_active': datetime.now(),
            'llm_memory': state['llm_memory'],
            'python_namespace': self.serialize_namespace(state['namespace']),
            'outputs': state['outputs']
        })
```

### LLM Session Context

```python
class LLMSessionExecutor:
    """
    LLM operates within a session context.
    Has access to its own persistent memory.
    """

    def create_session_namespace(self, session):
        """
        Create namespace with session-specific context.
        """
        # Load session memory
        memory = session['llm_memory']

        def save_to_memory(key, value):
            """LLM can explicitly save things to remember."""
            memory[key] = value
            # Auto-persist
            self.save_session_state()

        def recall_from_memory(key):
            """LLM can recall previous discoveries."""
            return memory.get(key)

        def get_session_info():
            """LLM can know about its session context."""
            return {
                'session_name': session['name'],
                'created': session['created'],
                'previous_outputs': len(session['outputs']),
                'learned_context': memory.get('learned_context', {})
            }

        # Namespace includes session-aware functions
        namespace = {
            # Standard bridges
            'show': self.make_session_aware_show(session),
            'send_status': send_status,

            # Session-specific bridges
            'save_to_memory': save_to_memory,
            'recall_from_memory': recall_from_memory,
            'get_session_info': get_session_info,

            # Restored Python variables from last session
            **session.get('python_namespace', {})
        }

        return namespace
```

### Session-Aware Frontend

```jsx
function SessionWorkspace({ sessionId }) {
    const [session, setSession] = useState(null);
    const [outputs, setOutputs] = useState([]);

    useEffect(() => {
        // Load session and all its outputs
        loadSession(sessionId).then(data => {
            setSession(data.session);
            setOutputs(data.outputs);

            // Restore scroll position, zoom states, etc.
            restoreUIState(data.uiState);
        });
    }, [sessionId]);

    const handleSave = () => {
        // Save current state
        saveSessionState(sessionId, {
            outputs,
            uiState: captureUIState(),
            timestamp: Date.now()
        });
    };

    return (
        <div className="session-workspace">
            <SessionHeader>
                <h2>{session?.name}</h2>
                <button onClick={handleSave}>Save State</button>
                <button onClick={() => navigate('/sessions')}>
                    Switch Session
                </button>
            </SessionHeader>

            <div className="workspace-content">
                <ChatPanel sessionId={sessionId} />
                <ResultsCanvas outputs={outputs} />
            </div>
        </div>
    );
}
```

### Example: LLM Using Session Memory

```python
# User returns to a session after a week
# LLM automatically has context:

session_info = get_session_info()
send_status(f"Welcome back to {session_info['session_name']}!")
send_status(f"Last time we were analyzing {len(session_info['previous_outputs'])} datasets")

# Check what we learned before
previous_analysis = recall_from_memory('analysis_findings')
if previous_analysis:
    send_status("I remember we found some interesting patterns in the sales data...")

    # LLM can continue from where it left off
    df = recall_from_memory('main_dataframe')
    if df is not None:
        send_status("Let me continue our analysis...")
        # Continue working with the same data

# Save new discoveries
correlation_matrix = df.corr()
save_to_memory('correlation_matrix', correlation_matrix)
save_to_memory('analysis_findings', {
    'high_correlations': [...],
    'outliers_detected': [...],
    'timestamp': datetime.now()
})
```

## What Makes This Different

### Traditional Approach vs. Our Approach

#### Traditional (What We're NOT Doing):
```python
class DataAnalyzer:
    def analyze_csv(self, filepath):
        # Hardcoded workflow
        df = self.load_data(filepath)
        summary = self.generate_summary(df)
        plot = self.create_default_plot(df)
        return self.format_output(summary, plot)

    def handle_error(self, error):
        # Predefined error handling
        if error.type == 'FileNotFound':
            return self.file_not_found_handler()
        # More rigid patterns...
```

#### Our Approach (LLM Freedom):
```python
# The system provides:
def show(anything, **whatever_metadata_llm_wants):
    pass  # Just a bridge

# The LLM writes everything:
# (This code is generated by LLM, not predefined)
import pandas as pd
import numpy as np

send_status("Hmm, let me explore what data you have...")
import glob
files = glob.glob('**/*.csv', recursive=True)

if not files:
    send_status("No CSV files found. Let me check for other formats...")
    files = glob.glob('**/*.xlsx', recursive=True)
    # LLM decides the workflow

# LLM implements its own approach
for file in files[:3]:  # LLM decided to sample first 3
    df = pd.read_csv(file)
    if 'revenue' in df.columns:  # LLM's decision
        # LLM's custom analysis
        trend = df.groupby('date')['revenue'].sum()
        show(trend, type='analysis', name=file)

# No predetermined patterns!
```

### Key Differences:

1. **No Preset Workflows**: Traditional systems have analyze(), visualize(), export() methods. We have just show() and send_status().

2. **No Error Templates**: Traditional systems have error handlers. Our LLM writes its own error handling inline.

3. **No Fixed Patterns**: Traditional systems enforce patterns like MVC, Repository, Service layers. Our LLM creates its own patterns.

4. **No Type Restrictions**: Traditional systems have strict typing (PlotType.SCATTER). Our LLM sends whatever metadata it wants.

5. **No Configuration**: Traditional systems have config files, settings, options. Our LLM decides everything in code.

## Web Fetching Capability

### Core Principle: LLM Writes All Fetch Code

Just like file operations, web fetching is not hardcoded. The LLM writes actual Python code to fetch, parse, and process web content as needed.

### Minimal Bridge Approach

```python
class ExecutionService:
    def create_namespace(self, session):
        """
        Provide standard Python libraries - LLM writes fetch logic.
        NO hardcoded fetch_web() functions!
        """
        namespace = {
            # Standard libraries for web operations
            'requests': requests,
            'urllib': urllib,
            'bs4': BeautifulSoup,  # If available
            'aiohttp': aiohttp,    # For async fetching

            # Data processing
            'pd': pd,
            'json': json,

            # Communication bridges (as before)
            'show': show,
            'send_status': send_status,

            # Everything else
            **session.user_namespace
        }

        return namespace
```

### LLM Web Fetching Patterns

```python
# User: "Get the latest stock prices for AAPL"
# LLM generates actual fetching code:

send_status("Fetching latest AAPL stock data...")

import requests
import json

# LLM writes the actual API call
response = requests.get(
    'https://api.example.com/stock/AAPL',
    headers={'Accept': 'application/json'}
)

if response.status_code == 200:
    data = response.json()
    send_status(f"Got AAPL price: ${data['price']}")

    # Convert to DataFrame
    df = pd.DataFrame([data])
    show(df)
else:
    send_status(f"Failed to fetch: {response.status_code}")

# User: "Scrape the table from this Wikipedia page"
# LLM generates web scraping code:

send_status("Fetching Wikipedia page...")

import requests
from bs4 import BeautifulSoup

url = 'https://en.wikipedia.org/wiki/List_of_countries_by_GDP'
response = requests.get(url)

if response.status_code == 200:
    send_status("Parsing HTML content...")
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the first table
    table = soup.find('table', class_='wikitable')

    if table:
        # Extract data from table
        headers = [th.text.strip() for th in table.find_all('th')]
        rows = []
        for tr in table.find_all('tr')[1:]:
            cells = [td.text.strip() for td in tr.find_all('td')]
            if cells:
                rows.append(cells)

        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers[:len(rows[0])])
        send_status(f"Extracted table with {len(df)} rows")
        show(df)

        # Visualize
        fig = px.bar(df.head(20), x='Country', y='GDP')
        show(fig, plot_type='bar')
    else:
        send_status("No table found on page")

# User: "Monitor this API endpoint every 5 seconds"
# LLM generates monitoring code:

send_status("Starting API monitoring...")

import time
import requests

updates = []
for i in range(10):  # Monitor for 50 seconds
    response = requests.get('https://api.example.com/status')
    if response.status_code == 200:
        data = response.json()
        updates.append({
            'timestamp': time.time(),
            'value': data['value']
        })
        send_status(f"Update {i+1}: {data['value']}")

        # Show live updating plot
        df = pd.DataFrame(updates)
        fig = px.line(df, x='timestamp', y='value', title='Live Data')
        show(fig, plot_type='line', intent='update')

        time.sleep(5)

send_status("Monitoring complete")
```

### LLM Guidance for Web Operations

```python
WEB_FETCHING_GUIDANCE = """
## Web Fetching Guidelines:

You have full Python capabilities for web operations:
- requests: HTTP requests
- urllib: URL handling
- BeautifulSoup: HTML parsing (if available)
- json: Parse JSON responses
- aiohttp: Async requests (if needed)

### Common Patterns:

1. **REST API calls**:
```python
response = requests.get(url, headers={...}, params={...})
data = response.json()
```

2. **Web scraping**:
```python
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
elements = soup.find_all('div', class_='data')
```

3. **Error handling**:
```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    send_status(f"Request failed: {e}")
```

4. **Rate limiting**:
```python
import time
for url in urls:
    response = requests.get(url)
    # Process...
    time.sleep(1)  # Be respectful
```

IMPORTANT:
- YOU write the actual fetching code
- Handle errors gracefully
- Respect rate limits
- Validate data before processing
- Always inform user of progress
"""
```

## Intelligent Adaptive Execution

### Core Principle: Natural Workflow, No Forced Patterns

The LLM intelligently decides when exploration is needed versus when to act directly. No hardcoded rounds, no forced exploration patterns - just natural, context-aware decision making.

### Adaptive Decision Making

```python
class LLMOrchestrator:
    async def process_with_intelligence(self, user_request: str, context: dict):
        """
        LLM decides its own workflow based on context and request.
        NO FORCED PATTERNS - natural intelligence.
        """

        prompt = f"""
        User request: {user_request}

        Context:
        - Available data: {context.get('known_files', [])}
        - Previous operations: {context.get('history', [])}
        - Current state: {context.get('current_state')}

        ## Intelligent Decision Making:

        Decide naturally what approach to take:

        1. **Direct Action** - When you have enough information:
           - User gives specific file/column names
           - Request is about modifying existing visualization
           - Clear, unambiguous instructions
           - You've worked with this data before

        2. **Quick Check Then Act** - When you need minimal verification:
           - Verify file exists before loading
           - Check column names before plotting
           - One simple check, then proceed

        3. **Explore Then Act** - When you need understanding:
           - User says "analyze the data" without specifics
           - Multiple files to choose from
           - Need to understand data structure first
           - Looking for patterns or insights

        4. **Iterative Refinement** - When building complex analysis:
           - Start simple, add complexity based on findings
           - Each step informs the next
           - Natural progression of analysis

        ## Examples of Natural Flow:

        ### Direct action (no exploration needed):
        User: "Plot sales vs date from sales.csv"
        → Load sales.csv and create plot immediately

        ### Quick check:
        User: "Plot the revenue data"
        → Check what files contain 'revenue' → Load and plot

        ### Natural exploration:
        User: "What insights can you find?"
        → List files → Examine structure → Find patterns → Visualize findings

        ### Adaptive iteration:
        User: "Analyze customer behavior"
        → Load customer data → See segmentation opportunity → Create segments → Compare segments

        IMPORTANT:
        - Follow natural logic, not prescribed patterns
        - Explore when genuinely needed
        - Act directly when information is sufficient
        - Let the conversation flow naturally
        """

        code = await self.llm.generate(prompt)
        return code
```

### Natural Workflow Examples

```python
# User: "Remove the outliers from the plot"
# LLM: Direct action - working with existing data
send_status("Removing outliers from the current data...")
fig = get_current_figure()
# ... remove outliers and update

# User: "Analyze all the CSV files in the project"
# LLM: Natural exploration needed
send_status("Let me explore your CSV files...")
import glob
csv_files = glob.glob('**/*.csv', recursive=True)
send_status(f"Found {len(csv_files)} CSV files, examining their structure...")

for file in csv_files:
    df = pd.read_csv(file)
    send_status(f"{file}: {len(df)} rows, columns: {', '.join(df.columns[:5])}")
    # Natural decision: interesting pattern found
    if 'revenue' in df.columns and 'date' in df.columns:
        send_status(f"Found time series data in {file}, creating trend analysis...")
        # ...

# User: "Show me the temperature data"
# LLM: Quick check then act
send_status("Looking for temperature data...")
import glob
files = glob.glob('**/*temp*.csv', recursive=True)
if files:
    send_status(f"Found {files[0]}, loading...")
    df = pd.read_csv(files[0])
    # Direct to visualization
else:
    send_status("No temperature data found, searching in all CSV files...")
    # Adaptive: expand search only when needed

# User: "What's interesting in this dataset?"
# LLM: Iterative discovery based on findings
send_status("Let me explore this dataset...")
df = pd.read_csv('data.csv')
send_status(f"Dataset has {len(df)} rows and {len(df.columns)} columns")

# Natural progression based on what's found
numeric_cols = df.select_dtypes(include='number').columns
if len(numeric_cols) > 2:
    send_status("Found multiple numeric columns, checking for correlations...")
    corr = df[numeric_cols].corr()

    # Natural decision: high correlation found
    high_corr = [(i,j) for i in range(len(corr)) for j in range(i+1, len(corr))
                 if abs(corr.iloc[i,j]) > 0.7]
    if high_corr:
        send_status(f"Interesting! Found {len(high_corr)} strong correlations")
        # Visualize the interesting finding
```

### Intelligent Context Awareness

```python
ADAPTIVE_EXECUTION_PROMPT = """
## Intelligent Execution Principles:

You are an intelligent assistant that adapts naturally to each situation.

### Decision Framework:

1. **Assess Available Information**:
   - What did the user explicitly provide?
   - What do I already know from context?
   - What's the minimum I need to know?

2. **Choose Approach Naturally**:
   - Sufficient info → Act immediately
   - Missing specifics → Quick check
   - Vague request → Explore as needed
   - Complex analysis → Build iteratively

3. **Adapt As You Go**:
   - If direct approach fails → Adapt and explore
   - If exploration finds something interesting → Pursue it
   - If pattern emerges → Follow it
   - If user corrects → Adjust immediately

### Anti-Patterns to AVOID:

❌ Forced exploration rounds
❌ Unnecessary file listing when file is specified
❌ Redundant data inspection when structure is known
❌ Rigid step sequences
❌ Exploring everything when user asks for something specific

### Natural Patterns to FOLLOW:

✓ Direct action when possible
✓ Minimal verification when prudent
✓ Exploration when genuinely needed
✓ Iteration when building understanding
✓ Adaptation based on findings

Remember: Work like an intelligent human would - efficiently, adaptively, and purposefully.
"""
```

### Context Persistence for Smarter Decisions

```python
class SessionContext:
    """
    Maintains context so LLM can make smarter decisions over time.
    """
    def __init__(self):
        self.known_files = {}  # file -> structure
        self.dataframes = {}   # name -> df info
        self.figures = {}      # id -> figure info
        self.user_preferences = {}  # learned patterns

    def update_file_knowledge(self, filepath, info):
        """Remember file structures to avoid re-exploration."""
        self.known_files[filepath] = {
            'columns': info.get('columns'),
            'shape': info.get('shape'),
            'dtypes': info.get('dtypes'),
            'last_accessed': datetime.now()
        }

    def get_context_for_llm(self):
        """Provide context so LLM can make informed decisions."""
        return {
            'known_files': list(self.known_files.keys()),
            'loaded_dataframes': list(self.dataframes.keys()),
            'active_figures': list(self.figures.keys()),
            'can_skip_exploration': len(self.known_files) > 0
        }
```

### Example: Context-Aware Execution

```python
# First request in session
User: "Analyze the sales data"
# LLM: No context, needs exploration
send_status("Let me find and explore your sales data...")
files = glob.glob('**/*sales*.csv', recursive=True)
# ... explores and learns structure

# Later in same session
User: "Now show revenue by region"
# LLM: Already knows sales.csv structure, acts directly
send_status("Creating revenue by region visualization...")
# No exploration needed - uses context!
df = pd.read_csv('sales.csv')  # Already knows this file
fig = px.bar(df.groupby('region')['revenue'].sum())
show(fig, plot_type='bar')

# Even later
User: "Compare with last year"
# LLM: Knows data structure, adapts query
send_status("Adding last year comparison...")
# Direct action using learned context
```

## Centralization & Best Practices

### Critical Implementation Principles

This section defines non-negotiable centralization patterns to ensure maintainability, consistency, and scalability.

### Frontend Centralization

#### 1. Styles - Single Source of Truth

```scss
// styles/variables.scss - ALL design tokens in one place
:root {
    // Colors - semantic naming
    --color-primary: #2563eb;
    --color-primary-hover: #1d4ed8;
    --color-success: #10b981;
    --color-warning: #f59e0b;
    --color-error: #ef4444;
    --color-info: #3b82f6;

    // Backgrounds
    --bg-primary: #ffffff;
    --bg-secondary: #f9fafb;
    --bg-tertiary: #f3f4f6;
    --bg-overlay: rgba(0, 0, 0, 0.5);

    // Text
    --text-primary: #111827;
    --text-secondary: #6b7280;
    --text-tertiary: #9ca3af;
    --text-inverse: #ffffff;

    // Spacing - consistent scale
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    --spacing-2xl: 48px;

    // Typography
    --font-sans: 'Inter', -apple-system, sans-serif;
    --font-mono: 'JetBrains Mono', 'Consolas', monospace;

    --text-xs: 12px;
    --text-sm: 14px;
    --text-base: 16px;
    --text-lg: 18px;
    --text-xl: 20px;
    --text-2xl: 24px;

    // Borders
    --border-radius-sm: 4px;
    --border-radius-md: 8px;
    --border-radius-lg: 12px;
    --border-radius-full: 9999px;

    --border-width: 1px;
    --border-color: #e5e7eb;

    // Shadows
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);

    // Z-index scale
    --z-dropdown: 1000;
    --z-sticky: 1020;
    --z-fixed: 1030;
    --z-modal-backdrop: 1040;
    --z-modal: 1050;
    --z-popover: 1060;
    --z-tooltip: 1070;

    // Animations
    --transition-fast: 150ms ease;
    --transition-base: 250ms ease;
    --transition-slow: 350ms ease;
}

// styles/themes.scss - Theme variations
[data-theme="dark"] {
    --color-primary: #3b82f6;
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --text-primary: #f1f5f9;
    --border-color: #334155;
    // ... override all relevant variables
}
```

#### 2. Icons - Centralized Icon System

```jsx
// components/Icons/index.js - Single icon export point
import {
    ChartBarIcon,
    TableIcon,
    CodeIcon,
    PlayIcon,
    SaveIcon,
    TrashIcon,
    PlusIcon,
    XMarkIcon,
    ArrowPathIcon,
    // ... import all icons
} from '@heroicons/react/24/outline';

// Map semantic names to actual icons
export const Icons = {
    // Actions
    add: PlusIcon,
    delete: TrashIcon,
    save: SaveIcon,
    close: XMarkIcon,
    refresh: ArrowPathIcon,
    play: PlayIcon,

    // Data types
    plot: ChartBarIcon,
    table: TableIcon,
    code: CodeIcon,

    // Status
    loading: () => <div className="spinner" />,
    success: () => <CheckCircleIcon className="text-success" />,
    error: () => <XCircleIcon className="text-error" />,
    warning: () => <ExclamationIcon className="text-warning" />,
};

// Usage: <Icons.add /> instead of importing icons everywhere
```

#### 3. Constants - Single Configuration File

```javascript
// config/constants.js - All app constants
export const APP_CONFIG = {
    // API endpoints
    API: {
        BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
        WS_URL: process.env.REACT_APP_WS_URL || 'ws://localhost:8000',
        TIMEOUT: 30000,
    },

    // Session settings
    SESSION: {
        AUTO_SAVE_INTERVAL: 30000, // 30 seconds
        MAX_OUTPUTS: 100,
        DEFAULT_NAME: 'Untitled Analysis',
    },

    // UI settings
    UI: {
        CHAT_PANEL_WIDTH: '30%',
        RESULTS_PANEL_WIDTH: '70%',
        MAX_PLOT_SIZE: 1000000, // 1MB
        ANIMATION_DURATION: 250,
        DEBOUNCE_DELAY: 300,
    },

    // LLM settings
    LLM: {
        MAX_RETRIES: 3,
        TEMPERATURE: 0.7,
        MODEL: 'gpt-4',
    },

    // Feature flags
    FEATURES: {
        DEBUG_MODE: process.env.NODE_ENV === 'development',
        MULTI_MODEL: false,
        EXPORT_ENABLED: true,
    }
};
```

#### 4. Component Library - Reusable UI Components

```jsx
// components/UI/index.js - Base components
export { Button } from './Button';
export { Input } from './Input';
export { Card } from './Card';
export { Modal } from './Modal';
export { Tooltip } from './Tooltip';
export { Spinner } from './Spinner';

// components/UI/Button.jsx - Example component
import { forwardRef } from 'react';
import { clsx } from 'clsx';

export const Button = forwardRef(({
    variant = 'primary',
    size = 'md',
    disabled = false,
    loading = false,
    icon,
    children,
    className,
    ...props
}, ref) => {
    return (
        <button
            ref={ref}
            disabled={disabled || loading}
            className={clsx(
                'btn',
                `btn-${variant}`,
                `btn-${size}`,
                {
                    'btn-loading': loading,
                    'btn-disabled': disabled,
                },
                className
            )}
            {...props}
        >
            {loading && <Icons.loading />}
            {icon && <span className="btn-icon">{icon}</span>}
            {children}
        </button>
    );
});
```

### Backend Centralization

#### 1. Bridge Functions - Single Module

```python
# bridges.py - ALL bridge functions in one place
from typing import Any, Dict, Optional

class BridgeRegistry:
    """Centralized bridge function registry."""

    def __init__(self, session_manager, websocket):
        self.session = session_manager
        self.ws = websocket

    def get_bridges(self, session_id: str) -> Dict[str, callable]:
        """Return all bridge functions for a session."""

        def show(data: Any, **metadata) -> None:
            """Universal output bridge."""
            self.ws.send_output(session_id, data, metadata)

        def send_status(message: str) -> None:
            """Status update bridge."""
            self.ws.send_status(session_id, message)

        def save_to_memory(key: str, value: Any) -> None:
            """Session memory bridge."""
            self.session.save_memory(session_id, key, value)

        def recall_from_memory(key: str) -> Any:
            """Memory recall bridge."""
            return self.session.get_memory(session_id, key)

        def get_session_info() -> Dict:
            """Session info bridge."""
            return self.session.get_info(session_id)

        def request_user_input(prompt: str, options: Optional[list] = None):
            """User input bridge."""
            return self.ws.request_input(session_id, prompt, options)

        return {
            'show': show,
            'send_status': send_status,
            'save_to_memory': save_to_memory,
            'recall_from_memory': recall_from_memory,
            'get_session_info': get_session_info,
            'request_user_input': request_user_input,
        }
```

#### 2. Configuration - Environment-Based

```python
# config.py - Centralized configuration
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings from environment."""

    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost/dbname"
    REDIS_URL: Optional[str] = None

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list = ["http://localhost:3000"]

    # Session Settings
    SESSION_TIMEOUT: int = 3600  # 1 hour
    SESSION_AUTO_SAVE_INTERVAL: int = 30  # seconds
    MAX_SESSION_SIZE: int = 104857600  # 100MB

    # LLM Settings
    OPENAI_API_KEY: str
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4000

    # Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 86400  # 24 hours

    # Storage
    STORAGE_TYPE: str = "local"  # or "s3"
    STORAGE_PATH: str = "./storage"
    AWS_S3_BUCKET: Optional[str] = None

    # Execution Limits
    EXECUTION_TIMEOUT: int = 60  # seconds
    EXECUTION_MEMORY_LIMIT: int = 536870912  # 512MB

    class Config:
        env_file = ".env"
        case_sensitive = True

# Single instance
settings = Settings()
```

#### 3. Error Handling - Centralized

```python
# exceptions.py - Custom exception hierarchy
class AppException(Exception):
    """Base application exception."""
    status_code = 500
    message = "Internal server error"

class SessionException(AppException):
    """Session-related exceptions."""
    status_code = 400

class ExecutionException(AppException):
    """Code execution exceptions."""
    status_code = 422

class LLMException(AppException):
    """LLM-related exceptions."""
    status_code = 503

# error_handler.py - Centralized error handling
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

async def app_exception_handler(request: Request, exc: AppException):
    """Handle all application exceptions consistently."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc),
            "detail": getattr(exc, 'detail', None)
        }
    )
```

#### 4. Utilities - Shared Functions

```python
# utils.py - Shared utility functions
import hashlib
import uuid
from datetime import datetime

def generate_session_id() -> str:
    """Generate unique session ID."""
    return f"session_{uuid.uuid4().hex[:12]}"

def generate_output_id() -> str:
    """Generate unique output ID."""
    return f"output_{uuid.uuid4().hex[:8]}"

def serialize_datetime(dt: datetime) -> str:
    """Serialize datetime for JSON."""
    return dt.isoformat()

def hash_content(content: str) -> str:
    """Generate content hash for caching."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]

def truncate_output(data: Any, max_size: int = 1000000) -> Any:
    """Truncate large outputs for transmission."""
    # Implementation here
    pass
```

### Project Structure

```
project/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UI/           # Base components
│   │   │   ├── Icons/        # Icon system
│   │   │   ├── Session/      # Session-specific
│   │   │   └── Plot/         # Plot-specific
│   │   ├── styles/
│   │   │   ├── variables.scss
│   │   │   ├── themes.scss
│   │   │   ├── components.scss
│   │   │   └── index.scss
│   │   ├── config/
│   │   │   ├── constants.js
│   │   │   └── routes.js
│   │   ├── hooks/           # Custom React hooks
│   │   ├── utils/           # Utility functions
│   │   └── services/        # API services
│   └── public/
│
├── backend/
│   ├── core/
│   │   ├── config.py        # Settings
│   │   ├── bridges.py       # Bridge functions
│   │   ├── exceptions.py    # Error types
│   │   └── utils.py         # Utilities
│   ├── session/
│   │   ├── manager.py       # Session management
│   │   └── storage.py       # Persistence
│   ├── execution/
│   │   └── executor.py      # Code execution
│   ├── api/
│   │   ├── server.py        # FastAPI app
│   │   ├── routes/          # API routes
│   │   └── middleware/      # Middleware
│   └── requirements.txt
│
├── docker-compose.yml
├── .env.example
└── README.md
```

### Development Rules

1. **Never hardcode values** - Use constants.js or config.py
2. **Never inline styles** - Use CSS variables
3. **Never import icons directly** - Use Icons object
4. **Never duplicate components** - Use UI library
5. **Never scatter bridge functions** - Use BridgeRegistry
6. **Never ignore errors** - Use exception hierarchy
7. **Never mix concerns** - Keep separation clear

## Comprehensive Logging & Debugging Strategy

### Core Principle: Visibility Into Everything

During development, logging is critical for understanding:
- What the LLM is generating
- How code is being executed
- What errors are occurring
- Performance bottlenecks
- User behavior patterns

### Backend Logging Architecture

#### 1. Structured Logging with Context

```python
# core/logging_config.py
import logging
import json
from datetime import datetime
from contextvars import ContextVar
from pythonjsonlogger import jsonlogger

# Context variables for request tracking
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
session_id_var: ContextVar[str] = ContextVar('session_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')

class ContextFilter(logging.Filter):
    """Add context variables to all log records."""
    def filter(self, record):
        record.request_id = request_id_var.get()
        record.session_id = session_id_var.get()
        record.user_id = user_id_var.get()
        record.timestamp = datetime.utcnow().isoformat()
        return True

def setup_logging(level=logging.INFO, json_format=True):
    """Configure structured logging for the application."""

    if json_format:
        # Production: JSON logs for parsing
        formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s',
            rename_fields={'levelname': 'level', 'name': 'logger'}
        )
    else:
        # Development: Human-readable logs
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)8s] [%(name)20s] '
            '[req:%(request_id)s] [sess:%(session_id)s] - %(message)s'
        )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(ContextFilter())

    # File handler for persistent logs
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(ContextFilter())

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    return root_logger

# Usage
logger = logging.getLogger(__name__)
```

#### 2. Logging Categories & Levels

```python
# core/loggers.py
import logging

# Specialized loggers for different components
llm_logger = logging.getLogger('llm')         # LLM interactions
exec_logger = logging.getLogger('execution')  # Code execution
ws_logger = logging.getLogger('websocket')    # WebSocket messages
db_logger = logging.getLogger('database')     # Database queries
api_logger = logging.getLogger('api')         # API requests/responses
perf_logger = logging.getLogger('performance')# Performance metrics

# Log levels by environment
LOG_LEVELS = {
    'development': {
        'llm': logging.DEBUG,        # See all LLM prompts and responses
        'execution': logging.DEBUG,   # See all executed code
        'websocket': logging.DEBUG,   # See all WebSocket messages
        'database': logging.INFO,     # See queries but not results
        'api': logging.DEBUG,         # See all API traffic
        'performance': logging.INFO   # Basic performance metrics
    },
    'production': {
        'llm': logging.INFO,          # Only important LLM events
        'execution': logging.WARNING, # Only execution errors
        'websocket': logging.INFO,    # Connection events
        'database': logging.WARNING,  # Only slow queries
        'api': logging.INFO,          # Request/response summary
        'performance': logging.INFO   # All performance metrics
    }
}
```

#### 3. LLM Interaction Logging

```python
# llm/orchestrator.py
import time
import hashlib

class LLMOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger('llm')

    async def generate_code(self, prompt: str, context: dict) -> str:
        """Generate code with comprehensive logging."""

        # Generate request ID for tracking
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]

        # Log the request
        self.logger.info("LLM request initiated", extra={
            'prompt_hash': prompt_hash,
            'prompt_length': len(prompt),
            'context_keys': list(context.keys()),
            'model': self.model_name
        })

        # Log full prompt in debug mode
        self.logger.debug("Full prompt", extra={
            'prompt': prompt,
            'context': context
        })

        start_time = time.time()

        try:
            # Make LLM call
            response = await self.llm.generate(prompt)

            # Log successful response
            duration = time.time() - start_time
            self.logger.info("LLM response received", extra={
                'prompt_hash': prompt_hash,
                'duration_seconds': duration,
                'response_length': len(response),
                'tokens_used': response.get('usage', {})
            })

            # Log generated code for debugging
            self.logger.debug("Generated code", extra={
                'prompt_hash': prompt_hash,
                'code': response
            })

            return response

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error("LLM generation failed", extra={
                'prompt_hash': prompt_hash,
                'error': str(e),
                'error_type': type(e).__name__,
                'duration_seconds': duration
            }, exc_info=True)
            raise
```

#### 4. Code Execution Logging

```python
# execution/executor.py
class CodeExecutor:
    def __init__(self):
        self.logger = logging.getLogger('execution')

    def execute(self, code: str, session_id: str):
        """Execute code with detailed logging."""

        exec_id = f"exec_{uuid.uuid4().hex[:8]}"

        # Log code to be executed
        self.logger.info("Code execution started", extra={
            'exec_id': exec_id,
            'code_length': len(code),
            'code_lines': code.count('\n') + 1
        })

        # Log actual code in debug
        self.logger.debug("Executing code", extra={
            'exec_id': exec_id,
            'code': code
        })

        start_time = time.time()

        try:
            # Execute with output capture
            result = self._execute_with_timeout(code, timeout=30)

            duration = time.time() - start_time
            self.logger.info("Code execution successful", extra={
                'exec_id': exec_id,
                'duration_seconds': duration,
                'output_length': len(str(result.get('output', '')))
            })

            return result

        except TimeoutError:
            self.logger.error("Code execution timeout", extra={
                'exec_id': exec_id,
                'timeout_seconds': 30,
                'code_preview': code[:200]
            })
            raise

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error("Code execution failed", extra={
                'exec_id': exec_id,
                'error': str(e),
                'error_type': type(e).__name__,
                'duration_seconds': duration,
                'code_preview': code[:200]
            }, exc_info=True)
            raise
```

#### 5. WebSocket Message Logging

```python
# api/websocket_handler.py
class WebSocketHandler:
    def __init__(self):
        self.logger = logging.getLogger('websocket')

    async def handle_message(self, websocket, session_id: str):
        """Handle WebSocket messages with logging."""

        msg_count = 0

        try:
            async for message in websocket:
                msg_count += 1
                msg_id = f"msg_{session_id}_{msg_count}"

                # Log received message
                self.logger.debug("WebSocket message received", extra={
                    'msg_id': msg_id,
                    'message_type': message.get('type'),
                    'message_size': len(json.dumps(message))
                })

                # Process message
                response = await self.process_message(message)

                # Log response
                self.logger.debug("WebSocket response sent", extra={
                    'msg_id': msg_id,
                    'response_type': response.get('type'),
                    'response_size': len(json.dumps(response))
                })

                await websocket.send_json(response)

        except WebSocketDisconnect:
            self.logger.info("WebSocket disconnected", extra={
                'session_id': session_id,
                'messages_processed': msg_count
            })
```

### Frontend Logging

#### 1. Console Logger with Levels

```javascript
// utils/logger.js
const LOG_LEVELS = {
    DEBUG: 0,
    INFO: 1,
    WARN: 2,
    ERROR: 3
};

const CURRENT_LEVEL = process.env.NODE_ENV === 'development'
    ? LOG_LEVELS.DEBUG
    : LOG_LEVELS.INFO;

class Logger {
    constructor(name) {
        this.name = name;
        this.context = {};
    }

    setContext(context) {
        this.context = { ...this.context, ...context };
    }

    _log(level, message, data = {}) {
        if (LOG_LEVELS[level] < CURRENT_LEVEL) return;

        const timestamp = new Date().toISOString();
        const logData = {
            timestamp,
            level,
            logger: this.name,
            message,
            ...this.context,
            ...data
        };

        // Console output
        const consoleMethod = level.toLowerCase();
        console[consoleMethod](`[${timestamp}] [${this.name}] ${message}`, logData);

        // Send to backend in production
        if (process.env.NODE_ENV === 'production') {
            this.sendToBackend(logData);
        }
    }

    async sendToBackend(logData) {
        try {
            await fetch('/api/logs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(logData)
            });
        } catch (error) {
            console.error('Failed to send logs to backend', error);
        }
    }

    debug(message, data) { this._log('DEBUG', message, data); }
    info(message, data) { this._log('INFO', message, data); }
    warn(message, data) { this._log('WARN', message, data); }
    error(message, data) { this._log('ERROR', message, data); }
}

// Create specialized loggers
export const wsLogger = new Logger('WebSocket');
export const llmLogger = new Logger('LLM');
export const uiLogger = new Logger('UI');
export const perfLogger = new Logger('Performance');
```

#### 2. WebSocket Communication Logging

```javascript
// services/websocket.js
import { wsLogger } from '../utils/logger';

class WebSocketService {
    connect(sessionId) {
        wsLogger.info('Connecting to WebSocket', { sessionId });

        this.ws = new WebSocket(WS_URL);

        this.ws.onopen = () => {
            wsLogger.info('WebSocket connected', { sessionId });
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            wsLogger.debug('Message received', {
                type: data.type,
                size: event.data.length
            });

            // Process message
            this.handleMessage(data);
        };

        this.ws.onerror = (error) => {
            wsLogger.error('WebSocket error', { error: error.message });
        };
    }

    send(message) {
        const msgId = Date.now();
        wsLogger.debug('Sending message', {
            msgId,
            type: message.type,
            size: JSON.stringify(message).length
        });

        this.ws.send(JSON.stringify(message));
    }
}
```

#### 3. Performance Monitoring

```javascript
// utils/performance.js
import { perfLogger } from '../utils/logger';

export function measurePerformance(name, fn) {
    return async (...args) => {
        const start = performance.now();

        try {
            const result = await fn(...args);
            const duration = performance.now() - start;

            perfLogger.info(`${name} completed`, {
                duration_ms: duration,
                success: true
            });

            // Alert if slow
            if (duration > 1000) {
                perfLogger.warn(`${name} slow performance`, {
                    duration_ms: duration,
                    threshold_ms: 1000
                });
            }

            return result;
        } catch (error) {
            const duration = performance.now() - start;
            perfLogger.error(`${name} failed`, {
                duration_ms: duration,
                error: error.message
            });
            throw error;
        }
    };
}

// Usage
const processMessage = measurePerformance('processMessage',
    async (message) => {
        // Process message
    }
);
```

### Development Tools

#### 1. Debug Dashboard

```python
# api/debug_routes.py
from fastapi import APIRouter

debug_router = APIRouter(prefix="/debug")

@debug_router.get("/logs")
async def get_recent_logs(
    level: str = "INFO",
    logger_name: str = None,
    session_id: str = None,
    limit: int = 100
):
    """Get recent logs for debugging."""
    # Query logs from file or database
    pass

@debug_router.get("/sessions/{session_id}/timeline")
async def get_session_timeline(session_id: str):
    """Get complete timeline of session events."""
    # Return all events for debugging
    pass

@debug_router.get("/performance")
async def get_performance_metrics():
    """Get performance metrics."""
    return {
        "llm_avg_response_time": metrics.llm_response_time,
        "execution_avg_time": metrics.execution_time,
        "active_sessions": len(active_sessions),
        "total_requests": metrics.total_requests
    }
```

#### 2. Log Viewer UI

```jsx
// components/DebugPanel/LogViewer.jsx
function LogViewer() {
    const [logs, setLogs] = useState([]);
    const [filter, setFilter] = useState({
        level: 'INFO',
        logger: 'all'
    });

    useEffect(() => {
        // Connect to log stream
        const eventSource = new EventSource('/api/debug/log-stream');

        eventSource.onmessage = (event) => {
            const log = JSON.parse(event.data);
            setLogs(prev => [...prev, log].slice(-1000)); // Keep last 1000
        };

        return () => eventSource.close();
    }, []);

    return (
        <div className="log-viewer">
            <LogFilters filter={filter} onChange={setFilter} />

            <div className="log-list">
                {logs
                    .filter(log => matchesFilter(log, filter))
                    .map((log, i) => (
                        <LogEntry key={i} log={log} />
                    ))
                }
            </div>
        </div>
    );
}
```

### Log Aggregation & Analysis

#### 1. Centralized Log Storage

```python
# core/log_storage.py
from elasticsearch import Elasticsearch

class LogStorage:
    def __init__(self):
        self.es = Elasticsearch(['localhost:9200'])

    async def store_log(self, log_entry):
        """Store log in Elasticsearch for analysis."""
        await self.es.index(
            index=f"logs-{datetime.now():%Y.%m.%d}",
            body=log_entry
        )

    async def search_logs(self, query, time_range='1h'):
        """Search logs for debugging."""
        return await self.es.search(
            index="logs-*",
            body={
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"message": query}},
                            {"range": {"timestamp": {"gte": f"now-{time_range}"}}}
                        ]
                    }
                }
            }
        )
```

#### 2. Error Tracking

```python
# core/error_tracking.py
import sentry_sdk

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENVIRONMENT,
    before_send=lambda event, hint: filter_sensitive_data(event)
)

def track_error(error, context=None):
    """Track errors with context for debugging."""
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)

        # Add session context
        scope.set_context("session", {
            "id": session_id_var.get(),
            "user_id": user_id_var.get()
        })

        sentry_sdk.capture_exception(error)
```

### Development Debug Mode

```python
# config.py
class Settings(BaseSettings):
    # Debug settings
    DEBUG_MODE: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_LLM_PROMPTS: bool = False
    LOG_EXECUTION_CODE: bool = False
    LOG_WS_MESSAGES: bool = False
    SAVE_DEBUG_ARTIFACTS: bool = False

    # Development helpers
    SLOW_QUERY_THRESHOLD: float = 1.0  # seconds
    PROFILE_REQUESTS: bool = False
    TRACE_MEMORY: bool = False

# When DEBUG_MODE is enabled:
if settings.DEBUG_MODE:
    # Save all LLM prompts and responses
    # Save all executed code
    # Log all WebSocket messages
    # Enable profiling
    # Save execution artifacts
```

### Best Practices

1. **Always log with context** - Include session_id, user_id, request_id
2. **Use structured logging** - JSON format for parsing
3. **Log at appropriate levels** - DEBUG for development, INFO for production
4. **Include timing information** - Measure and log performance
5. **Sanitize sensitive data** - Never log passwords, tokens, API keys
6. **Correlate related events** - Use request IDs to track flow
7. **Monitor log volume** - Rotate and archive logs appropriately
8. **Make logs actionable** - Include enough context to debug issues

## Future Enhancements & Suggestions

### 1. Bidirectional Communication
Allow LLM to request user input when needed:

```python
# Add to bridge functions (fixed, not LLM-created)
def request_user_input(prompt, options=None):
    """LLM can ask user for clarification."""
    return websocket.request_input({
        'prompt': prompt,
        'options': options,
        'type': 'user_input'
    })

# LLM uses it when needed:
choice = request_user_input(
    "Which columns should I analyze?",
    options=['sales', 'revenue', 'profit']
)
```

### 2. Resource Awareness
Give LLM context about computational resources:

```python
# LLM receives resource context
def get_resource_info():
    return {
        'data_size_limit': '100MB',  # for now
        'execution_time_limit': 60,   # seconds
        'available_libraries': ['pandas', 'numpy', 'plotly', ...]
    }

# LLM can make informed decisions
resource_info = get_resource_info()
if file_size > resource_info['data_size_limit']:
    send_status("Large file detected, I'll sample it for analysis...")
    df = pd.read_csv(file, nrows=10000)
```

### 3. Multi-Modal Capabilities
Since LLM can analyze images:

```python
# User provides screenshot
# "Make my chart look like this image"

def analyze_image(image_path):
    """Bridge to let LLM see images."""
    # Returns image to LLM for analysis
    return load_image(image_path)

# LLM analyzes and recreates
reference_img = analyze_image('/path/to/screenshot.png')
send_status("I see you want a dark theme with gradient colors...")
# LLM recreates the style
```

### 4. Parallel Exploration
LLM can try multiple approaches:

```python
# LLM decides to explore multiple approaches
import concurrent.futures

def try_approach(approach_name, code):
    try:
        exec(code)
        return f"{approach_name}: Success"
    except Exception as e:
        return f"{approach_name}: {str(e)}"

# LLM writes parallel exploration
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = {
        executor.submit(try_approach, "correlation", correlation_code),
        executor.submit(try_approach, "regression", regression_code),
        executor.submit(try_approach, "clustering", clustering_code)
    }

    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        send_status(result)
```

### 5. Debugging Transparency
Optional debug mode for LLM reasoning:

```python
# Add debug bridge (controlled by user preference)
def send_debug(reasoning):
    """LLM can explain its thinking when debug mode is on."""
    if session.get('debug_mode'):
        websocket.send({'type': 'debug', 'reasoning': reasoning})

# LLM uses it to explain decisions
send_debug("Detected time series data due to 'date' column")
send_debug("Choosing line plot for temporal visualization")
```

### 6. Smart Frontend Interpretation

```javascript
// Frontend becomes smarter at interpreting LLM outputs
class OutputInterpreter {
    interpretMultipleOutputs(outputs) {
        // Detect relationships
        const related = this.findRelatedOutputs(outputs);

        // Auto-layout decision
        if (related.length > 1) {
            return {
                layout: 'grid',
                columns: Math.ceil(Math.sqrt(related.length)),
                linked: true
            };
        }

        // Progressive rendering for large outputs
        if (this.isLargeOutput(outputs[0])) {
            return {
                render: 'progressive',
                chunks: this.chunkData(outputs[0])
            };
        }
    }
}
```

### 7. Implementation Roadmap

#### Phase 1: MVP (Week 1-2)
- Basic authentication & login page
- Session management UI
- Simple show() bridge
- WebSocket communication
- Basic frontend display

#### Phase 2: Session Persistence (Week 3)
- Session state saving/loading
- Memory bridges for LLM
- Python namespace persistence
- Output history

#### Phase 3: Enhanced Intelligence (Week 4-5)
- Bidirectional communication
- Resource awareness
- Parallel exploration
- Debug transparency

#### Phase 4: Polish (Week 6)
- Multi-modal capabilities
- Smart frontend interpretation
- Performance optimizations
- User experience improvements

### 8. Key Design Decisions for Implementation

1. **Database Choice**: PostgreSQL for session persistence (JSON columns for flexibility)
2. **Session Storage**: S3 or local filesystem for large outputs
3. **WebSocket Library**: Socket.io for reliability and reconnection
4. **Frontend State**: Redux or Zustand for complex state management
5. **Auto-save**: Every 30 seconds or on significant changes

## Implementation Plan: From Zero to Production

### Development Setup

#### Prerequisites
```bash
# Required tools
- Node.js 18+ and npm
- Python 3.10+
- PostgreSQL 14+
- Redis (optional, for caching)
- Git
```

#### Initial Setup Steps
```bash
# 1. Create project structure
mkdir llm-orchestrator && cd llm-orchestrator
git init

# 2. Setup backend
mkdir backend && cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install fastapi uvicorn websockets pydantic sqlalchemy asyncpg
pip install openai pandas numpy plotly

# 3. Setup frontend
cd .. && npx create-react-app frontend --template typescript
cd frontend
npm install axios socket.io-client plotly.js react-plotly.js
npm install @heroicons/react clsx sass zustand

# 4. Setup database
createdb llm_orchestrator_dev
```

### Phase 0: Foundation (Days 1-3)
**Goal**: Set up the minimal working infrastructure

#### Backend Tasks
```python
# 1. Create core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://localhost/llm_orchestrator_dev"
    OPENAI_API_KEY: str
    SECRET_KEY: str = "dev-secret-key"

settings = Settings()

# 2. Create core/bridges.py - Start with minimal bridges
def get_minimal_bridges():
    def show(data, **metadata):
        print(f"OUTPUT: {data}")  # Temporary

    def send_status(message):
        print(f"STATUS: {message}")

    return {"show": show, "send_status": send_status}

# 3. Create execution/executor.py - Basic execution
import sys
from io import StringIO

def execute_code(code: str, namespace: dict):
    old_stdout = sys.stdout
    sys.stdout = output = StringIO()

    try:
        exec(code, namespace)
        return {"success": True, "output": output.getvalue()}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        sys.stdout = old_stdout

# 4. Create api/server.py - Minimal FastAPI
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Minimal WebSocket handling
```

#### Frontend Tasks
```jsx
// 1. Create config/constants.js
export const APP_CONFIG = {
    API: {
        BASE_URL: 'http://localhost:8000',
        WS_URL: 'ws://localhost:8000/ws'
    }
};

// 2. Create minimal App.tsx
import { useState, useEffect } from 'react';

function App() {
    const [connected, setConnected] = useState(false);
    const [messages, setMessages] = useState([]);

    useEffect(() => {
        const ws = new WebSocket(APP_CONFIG.API.WS_URL);
        ws.onopen = () => setConnected(true);
        // Basic connection
    }, []);

    return (
        <div>
            <h1>LLM Orchestrator</h1>
            <p>Status: {connected ? 'Connected' : 'Disconnected'}</p>
        </div>
    );
}
```

#### Testing Phase 0
```python
# tests/test_foundation.py
def test_execution():
    """Test basic code execution works."""
    result = execute_code("x = 1 + 1", {})
    assert result["success"] == True

def test_bridges():
    """Test bridge functions exist."""
    bridges = get_minimal_bridges()
    assert "show" in bridges
    assert "send_status" in bridges

# Run: pytest tests/
```

**Milestone**: Can execute Python code and connect WebSocket ✓

---

### Phase 1: LLM Integration (Days 4-7)
**Goal**: Connect LLM and enable basic orchestration

#### Tasks
```python
# 1. Create llm/orchestrator.py
import openai
from core.config import settings

class LLMOrchestrator:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    async def generate_code(self, prompt: str) -> str:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Python expert."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

# 2. Update WebSocket to handle messages
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    orchestrator = LLMOrchestrator()
    executor = CodeExecutor()

    while True:
        data = await websocket.receive_json()

        # Generate code from user input
        code = await orchestrator.generate_code(data["prompt"])

        # Execute code
        result = executor.execute(code)

        # Send back result
        await websocket.send_json({
            "type": "result",
            "data": result
        })
```

#### Frontend Integration
```jsx
// Create components/Chat.jsx
function Chat() {
    const [input, setInput] = useState('');
    const [outputs, setOutputs] = useState([]);

    const sendMessage = () => {
        ws.send(JSON.stringify({
            prompt: input
        }));
    };

    useEffect(() => {
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'result') {
                setOutputs([...outputs, data.data]);
            }
        };
    }, [outputs]);
}
```

#### Testing Phase 1
```python
# tests/test_llm.py
async def test_llm_generates_code():
    """Test LLM can generate Python code."""
    orchestrator = LLMOrchestrator()
    code = await orchestrator.generate_code("Create a list of numbers 1 to 5")
    assert "range" in code or "[1, 2, 3, 4, 5]" in code

async def test_end_to_end():
    """Test user prompt → LLM → execution → output."""
    # Simulate WebSocket message flow
    pass
```

**Milestone**: User input → LLM → Code execution → Output display ✓

---

### Phase 2: Session Management (Days 8-12)
**Goal**: Add authentication, sessions, and persistence

#### Database Setup
```sql
-- migrations/001_create_tables.sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW(),
    memory JSONB DEFAULT '{}',
    namespace JSONB DEFAULT '{}',
    outputs JSONB DEFAULT '[]'
);
```

#### Backend Implementation
```python
# auth/service.py
from passlib.context import CryptContext
import jwt

pwd_context = CryptContext(schemes=["bcrypt"])

class AuthService:
    async def create_user(self, username: str, password: str):
        hashed = pwd_context.hash(password)
        # Save to DB

    async def login(self, username: str, password: str) -> str:
        # Verify and return JWT token
        pass

# session/manager.py
class SessionManager:
    async def create_session(self, user_id: str) -> str:
        session_id = str(uuid.uuid4())
        # Save to DB
        return session_id

    async def save_state(self, session_id: str, state: dict):
        # Update DB with current state
        pass

    async def load_session(self, session_id: str) -> dict:
        # Load from DB
        pass
```

#### Frontend Auth Pages
```jsx
// pages/Login.jsx
function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = async () => {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        const { token } = await response.json();
        localStorage.setItem('token', token);
        navigate('/sessions');
    };
}

// pages/Sessions.jsx
function Sessions() {
    const [sessions, setSessions] = useState([]);

    useEffect(() => {
        fetchSessions();
    }, []);

    const createSession = async () => {
        const response = await fetch('/api/sessions', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const session = await response.json();
        navigate(`/session/${session.id}`);
    };
}
```

#### Testing Phase 2
```python
# tests/test_auth.py
async def test_user_creation():
    auth = AuthService()
    user = await auth.create_user("test", "password")
    assert user.username == "test"

async def test_session_persistence():
    manager = SessionManager()
    session_id = await manager.create_session("user_id")

    # Save state
    await manager.save_state(session_id, {"test": "data"})

    # Load state
    loaded = await manager.load_session(session_id)
    assert loaded["test"] == "data"
```

**Milestone**: Users can login, create sessions, and persist state ✓

---

### Phase 3: Enhanced Bridges & Display (Days 13-17)
**Goal**: Implement full bridge system and output display

#### Enhanced Bridges
```python
# core/bridges.py
class BridgeRegistry:
    def get_bridges(self, session_id: str):
        def show(data, **metadata):
            # Send to WebSocket with metadata
            self.ws.send_json({
                "type": "output",
                "session_id": session_id,
                "data": serialize(data),
                "metadata": metadata
            })

        def save_to_memory(key, value):
            self.session_manager.save_memory(session_id, key, value)

        def recall_from_memory(key):
            return self.session_manager.get_memory(session_id, key)

        return {
            "show": show,
            "send_status": send_status,
            "save_to_memory": save_to_memory,
            "recall_from_memory": recall_from_memory,
        }
```

#### Frontend Output Display
```jsx
// components/OutputRenderer.jsx
function OutputRenderer({ output }) {
    const { data, metadata } = output;

    // Interpret metadata to decide rendering
    if (metadata?.type === 'plot' || isPlotlyData(data)) {
        return <Plot data={data} />;
    } else if (metadata?.type === 'table' || isDataFrame(data)) {
        return <DataTable data={data} />;
    } else {
        return <HTMLOutput content={data} />;
    }
}

// components/Plot.jsx
import Plotly from 'react-plotly.js';

function Plot({ data, metadata }) {
    return (
        <div className="plot-container">
            <Plotly
                data={data.data || data}
                layout={data.layout || {}}
                config={{ responsive: true }}
            />
        </div>
    );
}
```

#### Testing Phase 3
```python
# tests/test_bridges.py
async def test_show_bridge():
    """Test show() sends correct WebSocket message."""
    bridges = BridgeRegistry().get_bridges("session_123")

    # Mock WebSocket
    with patch('websocket.send_json') as mock_send:
        bridges["show"]({"test": "data"}, type="plot")
        mock_send.assert_called_with({
            "type": "output",
            "data": {"test": "data"},
            "metadata": {"type": "plot"}
        })

# Frontend testing with React Testing Library
```

**Milestone**: Full bridge system working with proper output display ✓

---

### Phase 4: Polish & Production (Days 18-21)
**Goal**: Add remaining features and prepare for production

#### Remaining Features
1. **Auto-save**
```javascript
// hooks/useAutoSave.js
function useAutoSave(sessionId, data) {
    useEffect(() => {
        const interval = setInterval(() => {
            saveSession(sessionId, data);
        }, 30000); // 30 seconds

        return () => clearInterval(interval);
    }, [sessionId, data]);
}
```

2. **Error Handling**
```python
# middleware/error_handler.py
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
```

3. **Centralized Styles**
```scss
// styles/variables.scss
:root {
    --color-primary: #2563eb;
    --spacing-unit: 8px;
    // ... all variables
}

// styles/components.scss
.btn {
    padding: var(--spacing-unit);
    background: var(--color-primary);
    // ... component styles
}
```

#### Production Setup
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://postgres:password@db/llm_orchestrator
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=llm_orchestrator
      - POSTGRES_PASSWORD=password
```

#### End-to-End Testing
```python
# tests/e2e/test_full_flow.py
async def test_complete_user_journey():
    """Test complete flow: signup → login → create session → execute → persist."""

    # 1. Create user
    user = await create_test_user()

    # 2. Login
    token = await login(user.username, "password")

    # 3. Create session
    session = await create_session(token)

    # 4. Send prompt
    ws = await connect_websocket(session.id, token)
    await ws.send_json({"prompt": "Create a plot"})

    # 5. Receive output
    response = await ws.receive_json()
    assert response["type"] == "output"

    # 6. Verify persistence
    loaded = await load_session(session.id)
    assert len(loaded["outputs"]) > 0
```

**Milestone**: Production-ready application ✓

---

### Testing Strategy

#### Unit Tests (Throughout)
```bash
# Backend
pytest tests/unit/ --cov=backend

# Frontend
npm test -- --coverage
```

#### Integration Tests (Phase 2+)
```python
# tests/integration/
- Test database operations
- Test WebSocket communication
- Test LLM integration
- Test session persistence
```

#### E2E Tests (Phase 4)
```javascript
// Using Cypress or Playwright
describe('User Journey', () => {
    it('completes full analysis workflow', () => {
        cy.visit('/login');
        cy.login('user', 'password');
        cy.createSession();
        cy.sendPrompt('Analyze data');
        cy.waitForOutput();
        cy.verifyPlotDisplayed();
    });
});
```

#### Performance Tests
```python
# tests/performance/
- Test with large datasets
- Test with concurrent users
- Test LLM response times
- Test WebSocket throughput
```

### Success Criteria

#### Phase 0-1 Success
- [ ] WebSocket connection works
- [ ] Code execution works
- [ ] LLM generates valid Python code

#### Phase 2 Success
- [ ] Users can sign up and login
- [ ] Sessions persist across logout/login
- [ ] State is correctly saved/loaded

#### Phase 3 Success
- [ ] All bridge functions work
- [ ] Plots display correctly
- [ ] Tables display correctly
- [ ] Memory functions work

#### Phase 4 Success
- [ ] Auto-save works
- [ ] No memory leaks
- [ ] <2s response time for simple queries
- [ ] Handles errors gracefully
- [ ] Passes all E2E tests

### Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] SSL certificates installed
- [ ] Monitoring configured (Sentry, etc.)
- [ ] Backup system configured
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Security headers set
- [ ] Logging configured
- [ ] Health checks working

## Conclusion: A Radical Rethinking

This architecture represents a fundamental shift in how we build intelligent systems:

### The Paradigm Shift

**From**: Systems that use LLMs as smart code generators within rigid frameworks
**To**: Systems where the LLM IS the system, with just minimal bridges for communication

### What We've Achieved

1. **True LLM Autonomy**: Not just generating code snippets, but orchestrating entire workflows
2. **Zero Architectural Constraints**: No patterns to follow, no frameworks to obey
3. **Natural Intelligence**: Decisions based on understanding, not rule matching
4. **Infinite Flexibility**: Can adapt to any requirement without system changes
5. **Minimal Surface Area**: Just a few bridge functions, not hundreds of APIs

### The Core Innovation

Traditional systems: `LLM → Preset Patterns → Rigid System → Output`
Our approach: `LLM → Direct Implementation → Minimal Bridges → Output`

### Why This Matters

- **Future-Proof**: As LLMs improve, the system automatically gets smarter
- **No Maintenance**: No patterns to update, no rules to maintain
- **Natural Evolution**: System behavior evolves with LLM capabilities
- **True Intelligence**: Not simulated through rules, but genuine reasoning

### The Ultimate Test

Ask yourself: If the LLM wanted to implement something completely different from all examples in this document, could it?

**Answer: YES.**

The LLM can ignore every example, every pattern, every suggestion in this document and implement its own approach. That's true freedom.

### Final Thought

**We're not building a system that uses an LLM.**
**We're building bridges for an LLM to create its own system.**

This is the difference between automation and intelligence.