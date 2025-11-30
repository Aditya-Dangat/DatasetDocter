"""
Scanner Agent - The "Doctor" That Examines Your Data

This agent's job is to look through your dataset and find problems.

Think of it like a doctor doing a checkup:
- Checks for missing values (like missing information)
- Checks for wrong data types (like text in number columns)
- Checks for duplicates (same row appearing twice)
- Checks for outliers (weird values that don't make sense)

It creates a list of all problems found (called "Issues").
"""

from typing import List
import pandas as pd
import numpy as np

from src.core.dataset import Dataset
from src.core.diagnostics import Issue
from src.llm.gemini_client import GeminiClient


class ScannerAgent:
    """
    The Scanner Agent - Finds problems in datasets
    
    Simple workflow:
        1. Receives a Dataset
        2. Scans each column for problems
        3. Creates Issue objects for each problem found
        4. Returns list of all issues
    """
    
    def __init__(self):
        """Initialize the Scanner Agent"""
        self.name = "ScannerAgent"
        self.gemini = GeminiClient()  # AI assistant for complex pattern detection
    
    def scan(self, dataset: Dataset) -> List[Issue]:
        """
        Main method - Scan the dataset for problems
        
        Args:
            dataset: The Dataset object to scan
        
        Returns:
            List of Issue objects (all problems found)
        """
        issues = []
        
        print(f"   🔍 Scanning {dataset.shape[0]} rows × {dataset.shape[1]} columns...")
        
        # Scan for different types of problems
        issues.extend(self._scan_missing_values(dataset))
        issues.extend(self._scan_type_inconsistencies(dataset))
        issues.extend(self._scan_duplicates(dataset))
        issues.extend(self._scan_outliers(dataset))
        
        print(f"   ✅ Found {len(issues)} issues")
        
        return issues
    
    def _scan_missing_values(self, dataset: Dataset) -> List[Issue]:
        """
        Find missing values (empty cells)
        
        Example: A row where "age" is empty
        """
        issues = []
        df = dataset.data
        
        # Check each column
        for column in df.columns:
            # Count both NaN and empty strings as missing
            missing_count = df[column].isna().sum()
            if df[column].dtype == 'object':
                empty_strings = (df[column] == '').sum()
                missing_count += empty_strings
            
            if missing_count > 0:
                # Calculate what percentage is missing
                missing_percent = (missing_count / len(df)) * 100
                
                # Determine severity based on how much is missing
                if missing_percent > 50:
                    severity = "critical"
                elif missing_percent > 20:
                    severity = "high"
                elif missing_percent > 5:
                    severity = "medium"
                else:
                    severity = "low"
                
                issue = Issue(
                    type="missing_values",
                    column=column,
                    severity=severity,
                    description=f"Found {missing_count} missing values ({missing_percent:.1f}%) in column '{column}'",
                    count=missing_count,
                    details={
                        'missing_percent': round(missing_percent, 2),
                        'total_rows': len(df)
                    }
                )
                issues.append(issue)
        
        return issues
    
    def _scan_type_inconsistencies(self, dataset: Dataset) -> List[Issue]:
        """
        Find type inconsistencies (wrong data types)
        
        Example: Text in a number column, or numbers that should be dates
        """
        issues = []
        df = dataset.data
        
        for column in df.columns:
            # Try to detect what the column should be
            expected_type = self._detect_expected_type(df[column])
            actual_type = str(df[column].dtype)
            
            # Check for type mismatches
            if expected_type == "numeric" and actual_type == "object":
                # Should be numbers but contains text
                non_numeric_count = 0
                non_numeric_samples = []
                for value in df[column]:
                    if pd.notna(value):
                        try:
                            float(str(value))
                        except (ValueError, TypeError):
                            non_numeric_count += 1
                            if len(non_numeric_samples) < 3:
                                non_numeric_samples.append(str(value))
                
                if non_numeric_count > 0:
                    # Use Gemini to analyze the pattern if available
                    gemini_insight = ""
                    if self.gemini.is_available() and non_numeric_count > 0:
                        sample_values = df[column].dropna().head(10).tolist()
                        gemini_insight = self.gemini.analyze_pattern(
                            column,
                            sample_values,
                            f"Found {non_numeric_count} non-numeric values: {non_numeric_samples}"
                        )
                    
                    description = f"Column '{column}' should be numeric but contains {non_numeric_count} non-numeric values"
                    
                    issue = Issue(
                        type="type_inconsistency",
                        column=column,
                        severity="high",
                        description=description,
                        count=non_numeric_count,
                        details={
                            'expected_type': 'numeric',
                            'actual_type': actual_type,
                            'gemini_insight': gemini_insight if gemini_insight else None
                        }
                    )
                    issues.append(issue)
        
        return issues
    
    def _scan_duplicates(self, dataset: Dataset) -> List[Issue]:
        """
        Find duplicate rows (same row appearing multiple times)
        """
        issues = []
        df = dataset.data
        
        # Find duplicate rows
        duplicates = df.duplicated()
        duplicate_count = duplicates.sum()
        
        if duplicate_count > 0:
            issue = Issue(
                type="duplicates",
                column=None,  # Duplicates affect entire rows, not specific columns
                severity="medium",
                description=f"Found {duplicate_count} duplicate row(s)",
                count=duplicate_count,
                details={
                    'total_rows': len(df),
                    'unique_rows': len(df) - duplicate_count
                }
            )
            issues.append(issue)
        
        return issues
    
    def _scan_outliers(self, dataset: Dataset) -> List[Issue]:
        """
        Find outliers (values that are way too high or low)
        
        Example: Age = 500 (impossible) or Salary = -1000 (negative salary)
        
        NOTE: Does NOT check identifiers (phone, email, ID) or categorical data
        """
        issues = []
        df = dataset.data
        
        for column in df.columns:
            # Skip if this column shouldn't be checked for outliers
            if not self._should_check_outliers(df[column]):
                continue
            
            # Only check numeric columns (that are measurements, not identifiers)
            if df[column].dtype in ['int64', 'float64']:
                # Calculate outliers using IQR method (Interquartile Range)
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                
                # Skip if IQR is 0 or very small (likely an ID column with sequential numbers)
                if IQR == 0 or IQR < 0.01:
                    continue
                
                # Values outside this range are outliers
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
                outlier_count = len(outliers)
                
                if outlier_count > 0:
                    # Check for impossible values (negative ages, etc.)
                    impossible_count = 0
                    col_lower = column.lower()
                    
                    if 'age' in col_lower:
                        impossible_count = (df[column] < 0).sum() + (df[column] > 150).sum()
                    elif 'salary' in col_lower or 'price' in col_lower or 'cost' in col_lower or 'amount' in col_lower:
                        impossible_count = (df[column] < 0).sum()
                    elif 'percentage' in col_lower or 'percent' in col_lower:
                        impossible_count = ((df[column] < 0) | (df[column] > 100)).sum()
                    elif 'count' in col_lower or 'quantity' in col_lower:
                        impossible_count = (df[column] < 0).sum()
                    
                    severity = "high" if impossible_count > 0 else "medium"
                    
                    issue = Issue(
                        type="outliers",
                        column=column,
                        severity=severity,
                        description=f"Found {outlier_count} outlier(s) in column '{column}'",
                        count=outlier_count,
                        details={
                            'impossible_values': impossible_count,
                            'lower_bound': float(lower_bound) if not pd.isna(lower_bound) else None,
                            'upper_bound': float(upper_bound) if not pd.isna(upper_bound) else None
                        }
                    )
                    issues.append(issue)
        
        return issues
    
    def _detect_expected_type(self, series: pd.Series) -> str:
        """
        Try to guess what type a column should be
        
        Returns: 'numeric', 'identifier', 'categorical', 'text', 'date', 'phone', 'email'
        """
        col_name_lower = series.name.lower()
        
        # If it's already numeric, check if it's an identifier or measurement
        if series.dtype in ['int64', 'float64']:
            # Check if it's likely an ID (high cardinality, sequential)
            unique_ratio = series.nunique() / len(series) if len(series) > 0 else 0
            if unique_ratio > 0.95 and any(kw in col_name_lower for kw in ['id', 'code', 'key', 'mobile', 'phone']):
                return "identifier"
            return "numeric"
        
        # Identifier types (phone, email, ID) - should NOT check for outliers
        phone_keywords = ['phone', 'mobile', 'tel', 'contact', 'cell']
        if any(keyword in col_name_lower for keyword in phone_keywords):
            return "phone"
        
        email_keywords = ['email', 'mail', 'e-mail']
        if any(keyword in col_name_lower for keyword in email_keywords):
            return "email"
        
        id_keywords = ['id', 'identifier', 'code', 'key', 'ref', 'reference']
        if any(keyword in col_name_lower for keyword in id_keywords):
            return "identifier"
        
        # Categorical types - limited distinct values
        categorical_keywords = ['category', 'type', 'status', 'class', 'group', 'label', 'tag']
        if any(keyword in col_name_lower for keyword in categorical_keywords):
            # Also check if it has few unique values
            if series.nunique() < 20:
                return "categorical"
        
        # If column name suggests it should be numeric (measurement)
        numeric_keywords = ['age', 'salary', 'price', 'cost', 'amount', 'count', 'quantity', 'stock', 'qty', 'weight', 'height', 'score', 'rating']
        if any(keyword in col_name_lower for keyword in numeric_keywords):
            return "numeric"
        
        # Check if most values are numeric (even if column is object type)
        if series.dtype == 'object':
            numeric_count = 0
            total_count = 0
            sample_values = series.dropna().head(50)  # Sample more values
            
            for value in sample_values:
                total_count += 1
                try:
                    float(str(value).strip())
                    numeric_count += 1
                except (ValueError, TypeError):
                    pass
            
            # If >70% of values are numeric, it should be numeric
            if total_count > 0 and (numeric_count / total_count) > 0.7:
                # But check if it's an ID (high cardinality)
                unique_ratio = series.nunique() / len(series) if len(series) > 0 else 0
                if unique_ratio > 0.9 and any(kw in col_name_lower for kw in ['id', 'code', 'key']):
                    return "identifier"
                return "numeric"
            
            # Check if it's categorical (few unique values)
            if series.nunique() < 20 and len(series) > 10:
                return "categorical"
        
        # If column name suggests it should be a date
        date_keywords = ['date', 'time', 'created', 'updated', 'birth', 'joined', 'registered']
        if any(keyword in col_name_lower for keyword in date_keywords):
            return "date"
        
        # Text/Name columns
        text_keywords = ['name', 'title', 'description', 'comment', 'note', 'address']
        if any(keyword in col_name_lower for keyword in text_keywords):
            return "text"
        
        # Default to text
        return "text"
    
    def _should_check_outliers(self, series: pd.Series) -> bool:
        """
        Determine if a column should be checked for outliers
        
        Returns False for:
        - Identifiers (phone, email, ID)
        - Categorical data
        - Text data
        - Dates
        """
        expected_type = self._detect_expected_type(series)
        
        # Only check outliers for numeric measurements
        # Don't check for identifiers, categorical, text, dates
        return expected_type == "numeric"
    
    def get_info(self) -> dict:
        """Get information about this agent"""
        return {
            'name': self.name,
            'role': 'Issue Detection',
            'description': 'Scans datasets for data quality issues',
            'detects': [
                'Missing values',
                'Type inconsistencies',
                'Duplicate rows',
                'Outliers'
            ]
        }

