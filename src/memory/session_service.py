"""
Session Service - Tracks Workflow State

This keeps track of what's happening during a dataset processing session.
Think of it like a shopping cart - it remembers what you're doing.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class InMemorySessionService:
    """
    In-memory session service - tracks workflow state
    
    Simple explanation:
    - Each dataset processing gets a session
    - Session stores current state (which step we're on)
    - Session stores history (what we did)
    - Session stores preferences (user choices)
    """
    
    def __init__(self):
        """Initialize session service"""
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, session_id: str = None, dataset_info: Dict = None) -> str:
        """
        Create a new session
        
        Returns:
            session_id: Unique session identifier
        """
        session_id = session_id or str(uuid.uuid4())
        
        self.sessions[session_id] = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'dataset_info': dataset_info or {},
            'state': 'created',
            'history': [],
            'preferences': {},
            'metadata': {}
        }
        
        return session_id
    
    def update_state(self, session_id: str, new_state: str, agent_name: str, result: Any = None):
        """
        Update session state and add to history
        
        Example:
            session.update_state(session_id, "scanning", "ScannerAgent", {"issues": 3})
        """
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        session['state'] = new_state
        session['history'].append({
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'state': new_state,
            'result': str(result) if result else None
        })
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        return self.sessions.get(session_id)
    
    def set_preference(self, session_id: str, key: str, value: Any):
        """Store user preference (e.g., preferred imputation method)"""
        if session_id in self.sessions:
            self.sessions[session_id]['preferences'][key] = value
    
    def get_preference(self, session_id: str, key: str, default: Any = None) -> Any:
        """Get user preference"""
        if session_id in self.sessions:
            return self.sessions[session_id]['preferences'].get(key, default)
        return default
    
    def clear_session(self, session_id: str):
        """Clear a session (cleanup)"""
        if session_id in self.sessions:
            del self.sessions[session_id]

