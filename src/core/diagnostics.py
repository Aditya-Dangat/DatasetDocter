"""
Diagnostics - The "Medical Report" for Your Dataset

This stores all the problems we found and fixes we applied.
Think of it like a patient's medical chart.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd


@dataclass
class Issue:
    """
    Represents a single problem found in the dataset
    
    Example:
        Issue(
            type="missing_values",
            column="age",
            severity="high",
            description="Found 150 missing values in 'age' column"
        )
    """
    type: str  # What kind of problem (missing_values, type_error, etc.)
    column: Optional[str] = None  # Which column has the problem
    severity: str = "medium"  # low, medium, high, critical
    description: str = ""  # Human-readable description
    count: int = 0  # How many instances of this problem
    details: Dict[str, Any] = field(default_factory=dict)  # Extra info


@dataclass
class Fix:
    """
    Represents a fix we applied
    
    Example:
        Fix(
            issue_type="missing_values",
            column="age",
            method="median_imputation",
            description="Filled missing values with median (32.5)"
        )
    """
    issue_type: str  # What problem this fixes
    column: Optional[str] = None
    method: str = ""  # How we fixed it (median_imputation, etc.)
    description: str = ""
    before_count: int = 0  # Problems before fix
    after_count: int = 0  # Problems after fix
    success: bool = True  # Did the fix work?


class DiagnosticReport:
    """
    The complete "medical report" for a dataset
    
    Contains:
    - All issues found
    - All fixes applied
    - Quality scores
    - Summary statistics
    """
    
    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name
        self.timestamp = datetime.now()
        self.issues: List[Issue] = []
        self.fixes: List[Fix] = []
        self.quality_score: float = 100.0  # Start at 100, decrease for each problem
        self.summary: Dict[str, Any] = {}
    
    def add_issue(self, issue: Issue):
        """Add a problem we found"""
        self.issues.append(issue)
        # Lower quality score based on severity
        if issue.severity == "critical":
            self.quality_score -= 10
        elif issue.severity == "high":
            self.quality_score -= 5
        elif issue.severity == "medium":
            self.quality_score -= 2
        else:
            self.quality_score -= 1
        
        # Don't go below 0
        self.quality_score = max(0, self.quality_score)
    
    def add_fix(self, fix: Fix):
        """Record a fix we applied"""
        self.fixes.append(fix)
        if fix.success:
            # Improve quality score if fix worked
            self.quality_score = min(100, self.quality_score + 2)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the diagnostic report"""
        return {
            'dataset_name': self.dataset_name,
            'timestamp': self.timestamp.isoformat(),
            'total_issues': len(self.issues),
            'total_fixes': len(self.fixes),
            'quality_score': round(self.quality_score, 2),
            'issues_by_type': self._count_issues_by_type(),
            'issues_by_severity': self._count_issues_by_severity()
        }
    
    def _count_issues_by_type(self) -> Dict[str, int]:
        """Count how many issues of each type"""
        counts = {}
        for issue in self.issues:
            counts[issue.type] = counts.get(issue.type, 0) + 1
        return counts
    
    def _count_issues_by_severity(self) -> Dict[str, int]:
        """Count how many issues of each severity level"""
        counts = {}
        for issue in self.issues:
            counts[issue.severity] = counts.get(issue.severity, 0) + 1
        return counts
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the report to a dictionary (for JSON export)"""
        def convert_value(v):
            """Convert numpy/pandas types to native Python types"""
            import numpy as np
            if isinstance(v, (np.integer, np.int64, np.int32)):
                return int(v)
            elif isinstance(v, (np.floating, np.float64, np.float32)):
                return float(v)
            elif isinstance(v, (np.bool_, bool)):
                return bool(v)
            elif isinstance(v, np.ndarray):
                return v.tolist()
            elif pd.isna(v):
                return None
            return v
        
        def clean_dict(d):
            """Recursively clean dictionary values"""
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [clean_dict(item) for item in d]
            else:
                return convert_value(d)
        
        result = {
            'dataset_name': self.dataset_name,
            'timestamp': self.timestamp.isoformat(),
            'quality_score': float(self.quality_score),
            'summary': clean_dict(self.get_summary()),
            'issues': [
                {
                    'type': i.type,
                    'column': i.column,
                    'severity': i.severity,
                    'description': i.description,
                    'count': int(i.count),
                    'details': clean_dict(i.details)
                }
                for i in self.issues
            ],
            'fixes': [
                {
                    'issue_type': f.issue_type,
                    'column': f.column,
                    'method': f.method,
                    'description': f.description,
                    'before_count': int(f.before_count),
                    'after_count': int(f.after_count),
                    'success': f.success
                }
                for f in self.fixes
            ]
        }
        
        return clean_dict(result)

