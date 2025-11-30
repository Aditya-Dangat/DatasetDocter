"""
Validation Tools - MCP-style tools for data validation

These tools validate data quality and schema compliance
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from src.tools.mcp_registry import MCPTool, get_registry


class ValidationTools:
    """
    Data validation tools following MCP specification
    """
    
    @staticmethod
    def validate_schema(dataset: pd.DataFrame, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate dataset against a schema
        
        Args:
            dataset: DataFrame to validate
            schema: Schema definition with column types and constraints
        
        Returns:
            Validation result with pass/fail and details
        """
        errors = []
        warnings = []
        
        # Check required columns
        required_columns = schema.get("required_columns", [])
        for col in required_columns:
            if col not in dataset.columns:
                errors.append(f"Required column '{col}' is missing")
        
        # Check column types
        column_types = schema.get("column_types", {})
        for col, expected_type in column_types.items():
            if col in dataset.columns:
                actual_type = str(dataset[col].dtype)
                if not ValidationTools._type_matches(actual_type, expected_type):
                    errors.append(
                        f"Column '{col}' has type {actual_type}, expected {expected_type}"
                    )
        
        # Check constraints
        constraints = schema.get("constraints", {})
        for col, constraint_list in constraints.items():
            if col in dataset.columns:
                for constraint in constraint_list:
                    result = ValidationTools._check_constraint(
                        dataset, col, constraint
                    )
                    if not result["valid"]:
                        if constraint.get("severity") == "error":
                            errors.append(result["message"])
                        else:
                            warnings.append(result["message"])
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "total_errors": len(errors),
            "total_warnings": len(warnings)
        }
    
    @staticmethod
    def _type_matches(actual: str, expected: str) -> bool:
        """Check if actual type matches expected type"""
        type_map = {
            "numeric": ["int64", "float64", "int32", "float32"],
            "integer": ["int64", "int32"],
            "float": ["float64", "float32"],
            "string": ["object", "string"],
            "boolean": ["bool"]
        }
        
        if expected in type_map:
            return actual in type_map[expected]
        return actual == expected
    
    @staticmethod
    def _check_constraint(dataset: pd.DataFrame, column: str, constraint: Dict[str, Any]) -> Dict[str, Any]:
        """Check a single constraint on a column"""
        constraint_type = constraint.get("type")
        message = ""
        valid = True
        
        if constraint_type == "not_null":
            null_count = dataset[column].isna().sum()
            if null_count > 0:
                valid = False
                message = f"Column '{column}' has {null_count} null values (not_null constraint violated)"
        
        elif constraint_type == "min":
            min_value = constraint.get("value")
            if pd.api.types.is_numeric_dtype(dataset[column]):
                if (dataset[column] < min_value).any():
                    valid = False
                    message = f"Column '{column}' has values below minimum {min_value}"
        
        elif constraint_type == "max":
            max_value = constraint.get("value")
            if pd.api.types.is_numeric_dtype(dataset[column]):
                if (dataset[column] > max_value).any():
                    valid = False
                    message = f"Column '{column}' has values above maximum {max_value}"
        
        elif constraint_type == "unique":
            if dataset[column].duplicated().any():
                valid = False
                message = f"Column '{column}' has duplicate values (unique constraint violated)"
        
        elif constraint_type == "in_range":
            min_val = constraint.get("min")
            max_val = constraint.get("max")
            if pd.api.types.is_numeric_dtype(dataset[column]):
                out_of_range = (dataset[column] < min_val) | (dataset[column] > max_val)
                if out_of_range.any():
                    valid = False
                    count = out_of_range.sum()
                    message = f"Column '{column}' has {count} values outside range [{min_val}, {max_val}]"
        
        return {"valid": valid, "message": message}
    
    @staticmethod
    def check_data_quality(dataset: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive data quality check
        
        Args:
            dataset: DataFrame to check
        
        Returns:
            Quality report with scores and issues
        """
        issues = []
        total_issues = 0
        
        # Check for missing values
        for col in dataset.columns:
            missing_count = dataset[col].isna().sum()
            if missing_count > 0:
                missing_percent = (missing_count / len(dataset)) * 100
                issues.append({
                    "type": "missing_values",
                    "column": col,
                    "count": int(missing_count),
                    "percent": round(missing_percent, 2)
                })
                total_issues += 1
        
        # Check for duplicates
        duplicate_count = dataset.duplicated().sum()
        if duplicate_count > 0:
            issues.append({
                "type": "duplicates",
                "count": int(duplicate_count)
            })
            total_issues += 1
        
        # Calculate quality score (0-100)
        max_possible_issues = len(dataset.columns) * 2 + 1  # Missing + type issues + duplicates
        quality_score = max(0, 100 - (total_issues / max_possible_issues * 100))
        
        return {
            "quality_score": round(quality_score, 2),
            "total_issues": total_issues,
            "issues": issues,
            "total_rows": len(dataset),
            "total_columns": len(dataset.columns)
        }


def register_validation_tools(registry):
    """Register all validation tools"""
    
    # Validate Schema Tool
    registry.register(MCPTool(
        name="validate_schema",
        description="Validate a dataset against a schema definition. Checks column types, required columns, and constraints.",
        input_schema={
            "type": "object",
            "properties": {
                "schema": {
                    "type": "object",
                    "description": "Schema definition with column types and constraints",
                    "properties": {
                        "required_columns": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "column_types": {
                            "type": "object",
                            "additionalProperties": {"type": "string"}
                        },
                        "constraints": {
                            "type": "object",
                            "additionalProperties": {
                                "type": "array",
                                "items": {"type": "object"}
                            }
                        }
                    }
                }
            },
            "required": ["schema"]
        },
        handler=ValidationTools.validate_schema,
        category="validation",
        version="1.0.0"
    ))
    
    # Check Data Quality Tool
    registry.register(MCPTool(
        name="check_data_quality",
        description="Perform comprehensive data quality check. Returns quality score and list of issues.",
        input_schema={
            "type": "object",
            "properties": {},
            "required": []
        },
        handler=ValidationTools.check_data_quality,
        category="validation",
        version="1.0.0"
    ))

