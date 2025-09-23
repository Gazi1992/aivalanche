from __future__ import annotations

# Standard Library
import copy
import json
import logging
import os
from pathlib import Path
from typing import List, Optional

# Third-party
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import plotly.graph_objs as go

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

import logging

_root_logger = logging.getLogger()
# On each fresh start, overwrite the log file (mode="w") so we get a clean snapshot.
if not any(isinstance(h, logging.FileHandler) for h in _root_logger.handlers):
    file_handler = logging.FileHandler("logs/backend_debug.log", mode="w", encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    _root_logger.addHandler(file_handler)
    _root_logger.setLevel(logging.DEBUG)

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))


# Local modules
from backend.core.data_handler import load_dataset, available_datasets
from backend.core.ai.ai_service import AIService
from backend.core.data.data_analyzer import DataAnalyzer
from backend.core.sessions_db import sessions_db


# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

# Directory is taken from data_handler when imported
from backend.core.data_handler import DATA_DIR

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize AI service
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logging.warning("GEMINI_API_KEY not found in environment variables. AI features will be limited.")
ai_service = AIService(GEMINI_API_KEY)


# ----------------------------------------------------------------------------
# Pydantic models (request/response schemas)
# ----------------------------------------------------------------------------



# ----------------------------------------------------------------------------
# FastAPI application & middleware
# ----------------------------------------------------------------------------

app = FastAPI(title="Aivalanche Backend API", version="0.1.0")

# Allow local Vite dev server and Electron file:// origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],  # loosen when needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/config", summary="Get the full UI configuration")
def get_config():
    """
    Loads and returns the dashboard configuration from a default file.
    This is the primary endpoint for the frontend to fetch its layout and data sources.
    """
    # For simplicity, we'll hardcode the default config file.
    # This could be made dynamic (e.g., from a query parameter) if needed.
    config_name = "default_config.json"
    config_path = (DATA_DIR / "configs" / config_name).resolve()

    if not config_path.exists():
        raise HTTPException(404, detail=f"Default config file '{config_name}' not found.")

    try:
        # The dashboard builder now handles loading, validation, and structuring.
        dashboard_json = build_dashboard(config_path)

        # Also persist payload for front-end debugging (same as /dashboard route)
        try:
            sanitized = copy.deepcopy(dashboard_json)

            for fig_entry in sanitized.get("figures", []):
                if isinstance(fig_entry, dict):
                    layout = fig_entry.get("figure", {}).get("layout", {})
                    if isinstance(layout, dict):
                        layout.pop("template", None)

            payload_path = Path("logs/frontend_payload.json")

            json_text = json.dumps(sanitized, ensure_ascii=False, indent=2)

            def _inline_xy_lists(text: str) -> str:
                lines = text.splitlines()
                out_lines: list[str] = []
                i = 0
                while i < len(lines):
                    line = lines[i]
                    stripped = line.lstrip()
                    if stripped.startswith("\"x\": [") or stripped.startswith("\"y\": ["):
                        indent = line[: len(line) - len(stripped)]
                        collected = stripped
                        i += 1
                        while i < len(lines):
                            next_line = lines[i]
                            collected += next_line.strip()
                            if next_line.strip().endswith("],") or next_line.strip().endswith("]"):
                                break
                            i += 1
                        out_lines.append(indent + collected)
                        i += 1
                    else:
                        out_lines.append(line)
                        i += 1
                return "\n".join(out_lines)

            json_text = _inline_xy_lists(json_text)
            payload_path.write_text(json_text, encoding="utf-8")
        except Exception as exc:
            logging.getLogger(__name__).error("Failed to write frontend payload from /config: %s", exc)

        return JSONResponse(content=dashboard_json, media_type="application/json; charset=utf-8")
    except Exception as e:
        logging.getLogger(__name__).error(f"Error building dashboard from {config_name}: {e}", exc_info=True)
        raise HTTPException(500, detail="Failed to process configuration.")


@app.get("/health", summary="Health check")
def health() -> dict[str, str]:
    """Return simple *ok* status so front-end can verify connection."""
    return {"status": "ok"}


@app.get("/datasets", response_model=List[str], summary="List available datasets")
def list_datasets() -> List[str]:
    """Return dataset filenames available in *data* directory."""
    return available_datasets()


@app.get("/datasets/{name}", summary="Preview a dataset")
def preview_dataset(name: str) -> dict:
    """Return the first 10 rows of *name* as JSON for quick preview."""
    file_path = DATA_DIR / name
    if not file_path.exists():
        raise HTTPException(404, detail="Dataset not found")

    try:
        df = load_dataset(name)
        return {"columns": df.columns.tolist(), "preview": df.head(10).to_dict(orient="records")}
    except FileNotFoundError:
        raise HTTPException(404, detail="Dataset not found")
    except Exception as exc:
        raise HTTPException(500, detail=str(exc)) from exc




# ---------------------------------------------------------------------------
# Gemini AI Endpoints
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    current_config: Optional[dict] = None


