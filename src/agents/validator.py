"""
Validator Agent - The "Lab Tech" That Verifies Fixes

This agent's job is to check if the fixes actually worked.

Think of it like a lab tech doing a follow-up test:
- Re-scans the dataset to see if issues are gone
- Compares before/after quality scores
- Verifies no new issues were introduced
- Confirms the dataset is now clean
"""

from typing import Dict, Any
import pandas as pd

from src.core.dataset import Dataset
from src.core.diagnostics import DiagnosticReport
from src.agents.scanner import ScannerAgent


class ValidatorAgent:
    """
    The Validator Agent - Verifies that fixes worked
    
    Simple workflow:
        1. Re-scans the dataset after fixes
        2. Compares with original issues
        3. Checks if quality improved
        4. Returns validation results
    """
    
    def __init__(self):
        """Initialize the Validator Agent"""
        self.name = "ValidatorAgent"
        self.scanner = ScannerAgent()  # Re-use scanner to check for remaining issues
    
    def validate(self, dataset: Dataset, report: DiagnosticReport) -> Dict[str, Any]:
        """
        Main method - Validate that fixes worked
        
        Args:
            dataset: The Dataset after fixes
            report: The DiagnosticReport with original issues and fixes
        
        Returns:
            Dictionary with validation results
        """
        print(f"   ✅ Validating fixes...")
        
        # Re-scan to see if issues are gone
        remaining_issues = self.scanner.scan(dataset)
        
        # Count how many original issues were fixed
        original_issue_count = len(report.issues)
        remaining_issue_count = len(remaining_issues)
        fixed_count = original_issue_count - remaining_issue_count
        
        # Calculate success rate
        if original_issue_count > 0:
            success_rate = (fixed_count / original_issue_count) * 100
        else:
            success_rate = 100.0
        
        # Check if quality improved
        original_quality = 100.0  # Start quality
        for issue in report.issues:
            if issue.severity == "critical":
                original_quality -= 10
            elif issue.severity == "high":
                original_quality -= 5
            elif issue.severity == "medium":
                original_quality -= 2
            else:
                original_quality -= 1
        original_quality = max(0, original_quality)
        
        current_quality = report.quality_score
        quality_improvement = current_quality - original_quality
        
        # Check if any new issues were introduced
        new_issues = []
        original_issue_types = {issue.type: issue.column for issue in report.issues}
        for issue in remaining_issues:
            key = (issue.type, issue.column)
            original_key = (issue.type, issue.column)
            if original_key not in original_issue_types:
                new_issues.append(issue)
        
        # Build validation result
        validation_result = {
            'success': remaining_issue_count == 0 and len(new_issues) == 0,
            'original_issues': original_issue_count,
            'remaining_issues': remaining_issue_count,
            'fixed_issues': fixed_count,
            'success_rate': round(success_rate, 1),
            'original_quality': round(original_quality, 1),
            'current_quality': round(current_quality, 1),
            'quality_improvement': round(quality_improvement, 1),
            'new_issues_introduced': len(new_issues),
            'remaining_issue_details': [
                {
                    'type': issue.type,
                    'column': issue.column,
                    'description': issue.description
                }
                for issue in remaining_issues[:5]  # First 5
            ]
        }
        
        # Print summary
        if validation_result['success']:
            print(f"   ✅ All issues fixed! Quality improved from {original_quality:.1f} to {current_quality:.1f}")
        else:
            print(f"   ⚠️  {remaining_issue_count} issue(s) remaining (fixed {fixed_count}/{original_issue_count})")
            print(f"   📈 Quality improved from {original_quality:.1f} to {current_quality:.1f} (+{quality_improvement:.1f})")
        
        if new_issues:
            print(f"   ⚠️  Warning: {len(new_issues)} new issue(s) introduced during fixing")
        
        return validation_result
    
    def get_info(self) -> dict:
        """Get information about this agent"""
        return {
            'name': self.name,
            'role': 'Fix Validation',
            'description': 'Verifies that fixes were successful and quality improved'
        }

