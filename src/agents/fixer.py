"""
Fixer Agent - The "Nurse" That Applies Treatments

This agent's job is to fix the problems found by the Scanner.

Think of it like a nurse applying treatments:
- Fills missing values (like filling in missing information)
- Fixes type errors (converts wrong types to correct ones)
- Removes duplicates (gets rid of duplicate rows)
- Handles outliers (fixes or removes weird values)

It applies fixes and records what it did.
"""

from typing import List
import pandas as pd
import numpy as np

from src.core.dataset import Dataset
from src.core.diagnostics import Issue, Fix
from src.llm.gemini_client import GeminiClient


class FixerAgent:
    """
    The Fixer Agent - Applies fixes to datasets
    
    Simple workflow:
        1. Receives Dataset and list of Issues
        2. For each issue, applies appropriate fix
        3. Records what was fixed
        4. Returns list of Fix objects
    """
    
    def __init__(self):
        """Initialize the Fixer Agent"""
        self.name = "FixerAgent"
        self.gemini = GeminiClient()  # AI assistant for intelligent fix strategies
    
    def fix(self, dataset: Dataset, issues: List[Issue]) -> List[Fix]:
        """
        Main method - Fix all issues in the dataset
        
        Args:
            dataset: The Dataset to fix
            issues: List of Issue objects found by Scanner
        
        Returns:
            List of Fix objects (what was fixed)
        """
        fixes = []
        
        print(f"   🔧 Applying fixes to {len(issues)} issue(s)...")
        
        # Group issues by type for efficient fixing
        issues_by_type = {}
        for issue in issues:
            if issue.type not in issues_by_type:
                issues_by_type[issue.type] = []
            issues_by_type[issue.type].append(issue)
        
        # Fix missing values
        if 'missing_values' in issues_by_type:
            fixes.extend(self._fix_missing_values(dataset, issues_by_type['missing_values']))
        
        # Fix type inconsistencies
        if 'type_inconsistency' in issues_by_type:
            fixes.extend(self._fix_type_inconsistencies(dataset, issues_by_type['type_inconsistency']))
        
        # Fix duplicates
        if 'duplicates' in issues_by_type:
            fixes.extend(self._fix_duplicates(dataset, issues_by_type['duplicates']))
        
        # Fix outliers
        if 'outliers' in issues_by_type:
            fixes.extend(self._fix_outliers(dataset, issues_by_type['outliers']))
        
        print(f"   ✅ Applied {len(fixes)} fix(es)")
        
        return fixes
    
    def _fix_missing_values(self, dataset: Dataset, issues: List[Issue]) -> List[Fix]:
        """Fix missing values using appropriate imputation strategy"""
        fixes = []
        df = dataset.data
        
        for issue in issues:
            column = issue.column
            # Count both NaN and empty strings as missing
            missing_count_before = df[column].isna().sum()
            if df[column].dtype == 'object':
                empty_strings = (df[column] == '').sum()
                missing_count_before += empty_strings
            
            if missing_count_before == 0:
                continue  # Already fixed or no longer missing
            
            # Replace empty strings with NaN first (for object columns)
            if df[column].dtype == 'object':
                df[column] = df[column].replace('', pd.NA)
                # Recalculate missing count after replacing empty strings
                missing_count_before = df[column].isna().sum()
            
            # Choose imputation strategy based on column type
            if df[column].dtype in ['int64', 'float64']:
                # Use Gemini to suggest best strategy if available
                gemini_suggestion = ""
                if self.gemini.is_available():
                    context = {
                        'column': column,
                        'missing_count': missing_count_before,
                        'total_rows': len(df),
                        'current_distribution': {
                            'mean': float(df[column].mean()) if not df[column].isna().all() else None,
                            'median': float(df[column].median()) if not df[column].isna().all() else None,
                            'std': float(df[column].std()) if not df[column].isna().all() else None
                        }
                    }
                    gemini_suggestion = self.gemini.suggest_fix_strategy("missing_values", column, context)
                
                # Numeric column - use median (or follow Gemini suggestion if it recommends mean)
                if gemini_suggestion and "mean" in gemini_suggestion.lower() and "median" not in gemini_suggestion.lower():
                    fill_value = df[column].mean()
                    method = "mean_imputation_ai_suggested"
                    description = f"Filled {missing_count_before} missing values in '{column}' with mean ({fill_value:.2f}) [AI suggested]"
                else:
                    fill_value = df[column].median()
                    method = "median_imputation"
                    description = f"Filled {missing_count_before} missing values in '{column}' with median ({fill_value:.2f})"
                    if gemini_suggestion:
                        description += f" | AI: {gemini_suggestion[:80]}"
                
                df[column].fillna(fill_value, inplace=True)
            else:
                # Categorical/text column - use mode (most common value)
                mode_value = df[column].mode()
                if len(mode_value) > 0:
                    fill_value = mode_value[0]
                    df[column].fillna(fill_value, inplace=True)
                    method = "mode_imputation"
                    description = f"Filled {missing_count_before} missing values in '{column}' with mode ('{fill_value}')"
                else:
                    # No mode available, use placeholder
                    df[column].fillna("MISSING", inplace=True)
                    method = "placeholder_imputation"
                    description = f"Filled {missing_count_before} missing values in '{column}' with placeholder 'MISSING'"
            
            missing_count_after = df[column].isna().sum()
            
            fix = Fix(
                issue_type="missing_values",
                column=column,
                method=method,
                description=description,
                before_count=missing_count_before,
                after_count=missing_count_after,
                success=(missing_count_after == 0)
            )
            fixes.append(fix)
            
            # Log the change
            dataset.log_change("imputation", description, {
                'column': column,
                'method': method,
                'filled_count': missing_count_before
            })
        
        return fixes
    
    def _fix_type_inconsistencies(self, dataset: Dataset, issues: List[Issue]) -> List[Fix]:
        """Fix type inconsistencies by converting or removing invalid values"""
        fixes = []
        df = dataset.data
        
        for issue in issues:
            column = issue.column
            invalid_count_before = issue.count
            
            # Get original NaN count if available
            original_na = 0
            if hasattr(dataset, 'original_data') and dataset.original_data is not None and column in dataset.original_data.columns:
                original_na = dataset.original_data[column].isna().sum()
            else:
                # If no original data, use current NaN count before conversion
                original_na = df[column].isna().sum()
            
            # Replace empty strings with NaN first
            if df[column].dtype == 'object':
                df[column] = df[column].replace('', pd.NA)
            
            # Try to convert to numeric, invalid values become NaN
            df[column] = pd.to_numeric(df[column], errors='coerce')
            
            # Count how many new NaN values were created (from invalid conversions)
            new_na = df[column].isna().sum()
            new_nans_from_conversion = max(0, new_na - original_na)
            actually_fixed = invalid_count_before - new_nans_from_conversion
            
            # If there are still invalid values (new NaN from conversion), fill them with median
            if new_nans_from_conversion > 0:
                median_value = df[column].median()
                if pd.notna(median_value):
                    df[column].fillna(median_value, inplace=True)
                    method = "type_conversion_with_median_fallback"
                    description = f"Converted {actually_fixed} invalid values in '{column}' to numeric, filled {new_nans_from_conversion} remaining with median ({median_value:.2f})"
                else:
                    # If no median available, use mode of numeric values
                    numeric_values = df[column].dropna()
                    if len(numeric_values) > 0:
                        mode_value = numeric_values.mode()[0] if len(numeric_values.mode()) > 0 else 0
                        df[column].fillna(mode_value, inplace=True)
                        method = "type_conversion_with_mode_fallback"
                        description = f"Converted {actually_fixed} invalid values in '{column}' to numeric, filled {new_nans_from_conversion} remaining with mode ({mode_value:.2f})"
                    else:
                        df[column].fillna(0, inplace=True)
                        method = "type_conversion_with_zero_fallback"
                        description = f"Converted {actually_fixed} invalid values in '{column}' to numeric, filled {new_nans_from_conversion} remaining with 0"
            else:
                method = "type_conversion"
                description = f"Converted {invalid_count_before} invalid values in '{column}' to numeric"
            
            invalid_count_after = 0  # All should be fixed now
            
            fix = Fix(
                issue_type="type_inconsistency",
                column=column,
                method=method,
                description=description,
                before_count=invalid_count_before,
                after_count=invalid_count_after,
                success=True
            )
            fixes.append(fix)
            
            dataset.log_change("type_conversion", description, {
                'column': column,
                'method': method
            })
        
        return fixes
    
    def _fix_duplicates(self, dataset: Dataset, issues: List[Issue]) -> List[Fix]:
        """Remove duplicate rows"""
        fixes = []
        df = dataset.data
        
        for issue in issues:
            duplicate_count_before = df.duplicated().sum()
            
            if duplicate_count_before > 0:
                # Remove duplicates, keeping first occurrence
                df.drop_duplicates(inplace=True, keep='first')
                duplicate_count_after = df.duplicated().sum()
                
                fix = Fix(
                    issue_type="duplicates",
                    column=None,
                    method="remove_duplicates",
                    description=f"Removed {duplicate_count_before} duplicate row(s)",
                    before_count=duplicate_count_before,
                    after_count=duplicate_count_after,
                    success=(duplicate_count_after == 0)
                )
                fixes.append(fix)
                
                dataset.log_change("deduplication", f"Removed {duplicate_count_before} duplicate rows")
        
        return fixes
    
    def _fix_outliers(self, dataset: Dataset, issues: List[Issue]) -> List[Fix]:
        """Fix outliers by capping them to reasonable values"""
        fixes = []
        df = dataset.data
        
        for issue in issues:
            column = issue.column
            if column is None:
                continue
            
            if df[column].dtype not in ['int64', 'float64']:
                continue  # Only fix numeric columns
            
            outlier_count_before = issue.count
            details = issue.details
            
            # Use IQR method to cap outliers
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Cap values outside bounds
            before_outliers = ((df[column] < lower_bound) | (df[column] > upper_bound)).sum()
            
            # For impossible values (negative ages, etc.), set to median
            if 'age' in column.lower():
                # Age can't be negative or > 150
                df.loc[df[column] < 0, column] = df[column].median()
                df.loc[df[column] > 150, column] = df[column].median()
                method = "outlier_capping_age"
                description = f"Capped {before_outliers} outlier(s) in '{column}' to reasonable age values"
            elif 'salary' in column.lower() or 'price' in column.lower():
                # Salary/price can't be negative
                negative_count = (df[column] < 0).sum()
                if negative_count > 0:
                    df.loc[df[column] < 0, column] = df[column].median()
                # Cap extreme positive values
                extreme_high = (df[column] > upper_bound).sum()
                if extreme_high > 0:
                    df.loc[df[column] > upper_bound, column] = upper_bound
                method = "outlier_capping_financial"
                description = f"Capped {before_outliers} outlier(s) in '{column}' to reasonable values"
            else:
                # Generic capping
                df.loc[df[column] < lower_bound, column] = lower_bound
                df.loc[df[column] > upper_bound, column] = upper_bound
                method = "outlier_capping"
                description = f"Capped {before_outliers} outlier(s) in '{column}' using IQR method"
            
            outlier_count_after = ((df[column] < lower_bound) | (df[column] > upper_bound)).sum()
            
            fix = Fix(
                issue_type="outliers",
                column=column,
                method=method,
                description=description,
                before_count=outlier_count_before,
                after_count=outlier_count_after,
                success=(outlier_count_after == 0)
            )
            fixes.append(fix)
            
            dataset.log_change("outlier_fix", description, {
                'column': column,
                'method': method
            })
        
        return fixes
    
    def get_info(self) -> dict:
        """Get information about this agent"""
        return {
            'name': self.name,
            'role': 'Issue Fixing',
            'description': 'Applies fixes to data quality issues',
            'fixes': [
                'Missing value imputation',
                'Type conversion',
                'Duplicate removal',
                'Outlier capping'
            ]
        }

