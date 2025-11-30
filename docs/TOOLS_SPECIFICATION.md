# MCP Tools Specification

## Overview

DatasetDoctor implements MCP (Model Context Protocol) style tools that agents can use to perform data operations.

## Tool Categories

### 1. Data Tools (`data`)
Tools for data manipulation and transformation.

### 2. Validation Tools (`validation`)
Tools for data quality validation and schema checking.

### 3. File Tools (`file`)
Tools for reading and writing datasets.

---

## Available Tools

### Data Tools

#### `detect_missing_values`
**Description:** Detect missing values in a dataset or specific column.

**Parameters:**
- `column` (string, optional): Column name to check. If not provided, checks all columns.

**Returns:** Dictionary with missing value statistics.

**Example:**
```python
result = registry.execute("detect_missing_values", {"column": "age"})
# Returns: {"column": "age", "missing_count": 5, "total_rows": 100, "missing_percent": 5.0}
```

#### `impute_median`
**Description:** Fill missing values in a numeric column with the median value.

**Parameters:**
- `column` (string, required): Column name to impute.

**Returns:** Modified DataFrame.

#### `impute_mode`
**Description:** Fill missing values with the most common value (mode).

**Parameters:**
- `column` (string, required): Column name to impute.

**Returns:** Modified DataFrame.

#### `convert_to_numeric`
**Description:** Convert a column to numeric type.

**Parameters:**
- `column` (string, required): Column name to convert.
- `errors` (string, optional): How to handle errors ('coerce', 'raise', 'ignore'). Default: 'coerce'.

**Returns:** Modified DataFrame.

#### `remove_duplicates`
**Description:** Remove duplicate rows from the dataset.

**Parameters:**
- `subset` (array, optional): Columns to consider for duplicates.
- `keep` (string, optional): Which duplicate to keep ('first' or 'last'). Default: 'first'.

**Returns:** DataFrame with duplicates removed.

#### `detect_outliers_iqr`
**Description:** Detect outliers using IQR (Interquartile Range) method.

**Parameters:**
- `column` (string, required): Column name to check.

**Returns:** Dictionary with outlier statistics.

#### `get_column_statistics`
**Description:** Get statistical summary of a column.

**Parameters:**
- `column` (string, required): Column name to analyze.

**Returns:** Dictionary with statistics (mean, median, std, min, max, etc.).

---

### Validation Tools

#### `validate_schema`
**Description:** Validate a dataset against a schema definition.

**Parameters:**
- `schema` (object, required): Schema definition with:
  - `required_columns` (array): List of required column names
  - `column_types` (object): Map of column names to expected types
  - `constraints` (object): Map of column names to constraint arrays

**Returns:** Validation result with pass/fail and error details.

#### `check_data_quality`
**Description:** Perform comprehensive data quality check.

**Parameters:** None

**Returns:** Quality report with score and issues list.

---

### File Tools

#### `read_csv`
**Description:** Read a CSV file into a DataFrame.

**Parameters:**
- `filepath` (string, required): Path to CSV file.

**Returns:** DataFrame.

#### `read_json`
**Description:** Read a JSON file into a DataFrame.

**Parameters:**
- `filepath` (string, required): Path to JSON file.

**Returns:** DataFrame.

#### `write_csv`
**Description:** Write a DataFrame to a CSV file.

**Parameters:**
- `filepath` (string, required): Output file path.

**Returns:** Dictionary with file info.

#### `write_json`
**Description:** Write a DataFrame to a JSON file.

**Parameters:**
- `filepath` (string, required): Output file path.

**Returns:** Dictionary with file info.

#### `get_file_info`
**Description:** Get metadata about a file.

**Parameters:**
- `filepath` (string, required): Path to file.

**Returns:** Dictionary with file metadata (size, extension, etc.).

---

## Usage Example

```python
from src.tools.mcp_registry import get_registry
from src.tools.initialize_tools import ensure_tools_initialized

# Initialize tools
ensure_tools_initialized()
registry = get_registry()

# List all tools
all_tools = registry.list_tools()
print(f"Total tools: {len(all_tools)}")

# List tools by category
data_tools = registry.list_tools(category="data")
print(f"Data tools: {len(data_tools)}")

# Execute a tool
result = registry.execute("detect_missing_values", {
    "column": "age"
})
print(result)

# Get tool specification
spec = registry.get_tool_spec("impute_median")
print(spec)
```

---

## MCP Format

All tools follow MCP specification with:
- **name**: Unique tool identifier
- **description**: Human-readable description
- **inputSchema**: JSON Schema defining parameters
- **handler**: Python function that executes the tool
- **version**: Tool version
- **category**: Tool category (data, validation, file)

---

## Tool Discovery

Tools can be discovered programmatically:
```python
# Get all tools
tools = registry.list_tools()

# Get tools by category
data_tools = registry.list_tools(category="data")

# Export as JSON
tools_json = registry.export_tools_json()
```

---

## Integration with Agents

Agents can use tools through the registry:
```python
# In an agent
tool_registry = get_registry()
result = tool_registry.execute("impute_median", {"column": "age"})
```

This allows agents to perform operations without duplicating code.

