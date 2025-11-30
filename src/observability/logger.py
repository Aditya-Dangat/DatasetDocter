"""
Structured Logger - Tracks Everything That Happens

This logs all activities in a structured way (JSON format).
Think of it like a flight recorder - it records everything for debugging.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from src.core.config import Config


class StructuredLogger:
    """
    Structured logger that outputs JSON logs
    
    Why JSON? Easy to parse, search, and analyze later.
    """
    
    def __init__(self, log_dir: str = None):
        """Initialize the logger"""
        self.log_dir = Path(log_dir or Config.LOGS_FOLDER)
        self.log_dir.mkdir(exist_ok=True)
        
        # Set up Python logging
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('DatasetDoctor')
    
    def log(self, level: str, message: str, trace_id: str = None, **kwargs):
        """
        Log a message with structured data
        
        Args:
            level: Log level (info, warning, error, debug)
            message: The message
            trace_id: Unique ID to track this operation
            **kwargs: Additional structured data
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level.upper(),
            'message': message,
            'trace_id': trace_id,
            **kwargs
        }
        
        # Write to JSON log file
        log_file = self.log_dir / f"datasetdoctor_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Also use standard Python logging
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message)
    
    def info(self, message: str, trace_id: str = None, **kwargs):
        """Log info message"""
        self.log('info', message, trace_id, **kwargs)
    
    def warning(self, message: str, trace_id: str = None, **kwargs):
        """Log warning message"""
        self.log('warning', message, trace_id, **kwargs)
    
    def error(self, message: str, trace_id: str = None, **kwargs):
        """Log error message"""
        self.log('error', message, trace_id, **kwargs)
    
    def debug(self, message: str, trace_id: str = None, **kwargs):
        """Log debug message"""
        self.log('debug', message, trace_id, **kwargs)

