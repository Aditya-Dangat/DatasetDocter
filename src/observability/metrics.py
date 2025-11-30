"""
Metrics Collector - Tracks Performance Numbers

This tracks metrics like:
- How long each agent takes
- How many issues found
- Success rates
- Quality improvements

Think of it like a dashboard showing key numbers.
"""

import time
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import json

from src.core.config import Config


class MetricsCollector:
    """
    Collects performance and quality metrics
    
    Simple explanation:
    - Records timing for each operation
    - Tracks success/failure rates
    - Stores quality scores
    - Can generate summary statistics
    """
    
    def __init__(self, metrics_dir: str = None):
        """Initialize metrics collector"""
        self.metrics_dir = Path(metrics_dir or Config.LOGS_FOLDER)
        self.metrics_dir.mkdir(exist_ok=True)
        self.current_metrics: Dict[str, Any] = {}
    
    def start_operation(self, operation_name: str):
        """Start timing an operation"""
        self.current_metrics[operation_name] = {
            'start_time': time.time(),
            'operation': operation_name
        }
    
    def end_operation(self, operation_name: str, success: bool = True, **metadata):
        """End timing an operation and record metrics"""
        if operation_name not in self.current_metrics:
            return
        
        start_time = self.current_metrics[operation_name]['start_time']
        duration = time.time() - start_time
        
        metric = {
            'operation': operation_name,
            'duration_seconds': round(duration, 3),
            'success': success,
            'timestamp': datetime.now().isoformat(),
            **metadata
        }
        
        # Save metric
        metrics_file = self.metrics_dir / f"metrics_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(metrics_file, 'a') as f:
            f.write(json.dumps(metric) + '\n')
        
        # Keep in current metrics
        self.current_metrics[operation_name] = metric
    
    def record_metric(self, name: str, value: Any, **metadata):
        """Record a custom metric"""
        metric = {
            'name': name,
            'value': value,
            'timestamp': datetime.now().isoformat(),
            **metadata
        }
        
        metrics_file = self.metrics_dir / f"metrics_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(metrics_file, 'a') as f:
            f.write(json.dumps(metric) + '\n')
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of current metrics"""
        return {
            'operations': len(self.current_metrics),
            'metrics': self.current_metrics
        }

