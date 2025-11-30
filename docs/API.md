# DatasetDoctor API Documentation

## Web UI API Endpoints

### Base URL
```
http://localhost:5000
```

---

## Endpoints

### 1. Home Page
**GET** `/`

Returns the main web UI interface.

**Response:**
- HTML page with upload form

---

### 2. Upload and Process Dataset
**POST** `/upload`

Uploads a dataset file and processes it through the DatasetDoctor pipeline.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  ```
  file: <CSV or JSON file>
  ```

**Response (Success):**
```json
{
  "success": true,
  "dataset_name": "sample.csv",
  "shape": [100, 5],
  "columns": ["name", "age", "email", "price", "category"],
  "quality_score": 85.5,
  "total_issues": 12,
  "total_fixes": 10,
  "issues": [
    {
      "type": "missing_values",
      "description": "Found 5 missing values (5.0%) in column 'age'",
      "column": "age",
      "severity": "medium",
      "gemini_insight": "Age column should contain numeric values..."
    }
  ],
  "fixes": [
    {
      "method": "median_imputation",
      "description": "Filled 5 missing values in 'age' with median (32.5)",
      "column": "age",
      "success": true
    }
  ],
  "report_files": {
    "json_report": "sample_report_20251130_123456.json",
    "python_script": "sample_cleaning_20251130_123456.py",
    "cleaned_dataset": "sample_cleaned_20251130_123456.csv",
    "html_report": "sample_report_20251130_123456.html"
  },
  "validation": {
    "before_quality_score": 65.0,
    "after_quality_score": 85.5,
    "improvement": 20.5
  },
  "is_cleaned_file": false,
  "cleaned_file_note": ""
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Invalid file type: .txt",
  "allowed": ["csv", "json"]
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad request (invalid file, missing file, etc.)
- `500`: Server error

---

### 3. Download Cleaned Dataset
**GET** `/download/<filename>`

Downloads a generated file (cleaned dataset, Python script, or JSON report).

**Parameters:**
- `filename` (path): Name of the file to download

**Response:**
- File download (attachment)

**Status Codes:**
- `200`: Success
- `404`: File not found

**Example:**
```
GET /download/sample_cleaned_20251130_123456.csv
```

---

### 4. View HTML Report
**GET** `/report/<filename>`

Views an HTML report in the browser.

**Parameters:**
- `filename` (path): Name of the HTML report file

**Response:**
- HTML page

**Status Codes:**
- `200`: Success
- `404`: Report not found

**Example:**
```
GET /report/sample_report_20251130_123456.html
```

---

### 5. Health Check
**GET** `/health`

Health check endpoint for monitoring and deployment.

**Response:**
```json
{
  "status": "healthy",
  "service": "DatasetDoctor",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200`: Service is healthy

---

## Data Models

### Issue Object
```json
{
  "type": "missing_values | type_inconsistency | duplicates | outliers",
  "description": "Human-readable description",
  "column": "column_name",
  "severity": "critical | high | medium | low",
  "gemini_insight": "AI-generated insight (optional)"
}
```

### Fix Object
```json
{
  "method": "median_imputation | mode_imputation | type_conversion | ...",
  "description": "Description of the fix applied",
  "column": "column_name",
  "success": true
}
```

### Report Files Object
```json
{
  "json_report": "filename.json",
  "python_script": "filename.py",
  "cleaned_dataset": "filename.csv",
  "html_report": "filename.html"
}
```

---

## Error Responses

### Standard Error Format
```json
{
  "error": "Error message",
  "details": "Additional details (optional)"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource not found |
| 413 | Payload Too Large - File exceeds size limit |
| 500 | Internal Server Error - Server error |

---

## File Size Limits

- **Maximum upload size**: 50 MB (configurable)
- **Allowed extensions**: `.csv`, `.json`

---

## Rate Limiting

Currently no rate limiting is implemented. For production deployment, consider adding rate limiting.

---

## Authentication

Currently no authentication is required. For production, consider adding authentication.

---

## Example Usage

### cURL Examples

**Upload a dataset:**
```bash
curl -X POST \
  -F "file=@sample.csv" \
  http://localhost:5000/upload
```

**Download cleaned dataset:**
```bash
curl -O http://localhost:5000/download/sample_cleaned_20251130_123456.csv
```

**Health check:**
```bash
curl http://localhost:5000/health
```

### JavaScript (Fetch API)

```javascript
// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/upload', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Success:', data);
})
.catch(error => {
  console.error('Error:', error);
});
```

### Python (Requests)

```python
import requests

# Upload file
with open('sample.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/upload', files=files)
    result = response.json()
    print(result)

# Download cleaned dataset
filename = result['report_files']['cleaned_dataset']
response = requests.get(f'http://localhost:5000/download/{filename}')
with open('cleaned.csv', 'wb') as f:
    f.write(response.content)
```

---

## WebSocket (Future Enhancement)

WebSocket support for real-time progress updates is planned for future versions.

---

## Versioning

Current API version: `1.0.0`

API versioning will be implemented in future releases if breaking changes are needed.