class DataUploadRequest(BaseModel):
    filename: str
    content: str
    file_type: str
    message: Optional[str] = None

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Handle chat messages with enhanced AI service"""
    try:
        context = {
            "current_config": request.current_config
        }
        response = ai_service.process_message(request.message, context)
        
        # Handle Python execution responses
        if response.get("type") == "python_execution":
            # Convert the execution result to frontend-compatible format
            execution_result = response.get("execution_result", {})
            plots = execution_result.get("plots", [])
            
            # Convert plots to dashboard format compatible with frontend
            dashboard_figures = []
            for plot in plots:
                dashboard_figures.append({
                    "id": plot["id"],
                    "figure": plot["figure"],
                    "metadata": plot.get("metadata", {}),
                    "visibility": True
                })
            
            # Return in a format the frontend expects
            return {
                "type": "python_execution",
                "message": response.get("message", "Visualization created successfully"),
                "dashboard": {
                    "figures": dashboard_figures,
                    "app_title": "Python Generated Dashboard",
                    "theme": "light"
                },
                "session_id": response.get("session_id"),
                "execution_output": execution_result.get("output", ""),
                "success": True
            }
        
        # If response includes processed data, store it temporarily
        if "data_summary" in response:
            # Data summary is included in the response for client use
            pass
            
        return response
    except Exception as e:
        logging.error(f"Error in chat endpoint: {e}")
        return {
            "type": "error",
            "message": f"Sorry, I encountered an error: {str(e)}"
        }


@app.post("/api/upload-data")
async def upload_data(request: DataUploadRequest):
    """Handle data file upload and analysis"""
    import pandas as pd
    from io import StringIO
    import tempfile
    import os
    import traceback
    
    try:
        logging.info(f"Processing file upload: {request.filename} (type: {request.file_type})")
        
        # Parse the file content based on file type
        if request.file_type == 'csv':
            df = pd.read_csv(StringIO(request.content))
        elif request.file_type in ['xlsx', 'xls']:
            # For Excel files, we need to save temporarily
            # Excel files need binary content, so we'll handle base64 if needed
            import base64
            with tempfile.NamedTemporaryFile(suffix=f'.{request.file_type}', delete=False) as tmp:
                # Check if content is base64 encoded
                try:
                    content_bytes = base64.b64decode(request.content)
                except:
                    content_bytes = request.content.encode('latin-1')
                tmp.write(content_bytes)
                tmp_path = tmp.name
            df = pd.read_excel(tmp_path)
            os.unlink(tmp_path)
        elif request.file_type == 'json':
            df = pd.read_json(StringIO(request.content))
        elif request.file_type == 'parquet':
            # Handle parquet files
            import base64
            with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp:
                content_bytes = base64.b64decode(request.content)
                tmp.write(content_bytes)
                tmp_path = tmp.name
            df = pd.read_parquet(tmp_path)
            os.unlink(tmp_path)
        else:
            raise ValueError(f"Unsupported file type: {request.file_type}")
        
        logging.info(f"Successfully parsed file with shape: {df.shape}")
        
        # Create .temp directory if it doesn't exist
        temp_dir = Path(".temp")
        temp_dir.mkdir(exist_ok=True)
        
        # Save the dataframe temporarily for analysis
        temp_file_path = temp_dir / f"{request.filename}"
        df.to_csv(temp_file_path, index=False)
        
        # Analyze the data
        logging.info("Starting data analysis...")
        analyzer = DataAnalyzer()
        analysis = analyzer.analyze_dataframe(df, str(temp_file_path))
        logging.info(f"Analysis complete. Found {len(analysis.get('suggested_plots', []))} plot suggestions")
        
        # Convert numpy types to Python native types for JSON serialization
        import numpy as np
        import pandas as pd
        from enum import Enum
        
        def convert_numpy_types(obj):
            # Check for numpy arrays first (before pd.isna which fails on arrays)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, (np.integer, np.int_)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float_)):
                return float(obj)
            elif isinstance(obj, Enum):
                return obj.value  # Convert Enum to its value
            elif isinstance(obj, (pd.NA.__class__, type(None))):
                return None
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif isinstance(obj, tuple):
                return tuple(convert_numpy_types(item) for item in obj)
            # Try to check for NaN on scalar values only
            try:
                if pd.isna(obj):
                    return None
            except (ValueError, TypeError):
                pass
            return obj
        
        analysis = convert_numpy_types(analysis)
        
        # Store the data in cache for later visualization requests
        if hasattr(ai_service, 'data_cache'):
            ai_service.data_cache[request.filename] = {
                "df": df,
                "analysis": analysis,
                "file_path": str(temp_file_path)
            }
            logging.info(f"Cached data for {request.filename}")
        
        # Build response message with insights
        insights = []
        if analysis.get('suggested_plots'):
            plot_types = [p.get('plot_type', 'visualization') for p in analysis['suggested_plots'][:3]]
            insights.append(f"Suggested visualizations: {', '.join(plot_types)}")
        
        if analysis.get('quality_issues'):
            insights.append(f"Found {len(analysis['quality_issues'])} data quality issues")
        
        summary_msg = f"Successfully loaded {request.filename} with {len(df)} rows and {len(df.columns)} columns."
        if insights:
            summary_msg += " " + ". ".join(insights) + "."
        
        return {
            "type": "data_analysis",
            "message": summary_msg,
            "analysis": analysis,
            "config": None  # No auto-generation - user must request visualization explicitly
        }
        
    except Exception as e:
        logging.error(f"Error in upload_data: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Python Execution Endpoints
# ---------------------------------------------------------------------------

from backend.core.execution_service import execution_service
from typing import Dict, Any

class PythonExecuteRequest(BaseModel):
    code: str
    session_id: Optional[str] = None

@app.post("/api/python/execute")
async def execute_python(request: PythonExecuteRequest) -> Dict[str, Any]:
    """Execute Python code and return results including any generated plots."""
    try:
        # Use provided session_id or create a new one
        session_id = request.session_id
        if not session_id:
            session_id = execution_service.create_session()
            
        # Execute the code
        result = execution_service.execute_in_session(session_id, request.code)
        
        # Add session_id to response
        result['session_id'] = session_id
        
        return result
        
    except Exception as e:
        logging.error(f"Error executing Python code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Sessions Management Endpoints
# ---------------------------------------------------------------------------

class SessionCreate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class SessionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

@app.get("/api/sessions")
async def list_sessions():
    """List all sessions from the file-based database."""
    sessions = sessions_db.list_sessions()
    return {"sessions": sessions}

@app.post("/api/sessions")
async def create_session(request: SessionCreate):
    """Create a new session."""
    session = sessions_db.create_session(
        name=request.name,
        description=request.description
    )
    return session

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a specific session."""
    session = sessions_db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.put("/api/sessions/{session_id}")
