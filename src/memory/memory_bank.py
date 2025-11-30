"""
Memory Bank - Long-Term Learning

This stores patterns learned from previous runs.
Think of it like experience - it remembers what worked before.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json

from src.core.config import Config


class MemoryBank:
    """
    Long-term memory for learned patterns
    
    Simple explanation:
    - Stores successful fix strategies
    - Remembers common issues by dataset type
    - Learns from user feedback
    - Can suggest fixes based on past experience
    """
    
    def __init__(self, memory_dir: str = None):
        """Initialize memory bank"""
        self.memory_dir = Path(memory_dir or "memory")
        self.memory_dir.mkdir(exist_ok=True)
        self.memory_file = self.memory_dir / "memory_bank.json"
        self.memories: Dict[str, Any] = self._load_memories()
    
    def _load_memories(self) -> Dict[str, Any]:
        """Load memories from disk"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'patterns': [],
            'successful_fixes': [],
            'common_issues': {},
            'user_feedback': []
        }
    
    def _save_memories(self):
        """Save memories to disk"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memories, f, indent=2)
    
    def store_pattern(self, pattern_type: str, pattern_data: Dict[str, Any], success_rate: float):
        """
        Store a learned pattern
        
        Example:
            memory.store_pattern("missing_values", {
                "column_type": "numeric",
                "fix_method": "median_imputation"
            }, success_rate=0.95)
        """
        pattern = {
            'type': pattern_type,
            'data': pattern_data,
            'success_rate': success_rate,
            'learned_at': datetime.now().isoformat(),
            'usage_count': 1
        }
        
        # Check if similar pattern exists
        for existing in self.memories['patterns']:
            if existing['type'] == pattern_type and existing['data'] == pattern_data:
                # Update existing pattern
                existing['success_rate'] = (existing['success_rate'] + success_rate) / 2
                existing['usage_count'] += 1
                self._save_memories()
                return
        
        # Add new pattern
        self.memories['patterns'].append(pattern)
        self._save_memories()
    
    def retrieve_similar_patterns(self, current_issue: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieve similar patterns from past runs
        
        Example:
            patterns = memory.retrieve_similar_patterns({
                "type": "missing_values",
                "column_type": "numeric"
            })
        """
        issue_type = current_issue.get('type')
        similar = []
        
        for pattern in self.memories['patterns']:
            if pattern['type'] == issue_type:
                # Check if data matches
                match_score = 0
                for key, value in current_issue.items():
                    if key in pattern['data'] and pattern['data'][key] == value:
                        match_score += 1
                
                if match_score > 0:
                    pattern['match_score'] = match_score
                    similar.append(pattern)
        
        # Sort by match score and success rate
        similar.sort(key=lambda x: (x['match_score'], x['success_rate']), reverse=True)
        return similar[:5]  # Return top 5
    
    def record_successful_fix(self, issue_type: str, fix_method: str, context: Dict[str, Any]):
        """Record a successful fix for future reference"""
        fix_record = {
            'issue_type': issue_type,
            'fix_method': fix_method,
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'success': True
        }
        
        self.memories['successful_fixes'].append(fix_record)
        
        # Keep only last 100
        if len(self.memories['successful_fixes']) > 100:
            self.memories['successful_fixes'] = self.memories['successful_fixes'][-100:]
        
        self._save_memories()
    
    def get_suggested_fix(self, issue_type: str, context: Dict[str, Any]) -> Optional[str]:
        """Get suggested fix method based on past successes"""
        # Look for similar successful fixes
        for fix_record in reversed(self.memories['successful_fixes']):
            if fix_record['issue_type'] == issue_type:
                # Check if context is similar
                context_match = sum(1 for k, v in context.items() 
                                  if k in fix_record['context'] and fix_record['context'][k] == v)
                if context_match >= 2:  # At least 2 context matches
                    return fix_record['fix_method']
        
        return None

