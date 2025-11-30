"""
Dataset Wrapper - A Simple Container for Our Data

Think of this like a box that holds your dataset.
It makes it easier to work with the data and keep track of changes.
"""

import pandas as pd
from typing import Optional, Dict, Any
import json


class Dataset:
    """
    A wrapper around pandas DataFrame that adds extra features.
    
    Why we need this:
    - Keeps track of original data (before fixes)
    - Stores metadata (info about the data)
    - Makes it easy to save/load
    """
    
    def __init__(self, data: pd.DataFrame, name: str = "dataset"):
        """
        Create a new Dataset
        
        Args:
            data: The actual data (pandas DataFrame)
            name: A name for this dataset (like "customer_data.csv")
        """
        self.data = data.copy()  # Make a copy so we don't modify original
        self.original_data = data.copy()  # Keep original for comparison
        self.name = name
        self.metadata = {
            'shape': data.shape,  # (rows, columns)
            'columns': list(data.columns),
            'dtypes': data.dtypes.to_dict(),  # Data types of each column
            'memory_usage': data.memory_usage(deep=True).sum()
        }
        self.changes_log = []  # Track what we changed
    
    def get_shape(self) -> tuple:
        """Get the dimensions: (number of rows, number of columns)"""
        return self.data.shape
    
    def get_columns(self) -> list:
        """Get list of column names"""
        return list(self.data.columns)
    
    def get_info(self) -> Dict[str, Any]:
        """Get summary information about the dataset"""
        return {
            'name': self.name,
            'shape': self.shape,
            'columns': self.get_columns(),
            'memory_usage_mb': self.metadata['memory_usage'] / (1024 * 1024),
            'changes_count': len(self.changes_log)
        }
    
    def log_change(self, change_type: str, description: str, details: Dict = None):
        """
        Record a change we made to the data
        
        Example:
            dataset.log_change("imputation", "Filled missing values in 'age' column")
        """
        self.changes_log.append({
            'type': change_type,
            'description': description,
            'details': details or {}
        })
    
    def save_cleaned(self, filepath: str):
        """Save the cleaned dataset to a file"""
        if filepath.endswith('.csv'):
            self.data.to_csv(filepath, index=False)
        elif filepath.endswith('.json'):
            self.data.to_json(filepath, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported file format: {filepath}")
    
    @property
    def shape(self) -> tuple:
        """Shortcut to get shape"""
        return self.data.shape
    
    @classmethod
    def from_file(cls, filepath: str) -> 'Dataset':
        """
        Load a dataset from a file
        
        Usage:
            dataset = Dataset.from_file("my_data.csv")
        """
        if filepath.endswith('.csv'):
            data = pd.read_csv(filepath)
        elif filepath.endswith('.json'):
            data = pd.read_json(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath}")
        
        name = filepath.split('/')[-1]  # Get filename
        return cls(data, name)

