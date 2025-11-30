"""
Tracer - Tracks Request Flow Across All Agents

This tracks how a request flows through all agents.
Think of it like GPS tracking - you can see the exact path taken.
"""

import uuid
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import json

from src.core.config import Config


class Tracer:
    """
    Distributed tracer - tracks operations across agents
    
    Simple explanation:
    - Each operation gets a unique trace ID
    - We record when each agent starts/finishes
    - We can see the complete flow later
    """
    
    def __init__(self, trace_dir: str = None):
        """Initialize the tracer"""
        self.trace_dir = Path(trace_dir or Config.TRACES_FOLDER)
        self.trace_dir.mkdir(exist_ok=True)
        self.active_traces: Dict[str, Dict] = {}
    
    def start_trace(self, operation_name: str, trace_id: str = None) -> str:
        """
        Start a new trace
        
        Returns:
            trace_id: Unique ID for this trace
        """
        trace_id = trace_id or str(uuid.uuid4())
        
        self.active_traces[trace_id] = {
            'trace_id': trace_id,
            'operation': operation_name,
            'start_time': time.time(),
            'spans': []
        }
        
        return trace_id
    
    def add_span(self, trace_id: str, span_name: str, agent_name: str, 
                 duration: float = None, metadata: Dict = None):
        """
        Add a span (one step in the trace)
        
        Example:
            trace_id = tracer.start_trace("process_dataset")
            tracer.add_span(trace_id, "ingest", "IngestorAgent", 0.5)
            tracer.add_span(trace_id, "scan", "ScannerAgent", 1.2)
        """
        if trace_id not in self.active_traces:
            return
        
        span = {
            'span_name': span_name,
            'agent': agent_name,
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'metadata': metadata or {}
        }
        
        self.active_traces[trace_id]['spans'].append(span)
    
    def end_trace(self, trace_id: str) -> Dict[str, Any]:
        """
        End a trace and save it
        
        Returns:
            Complete trace information
        """
        if trace_id not in self.active_traces:
            return {}
        
        trace = self.active_traces[trace_id]
        trace['end_time'] = time.time()
        trace['total_duration'] = trace['end_time'] - trace['start_time']
        
        # Save to file
        trace_file = self.trace_dir / f"trace_{trace_id}.json"
        with open(trace_file, 'w') as f:
            json.dump(trace, f, indent=2)
        
        # Remove from active traces
        del self.active_traces[trace_id]
        
        return trace
    
    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get a saved trace"""
        trace_file = self.trace_dir / f"trace_{trace_id}.json"
        if trace_file.exists():
            with open(trace_file, 'r') as f:
                return json.load(f)
        return None

