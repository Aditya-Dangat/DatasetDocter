"""
File I/O Tools - MCP-style tools for file operations

These tools handle reading and writing datasets
"""

from typing import Dict, Any, Optional
from pathlib import Path
import pandas as pd
import json
from src.tools.mcp_registry import MCPTool, get_registry


class FileTools:
    """
    File I/O tools following MCP specification
    """
    
    @staticmethod
    def read_csv(filepath: str, **kwargs) -> pd.DataFrame:
        """
        Read a CSV file into a DataFrame
        
        Args:
            filepath: Path to CSV file
            **kwargs: Additional arguments for pd.read_csv
        
        Returns:
            DataFrame
        """
        if not Path(filepath).exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        return pd.read_csv(filepath, **kwargs)
    
    @staticmethod
    def read_json(filepath: str, **kwargs) -> pd.DataFrame:
        """
        Read a JSON file into a DataFrame
        
        Args:
            filepath: Path to JSON file
            **kwargs: Additional arguments for pd.read_json
        
        Returns:
            DataFrame
        """
        if not Path(filepath).exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        return pd.read_json(filepath, **kwargs)
    
    @staticmethod
    def write_csv(dataset: pd.DataFrame, filepath: str, **kwargs) -> Dict[str, Any]:
        """
        Write DataFrame to CSV file
        
        Args:
            dataset: DataFrame to save
            filepath: Output file path
            **kwargs: Additional arguments for pd.to_csv
        
        Returns:
            Dictionary with file info
        """
        dataset.to_csv(filepath, **kwargs)
        file_size = Path(filepath).stat().st_size
        
        return {
            "filepath": filepath,
            "rows": len(dataset),
            "columns": len(dataset.columns),
            "file_size_bytes": file_size,
            "success": True
        }
    
    @staticmethod
    def write_json(dataset: pd.DataFrame, filepath: str, **kwargs) -> Dict[str, Any]:
        """
        Write DataFrame to JSON file
        
        Args:
            dataset: DataFrame to save
            filepath: Output file path
            **kwargs: Additional arguments for pd.to_json
        
        Returns:
            Dictionary with file info
        """
        dataset.to_json(filepath, **kwargs)
        file_size = Path(filepath).stat().st_size
        
        return {
            "filepath": filepath,
            "rows": len(dataset),
            "columns": len(dataset.columns),
            "file_size_bytes": file_size,
            "success": True
        }
    
    @staticmethod
    def get_file_info(filepath: str) -> Dict[str, Any]:
        """
        Get information about a file
        
        Args:
            filepath: Path to file
        
        Returns:
            Dictionary with file metadata
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        stat = path.stat()
        
        return {
            "filepath": str(path),
            "filename": path.name,
            "extension": path.suffix,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "exists": True
        }


def register_file_tools(registry):
    """Register all file I/O tools"""
    
    # Read CSV Tool
    registry.register(MCPTool(
        name="read_csv",
        description="Read a CSV file into a pandas DataFrame. Supports all pandas read_csv options.",
        input_schema={
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to CSV file"
                }
            },
            "required": ["filepath"]
        },
        handler=FileTools.read_csv,
        category="file",
        version="1.0.0"
    ))
    
    # Read JSON Tool
    registry.register(MCPTool(
        name="read_json",
        description="Read a JSON file into a pandas DataFrame. Supports all pandas read_json options.",
        input_schema={
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to JSON file"
                }
            },
            "required": ["filepath"]
        },
        handler=FileTools.read_json,
        category="file",
        version="1.0.0"
    ))
    
    # Write CSV Tool
    registry.register(MCPTool(
        name="write_csv",
        description="Write a DataFrame to a CSV file. Supports all pandas to_csv options.",
        input_schema={
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Output file path"
                }
            },
            "required": ["filepath"]
        },
        handler=FileTools.write_csv,
        category="file",
        version="1.0.0"
    ))
    
    # Write JSON Tool
    registry.register(MCPTool(
        name="write_json",
        description="Write a DataFrame to a JSON file. Supports all pandas to_json options.",
        input_schema={
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Output file path"
                }
            },
            "required": ["filepath"]
        },
        handler=FileTools.write_json,
        category="file",
        version="1.0.0"
    ))
    
    # Get File Info Tool
    registry.register(MCPTool(
        name="get_file_info",
        description="Get metadata about a file (size, extension, etc.).",
        input_schema={
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to file"
                }
            },
            "required": ["filepath"]
        },
        handler=FileTools.get_file_info,
        category="file",
        version="1.0.0"
    ))
