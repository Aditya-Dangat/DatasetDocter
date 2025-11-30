"""
Ingestor Agent - The "Receptionist"

This agent's job is simple:
1. Take a file (CSV or JSON)
2. Load it into memory
3. Check if it's valid
4. Return a Dataset object

Think of it like a receptionist at a hospital - they check you in and make sure
your paperwork is complete before sending you to the doctor.
"""

from typing import Optional, Tuple
from pathlib import Path
import pandas as pd

from src.core.dataset import Dataset
from src.core.diagnostics import DiagnosticReport, Issue


class IngestorAgent:
    """
    The Ingestor Agent - Loads and validates datasets
    
    Simple workflow:
        1. Receive file path
        2. Try to load it
        3. Check if it's valid (not empty, has columns, etc.)
        4. Return Dataset or report errors
    """
    
    def __init__(self):
        """Initialize the Ingestor Agent"""
        self.name = "IngestorAgent"
        self.supported_formats = ['.csv', '.json']
    
    def ingest(self, filepath: str) -> Tuple[Optional[Dataset], Optional[DiagnosticReport]]:
        """
        Main method - loads a dataset from a file
        
        Args:
            filepath: Path to the file (e.g., "data.csv")
        
        Returns:
            Tuple of (Dataset, DiagnosticReport)
            - If successful: (Dataset object, None)
            - If failed: (None, DiagnosticReport with errors)
        """
        report = DiagnosticReport(f"Ingestion of {filepath}")
        
        # Step 1: Check if file exists
        if not Path(filepath).exists():
            issue = Issue(
                type="file_not_found",
                severity="critical",
                description=f"File not found: {filepath}"
            )
            report.add_issue(issue)
            return None, report
        
        # Step 2: Check file format
        file_ext = Path(filepath).suffix.lower()
        if file_ext not in self.supported_formats:
            issue = Issue(
                type="unsupported_format",
                severity="critical",
                description=f"Unsupported file format: {file_ext}. Supported: {self.supported_formats}"
            )
            report.add_issue(issue)
            return None, report
        
        # Step 3: Try to load the file
        try:
            if file_ext == '.csv':
                # Try with default settings first
                try:
                    data = pd.read_csv(filepath)
                except Exception as e1:
                    # If that fails, try with more lenient settings
                    try:
                        # Try with error handling - skip bad lines
                        data = pd.read_csv(filepath, on_bad_lines='skip', engine='python')
                        if data.empty:
                            raise ValueError("File appears to be empty or all lines were skipped")
                    except Exception as e2:
                        # Try with different separators and quoting
                        try:
                            data = pd.read_csv(filepath, sep=',', quotechar='"', on_bad_lines='skip', engine='python')
                        except Exception as e3:
                            # Last resort: try with different encoding
                            try:
                                data = pd.read_csv(filepath, encoding='latin-1', on_bad_lines='skip', engine='python')
                            except Exception as e4:
                                # If all attempts fail, raise the original error
                                raise e1
            elif file_ext == '.json':
                data = pd.read_json(filepath)
            else:
                raise ValueError(f"Unsupported format: {file_ext}")
        
        except Exception as e:
            # If loading failed, report the error with helpful message
            error_msg = str(e)
            if "tokenizing" in error_msg.lower() or "expected" in error_msg.lower():
                error_msg = f"CSV parsing error: The file may have inconsistent columns or unquoted commas. Original error: {error_msg}"
            
            issue = Issue(
                type="load_error",
                severity="critical",
                description=error_msg
            )
            report.add_issue(issue)
            return None, report
        
        # Step 4: Validate the loaded data
        validation_issues = self._validate_data(data, filepath)
        for issue in validation_issues:
            report.add_issue(issue)
        
        # Step 5: Create Dataset object
        dataset = Dataset(data, name=Path(filepath).name)
        
        # If we have critical issues, don't proceed
        critical_issues = [i for i in validation_issues if i.severity == "critical"]
        if critical_issues:
            return None, report
        
        # Success! Return the dataset
        return dataset, None
    
    def _validate_data(self, data: pd.DataFrame, filepath: str) -> list:
        """
        Check if the loaded data is valid
        
        Validations:
        - Is it empty?
        - Does it have columns?
        - Does it have at least some rows?
        """
        issues = []
        
        # Check if empty
        if data.empty:
            issues.append(Issue(
                type="empty_dataset",
                severity="critical",
                description="Dataset is empty - no data to process"
            ))
            return issues  # No point checking further if empty
        
        # Check if has columns
        if len(data.columns) == 0:
            issues.append(Issue(
                type="no_columns",
                severity="critical",
                description="Dataset has no columns"
            ))
        
        # Check if has rows (we already checked empty, but double-check)
        if len(data) == 0:
            issues.append(Issue(
                type="no_rows",
                severity="critical",
                description="Dataset has no rows"
            ))
        
        return issues
    
    def get_info(self) -> dict:
        """Get information about this agent"""
        return {
            'name': self.name,
            'role': 'Dataset Ingestion',
            'description': 'Loads and validates datasets from files',
            'supported_formats': self.supported_formats
        }

