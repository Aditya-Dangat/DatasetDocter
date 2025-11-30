"""
Data Manipulation Tools - MCP-style tools for data operations

These tools can be called by agents to perform data transformations
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from src.tools.mcp_registry import MCPTool, get_registry


class DataTools:
    """
    Data manipulation tools following MCP specification
    
    These tools are used by agents to perform data operations
    """
    
    @staticmethod
    def detect_missing_values(dataset: pd.DataFrame, column: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect missing values in dataset or specific column
        
        Args:
            dataset: DataFrame to analyze
            column: Optional column name (if None, checks all columns)
        
        Returns:
            Dictionary with missing value statistics
        """
        if column:
            if column not in dataset.columns:
                raise ValueError(f"Column '{column}' not found")
            missing_count = dataset[column].isna().sum()
            total = len(dataset)
            missing_percent = (missing_count / total * 100) if total > 0 else 0
            return {
                "column": column,
                "missing_count": int(missing_count),
                "total_rows": total,
                "missing_percent": round(missing_percent, 2)
            }
        else:
            # Check all columns
            result = {}
            for col in dataset.columns:
                missing_count = dataset[col].isna().sum()
                total = len(dataset)
                missing_percent = (missing_count / total * 100) if total > 0 else 0
                result[col] = {
                    "missing_count": int(missing_count),
                    "missing_percent": round(missing_percent, 2)
                }
            return result
    
    @staticmethod
    def impute_median(dataset: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        Impute missing values with median
        
        Args:
            dataset: DataFrame to modify
            column: Column name to impute
        
        Returns:
            Modified DataFrame
        """
        if column not in dataset.columns:
            raise ValueError(f"Column '{column}' not found")
        
        dataset = dataset.copy()
        median_value = dataset[column].median()
        dataset[column].fillna(median_value, inplace=True)
        return dataset
    
    @staticmethod
    def impute_mode(dataset: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        Impute missing values with mode (most common value)
        
        Args:
            dataset: DataFrame to modify
            column: Column name to impute
        
        Returns:
            Modified DataFrame
        """
        if column not in dataset.columns:
            raise ValueError(f"Column '{column}' not found")
        
        dataset = dataset.copy()
        mode_value = dataset[column].mode()
        if len(mode_value) > 0:
            dataset[column].fillna(mode_value[0], inplace=True)
        else:
            dataset[column].fillna("MISSING", inplace=True)
        return dataset
    
    @staticmethod
    def convert_to_numeric(dataset: pd.DataFrame, column: str, errors: str = 'coerce') -> pd.DataFrame:
        """
        Convert column to numeric type
        
        Args:
            dataset: DataFrame to modify
            column: Column name to convert
            errors: How to handle errors ('coerce', 'raise', 'ignore')
        
        Returns:
            Modified DataFrame
        """
        if column not in dataset.columns:
            raise ValueError(f"Column '{column}' not found")
        
        dataset = dataset.copy()
        dataset[column] = pd.to_numeric(dataset[column], errors=errors)
        return dataset
    
    @staticmethod
    def remove_duplicates(dataset: pd.DataFrame, subset: Optional[List[str]] = None, keep: str = 'first') -> pd.DataFrame:
        """
        Remove duplicate rows
        
        Args:
            dataset: DataFrame to modify
            subset: Columns to consider (None = all columns)
            keep: Which duplicate to keep ('first', 'last', False)
        
        Returns:
            DataFrame with duplicates removed
        """
        dataset = dataset.copy()
        return dataset.drop_duplicates(subset=subset, keep=keep)
    
    @staticmethod
    def detect_outliers_iqr(dataset: pd.DataFrame, column: str) -> Dict[str, Any]:
        """
        Detect outliers using IQR (Interquartile Range) method
        
        Args:
            dataset: DataFrame to analyze
            column: Column name to check
        
        Returns:
            Dictionary with outlier statistics
        """
        if column not in dataset.columns:
            raise ValueError(f"Column '{column}' not found")
        
        if dataset[column].dtype not in ['int64', 'float64']:
            raise ValueError(f"Column '{column}' must be numeric")
        
        Q1 = dataset[column].quantile(0.25)
        Q3 = dataset[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = dataset[(dataset[column] < lower_bound) | (dataset[column] > upper_bound)]
        
        return {
            "column": column,
            "outlier_count": len(outliers),
            "lower_bound": float(lower_bound) if not pd.isna(lower_bound) else None,
            "upper_bound": float(upper_bound) if not pd.isna(upper_bound) else None,
            "outlier_indices": outliers.index.tolist()
        }
    
    @staticmethod
    def get_column_statistics(dataset: pd.DataFrame, column: str) -> Dict[str, Any]:
        """
        Get statistical summary of a column
        
        Args:
            dataset: DataFrame to analyze
            column: Column name
        
        Returns:
            Dictionary with statistics
        """
        if column not in dataset.columns:
            raise ValueError(f"Column '{column}' not found")
        
        col_data = dataset[column]
        stats = {
            "column": column,
            "dtype": str(col_data.dtype),
            "total_rows": len(col_data),
            "non_null_count": int(col_data.notna().sum()),
            "null_count": int(col_data.isna().sum()),
            "unique_count": int(col_data.nunique())
        }
        
        if pd.api.types.is_numeric_dtype(col_data):
            stats.update({
                "mean": float(col_data.mean()) if not col_data.isna().all() else None,
                "median": float(col_data.median()) if not col_data.isna().all() else None,
                "std": float(col_data.std()) if not col_data.isna().all() else None,
                "min": float(col_data.min()) if not col_data.isna().all() else None,
                "max": float(col_data.max()) if not col_data.isna().all() else None
            })
        
        return stats


def register_data_tools(registry):
    """Register all data manipulation tools"""
    
    # Detect Missing Values Tool
    registry.register(MCPTool(
        name="detect_missing_values",
        description="Detect missing values in a dataset or specific column. Returns statistics about missing data.",
        input_schema={
            "type": "object",
            "properties": {
                "column": {
                    "type": "string",
                    "description": "Column name to check (optional, checks all if not provided)"
                }
            },
            "required": []
        },
        handler=DataTools.detect_missing_values,
        category="data",
        version="1.0.0"
    ))
    
    # Impute Median Tool
    registry.register(MCPTool(
        name="impute_median",
        description="Fill missing values in a numeric column with the median value. Preserves data distribution.",
        input_schema={
            "type": "object",
            "properties": {
                "column": {
                    "type": "string",
                    "description": "Column name to impute"
                }
            },
            "required": ["column"]
        },
        handler=DataTools.impute_median,
        category="data",
        version="1.0.0"
    ))
    
    # Impute Mode Tool
    registry.register(MCPTool(
        name="impute_mode",
        description="Fill missing values in a categorical column with the most common value (mode).",
        input_schema={
            "type": "object",
            "properties": {
                "column": {
                    "type": "string",
                    "description": "Column name to impute"
                }
            },
            "required": ["column"]
        },
        handler=DataTools.impute_mode,
        category="data",
        version="1.0.0"
    ))
    
    # Convert to Numeric Tool
    registry.register(MCPTool(
        name="convert_to_numeric",
        description="Convert a column to numeric type. Invalid values become NaN.",
        input_schema={
            "type": "object",
            "properties": {
                "column": {
                    "type": "string",
                    "description": "Column name to convert"
                },
                "errors": {
                    "type": "string",
                    "enum": ["coerce", "raise", "ignore"],
                    "description": "How to handle conversion errors",
                    "default": "coerce"
                }
            },
            "required": ["column"]
        },
        handler=DataTools.convert_to_numeric,
        category="data",
        version="1.0.0"
    ))
    
    # Remove Duplicates Tool
    registry.register(MCPTool(
        name="remove_duplicates",
        description="Remove duplicate rows from the dataset. Can specify columns to check.",
        input_schema={
            "type": "object",
            "properties": {
                "subset": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Columns to consider for duplicates (all if not specified)"
                },
                "keep": {
                    "type": "string",
                    "enum": ["first", "last"],
                    "description": "Which duplicate to keep",
                    "default": "first"
                }
            },
            "required": []
        },
        handler=DataTools.remove_duplicates,
        category="data",
        version="1.0.0"
    ))
    
    # Detect Outliers Tool
    registry.register(MCPTool(
        name="detect_outliers_iqr",
        description="Detect outliers in a numeric column using IQR (Interquartile Range) method.",
        input_schema={
            "type": "object",
            "properties": {
                "column": {
                    "type": "string",
                    "description": "Column name to check for outliers"
                }
            },
            "required": ["column"]
        },
        handler=DataTools.detect_outliers_iqr,
        category="data",
        version="1.0.0"
    ))
    
    # Get Column Statistics Tool
    registry.register(MCPTool(
        name="get_column_statistics",
        description="Get statistical summary of a column (mean, median, std, min, max for numeric columns).",
        input_schema={
            "type": "object",
            "properties": {
                "column": {
                    "type": "string",
                    "description": "Column name to analyze"
                }
            },
            "required": ["column"]
        },
        handler=DataTools.get_column_statistics,
        category="data",
        version="1.0.0"
    ))

