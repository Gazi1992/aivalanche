"""
Simple file-based sessions database.
Sessions are stored in:
- backend/sessions.json (metadata)
- backend/sessions/{session_id}/ (session files)
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import uuid
import logging

logger = logging.getLogger(__name__)

class SessionsDB:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent / "sessions"
        self.db_file = Path(__file__).parent.parent / "sessions.json"

        # Create base directory if it doesn't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Initialize sessions.json if it doesn't exist
        if not self.db_file.exists():
            self._save_db({"sessions": []})

    def _load_db(self) -> Dict:
        """Load sessions database from JSON file."""
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading sessions DB: {e}")
            return {"sessions": []}

    def _save_db(self, data: Dict):
        """Save sessions database to JSON file."""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving sessions DB: {e}")

    def list_sessions(self) -> List[Dict]:
        """Get all sessions."""
        db = self._load_db()
        return db.get("sessions", [])

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get a specific session by ID."""
        sessions = self.list_sessions()
        for session in sessions:
            if session["id"] == session_id:
                return session
        return None

    def create_session(self, name: str = None, description: str = None) -> Dict:
        """Create a new session."""
        session_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()

        session = {
            "id": session_id,
            "name": name or f"Session {session_id}",
            "description": description or "",
            "created_at": timestamp,
            "last_modified": timestamp,
            "status": "active"
        }

        # Create session directory
        session_dir = self.base_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # Add to database
        db = self._load_db()
        db["sessions"].append(session)
        self._save_db(db)

        logger.info(f"Created session: {session_id}")
        return session

    def update_session(self, session_id: str, updates: Dict) -> Optional[Dict]:
        """Update session metadata."""
        db = self._load_db()
        sessions = db.get("sessions", [])

        for i, session in enumerate(sessions):
            if session["id"] == session_id:
                # Update fields
                session.update(updates)
                session["last_modified"] = datetime.now().isoformat()

                # Save
                db["sessions"][i] = session
                self._save_db(db)

                logger.info(f"Updated session: {session_id}")
                return session

        return None

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its directory."""
        db = self._load_db()
        sessions = db.get("sessions", [])

        # Find and remove session
        for i, session in enumerate(sessions):
            if session["id"] == session_id:
                # Remove from database
                sessions.pop(i)
                db["sessions"] = sessions
                self._save_db(db)

                # Remove session directory
                session_dir = self.base_dir / session_id
                if session_dir.exists():
                    shutil.rmtree(session_dir)

                logger.info(f"Deleted session: {session_id}")
                return True

        return False

    def get_session_directory(self, session_id: str) -> Optional[Path]:
        """Get the directory path for a session."""
        session = self.get_session(session_id)
        if session:
            return self.base_dir / session_id
        return None

    def save_session_file(self, session_id: str, filename: str, content: str):
        """Save a file to a session directory."""
        session_dir = self.get_session_directory(session_id)
        if session_dir:
            file_path = session_dir / filename
            file_path.write_text(content)

            # Update last_modified
            self.update_session(session_id, {})
            logger.info(f"Saved file {filename} to session {session_id}")

    def load_session_file(self, session_id: str, filename: str) -> Optional[str]:
        """Load a file from a session directory."""
        session_dir = self.get_session_directory(session_id)
        if session_dir:
            file_path = session_dir / filename
            if file_path.exists():
                return file_path.read_text()
        return None

# Global instance
sessions_db = SessionsDB()