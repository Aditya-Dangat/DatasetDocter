"""
Metrics Calculator - Computes precision, recall, F1, and other evaluation metrics
"""

from typing import Dict, List, Any
from src.core.diagnostics import Issue, Fix


class MetricsCalculator:
    """
    Calculates evaluation metrics for agent performance
    
    Metrics:
    - Precision: How many detected issues were correct?
    - Recall: How many actual issues were found?
    - F1 Score: Harmonic mean of precision and recall
    - Accuracy: Overall correctness
    """
    
    def __init__(self):
        self.name = "MetricsCalculator"
    
    def calculate_issue_metrics(self, detected_issues: List[Issue], expected_issues: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate precision, recall, F1 for issue detection
        
        Args:
            detected_issues: Issues found by ScannerAgent
            expected_issues: Ground truth issues from gold dataset
        
        Returns:
            Dictionary with precision, recall, f1, accuracy
        """
        # Convert expected issues to comparable format
        expected_set = set()
        for exp_issue in expected_issues:
            key = (exp_issue.get('type'), exp_issue.get('column'))
            expected_set.add(key)
        
        # Convert detected issues to comparable format
        detected_set = set()
        for det_issue in detected_issues:
            key = (det_issue.type, det_issue.column)
            detected_set.add(key)
        
        # Calculate metrics
        true_positives = len(detected_set & expected_set)  # Correctly detected
        false_positives = len(detected_set - expected_set)  # Incorrectly detected
        false_negatives = len(expected_set - detected_set)  # Missed issues
        
        # Precision: Of all detected, how many were correct?
        if len(detected_set) > 0:
            precision = true_positives / len(detected_set)
        else:
            precision = 0.0 if len(expected_set) > 0 else 1.0
        
        # Recall: Of all expected, how many were found?
        if len(expected_set) > 0:
            recall = true_positives / len(expected_set)
        else:
            recall = 1.0 if len(detected_set) == 0 else 0.0
        
        # F1 Score: Harmonic mean of precision and recall
        if precision + recall > 0:
            f1_score = 2 * (precision * recall) / (precision + recall)
        else:
            f1_score = 0.0
        
        # Accuracy: Overall correctness
        total = len(expected_set) + false_positives
        if total > 0:
            accuracy = true_positives / total
        else:
            accuracy = 1.0
        
        return {
            'precision': round(precision * 100, 2),
            'recall': round(recall * 100, 2),
            'f1_score': round(f1_score * 100, 2),
            'accuracy': round(accuracy * 100, 2),
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'total_expected': len(expected_set),
            'total_detected': len(detected_set)
        }
    
    def calculate_fix_metrics(self, applied_fixes: List[Fix], expected_fixes: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate metrics for fix application
        
        Args:
            applied_fixes: Fixes applied by FixerAgent
            expected_fixes: Expected fixes from gold dataset
        
        Returns:
            Dictionary with fix success metrics
        """
        # Convert to comparable format
        expected_set = set()
        for exp_fix in expected_fixes:
            key = (exp_fix.get('issue_type'), exp_fix.get('column'))
            expected_set.add(key)
        
        applied_set = set()
        successful_fixes = 0
        for fix in applied_fixes:
            key = (fix.issue_type, fix.column)
            applied_set.add(key)
            if fix.success:
                successful_fixes += 1
        
        # Calculate metrics
        true_positives = len(applied_set & expected_set)
        false_positives = len(applied_set - expected_set)
        false_negatives = len(expected_set - applied_set)
        
        # Precision
        if len(applied_set) > 0:
            precision = true_positives / len(applied_set)
        else:
            precision = 0.0 if len(expected_set) > 0 else 1.0
        
        # Recall
        if len(expected_set) > 0:
            recall = true_positives / len(expected_set)
        else:
            recall = 1.0 if len(applied_set) == 0 else 0.0
        
        # F1 Score
        if precision + recall > 0:
            f1_score = 2 * (precision * recall) / (precision + recall)
        else:
            f1_score = 0.0
        
        # Success rate (of applied fixes, how many succeeded?)
        success_rate = (successful_fixes / len(applied_fixes) * 100) if len(applied_fixes) > 0 else 0.0
        
        return {
            'precision': round(precision * 100, 2),
            'recall': round(recall * 100, 2),
            'f1_score': round(f1_score * 100, 2),
            'success_rate': round(success_rate, 2),
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'successful_fixes': successful_fixes,
            'total_expected': len(expected_set),
            'total_applied': len(applied_set)
        }
    
    def calculate_quality_metrics(self, final_quality_score: float, min_quality_score: float) -> Dict[str, Any]:
        """
        Calculate quality score metrics
        
        Returns:
            Dictionary with quality metrics
        """
        quality_improvement = final_quality_score - min_quality_score
        meets_threshold = final_quality_score >= min_quality_score
        
        return {
            'final_score': round(final_quality_score, 2),
            'min_threshold': min_quality_score,
            'improvement': round(quality_improvement, 2),
            'meets_threshold': meets_threshold
        }