async def update_session(session_id: str, request: SessionUpdate):
    """Update session metadata."""
    updates = {}
    if request.name is not None:
        updates["name"] = request.name
    if request.description is not None:
        updates["description"] = request.description

    session = sessions_db.update_session(session_id, updates)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    success = sessions_db.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}

class DemoRequest(BaseModel):
    session_id: str = "default"
    script_name: str = "comprehensive_demo"

@app.post("/api/python/demo")
async def execute_demo_script(request: DemoRequest) -> Dict[str, Any]:
    """Execute a demo script with status updates."""
    import re
    from pathlib import Path
    
    try:
        # Load the demo script
        demo_path = Path(__file__).parent.parent / 'demo_scripts' / f'{request.script_name}.py'
        with open(demo_path, 'r') as f:
            code = f.read()
        
        # Execute the code
        result = execution_service.execute_in_session(request.session_id, code)
        
        # Parse status messages from output
        status_messages = []
        if result.get('output'):
            lines = result['output'].split('\n')
            for line in lines:
                # Parse status messages in format [STATUS:type] message
                match = re.match(r'\[STATUS:(\w+)\]\s*(.*)', line)
                if match:
                    status_type, message = match.groups()
                    status_messages.append({
                        'type': status_type,
                        'message': message
                    })
        
        # Return enhanced result with status messages
        return {
            **result,
            'status_messages': status_messages
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Demo script not found")
    except Exception as e:
        logging.error(f"Error executing demo script: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------------------------
# Plot Guidelines API
# ---------------------------------------------------------------------------

@app.get("/api/plot-guidelines/{plot_type}")
async def get_plot_guide(plot_type: str, include_general: bool = True):
    """Get comprehensive guidelines for creating a specific plot type."""
    try:
        import sys
        from pathlib import Path
        # Add parent directory to path to find core module
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from core.plot_guidelines import get_plot_guidelines
        guidelines = get_plot_guidelines(plot_type, include_general)
        return guidelines
    except Exception as e:
        logging.error(f"Error getting plot guidelines: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/plot-guidelines")
async def list_plot_types():
    """Get list of all available plot types with descriptions."""
    try:
        import sys
        from pathlib import Path
        # Add parent directory to path to find core module
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from core.plot_guidelines import get_all_plot_types
        plot_types = get_all_plot_types()
        return {"plot_types": plot_types}
    except Exception as e:
        logging.error(f"Error listing plot types: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

class PlotRecommendationRequest(BaseModel):
    num_variables: int
    variable_types: List[str]
    relationship_type: Optional[str] = None
    data_size: Optional[int] = 100

@app.post("/api/plot-recommendations")
async def get_recommendations(request: PlotRecommendationRequest):
    """Get plot type recommendations based on data characteristics."""
    try:
        import sys
        from pathlib import Path
        # Add parent directory to path to find core module
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from core.plot_guidelines import get_plot_recommendation

        data_characteristics = {
            'num_variables': request.num_variables,
            'variable_types': request.variable_types,
            'relationship_type': request.relationship_type,
            'data_size': request.data_size
        }

        recommendations = get_plot_recommendation(data_characteristics)
        return recommendations
    except Exception as e:
        logging.error(f"Error getting plot recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


 