"""
Context Manager - Handles Large Datasets Efficiently

This compacts and summarizes data to make processing faster.
Think of it like a summary - instead of reading the whole book,
you read the summary first, then dive deeper if needed.
"""

from typing import Dict, Any
import pandas as pd
from src.core.dataset import Dataset


class ContextManager:
    """
    Manages context for large datasets
    
    Simple explanation:
    - Creates compact summaries of large datasets
    - Only loads full data when needed
    - Caches summaries for reuse
    """
    
    def __init__(self):
        """Initialize context manager"""
        self.cache: Dict[str, Dict] = {}
    
    def compact_dataset_summary(self, dataset: Dataset) -> Dict[str, Any]:
        """
        Create a compact summary of the dataset
        
        Instead of processing the whole dataset, create a summary:
        - Shape, column names, data types
        - Sample rows
        - Basic statistics
        """
        df = dataset.data
        
        summary = {
            'name': dataset.name,
            'shape': dataset.shape,
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'null_counts': df.isnull().sum().to_dict(),
            'sample_rows': df.head(5).to_dict('records'),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024)
        }
        
        # Add basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            summary['numeric_stats'] = df[numeric_cols].describe().to_dict()
        
        return summary
    
    def expand_context(self, summary: Dict[str, Any], full_dataset: Dataset) -> Dataset:
        """
        Expand from summary to full dataset when needed
        
        For now, just return the dataset (in future, could load lazily)
        """
        return full_dataset
    
    def get_cached_summary(self, dataset_name: str) -> Dict[str, Any]:
        """Get cached summary if available"""
        return self.cache.get(dataset_name)
    
    def cache_summary(self, dataset_name: str, summary: Dict[str, Any]):
        """Cache a summary for later use"""
        self.cache[dataset_name] = summary

