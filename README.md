# 🏥 DatasetDoctor - Your Data Quality Assistant

## What is DatasetDoctor?

**DatasetDoctor is an AI-powered multi-agent system that automatically diagnoses and fixes data quality issues in your datasets.**

Just like a doctor:
- **Examines** your dataset (like a checkup)
- **Diagnoses** problems (finds what's wrong)
- **Fixes** issues (applies treatments)
- **Validates** the fix worked (follow-up check)
- **Writes a report** (medical summary)

## 🚀 One-Command Run (For Judges)

**Simply run:**
```bash
./run.sh # For Unix/Linux/macOS
# or
./run.bat #for Windows CMD/PowerShell
```

This single command will:
1. ✅ Check Python installation
2. ✅ Create virtual environment
3. ✅ Install all dependencies
4. ✅ Set up directories
5. ✅ Start the web UI

**Then open:** `http://localhost:5000` in your browser

---

## 🎯 What Does It Do?

1. **You upload a messy dataset** (CSV or JSON file)
2. **DatasetDoctor scans it** and finds problems like:
   - Missing values (empty cells)
   - Wrong data types (text in number columns)
   - Duplicates (same row appearing twice)
   - Outliers (weird values that don't make sense)
3. **DatasetDoctor fixes them automatically**
4. **You get back:**
   - Clean dataset
   - Detailed HTML report
   - JSON report
   - Python script to reproduce the cleaning

## 📋 Features

### Multi-Agent System
- **IngestorAgent**: Loads and validates datasets
- **ScannerAgent**: Detects data quality issues
- **FixerAgent**: Automatically fixes issues
- **ValidatorAgent**: Validates fixes worked
- **ReporterAgent**: Generates comprehensive reports

### AI-Powered Insights
- **Gemini Integration**: Provides intelligent analysis and suggestions
- **Pattern Recognition**: Identifies data quality patterns
- **Context-Aware Fixes**: Understands data semantics

### MCP Tools (14 Tools)
- **Data Tools**: 7 tools for data manipulation
- **Validation Tools**: 2 tools for quality checks
- **File Tools**: 5 tools for file operations

### Observability
- Structured logging
- Distributed tracing
- Performance metrics
- Session management

### Memory & Context
- Session management
- Memory bank for learned patterns
- Context engineering for large datasets

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Setup

**Option 1: One-Command Run (Recommended)**
```bash
./run.sh
```

**Option 2: Manual Setup**
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional - for Gemini AI features)
echo "GOOGLE_API_KEY=your_key_here" > .env

# Start the application
python3 ui/app.py
```

### Environment Variables (Optional)

Create a `.env` file:
```bash
GOOGLE_API_KEY=your_google_api_key_here
PROJECT_ID=your_gcp_project_id  # For Vertex AI
REGION=us-central1
PORT=5000
FLASK_DEBUG=False
```

**Note:** The application works without `GOOGLE_API_KEY`, but AI features will be disabled.

## 📖 Usage

### Web UI (Recommended)

1. Run `./run.sh`
2. Open `http://localhost:5000`
3. Upload a CSV or JSON file
4. Wait for processing
5. Download cleaned dataset and reports

### Command Line

```bash
# Process a dataset file
python3 src/main.py path/to/dataset.csv

# Or use bootstrap script
./bootstrap_and_run.sh path/to/dataset.csv
```

## 📁 Project Structure

```
DatasetDoctor/
├── run.sh                 # One-command run script
├── bootstrap_and_run.sh   # CLI bootstrap script
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── src/                   # Source code
│   ├── agents/           # Multi-agent system
│   ├── core/              # Core utilities
│   ├── llm/              # Gemini integration
│   ├── tools/            # MCP tools
│   ├── memory/           # Memory management
│   ├── observability/    # Logging, tracing, metrics
│   └── evaluation/       # Evaluation framework
├── ui/                    # Web UI
│   ├── app.py            # Flask application
│   ├── templates/        # HTML templates
│   └── static/           # CSS, JS, assets
├── examples/              # Sample datasets
├── evaluation/            # Evaluation framework
└── deployment/           # Cloud deployment configs
```

## 🧪 Testing

```bash
# Run system tests
python3 test_system.py

# Run evaluation framework
python3 evaluation/run_evaluation.py
```

## 🚀 Deployment

### Local Docker
```bash
cd deployment/local
docker-compose up --build
```

### Google Cloud Run
```bash
./deployment/cloud-run/deploy.sh
```

See `deployment/cloud-run/README.md` for details.

## 🎓 Competition Alignment

This project demonstrates:

✅ **Multi-agent system** - 5 specialized agents working together  
✅ **MCP Tools** - 14 standardized tools following MCP specification  
✅ **Sessions & Memory** - Session service and memory bank  
✅ **Context Engineering** - Dataset summarization and compaction  
✅ **Observability** - Logging, tracing, and metrics  
✅ **Agent Evaluation** - Gold datasets and automated metrics  
✅ **A2A Protocol** - Agent-to-agent communication  
✅ **Cloud Deployment** - Docker + Cloud Run setup  

## 📚 Documentation

- **Architecture**: `docs/ARCHITECTURE.md` - System design and architecture
- **API Documentation**: `docs/API.md` - Complete API reference
- **Tools Specification**: `docs/TOOLS_SPECIFICATION.md` - MCP tools documentation
- **Submission Guide**: `docs/SUBMISSION_GUIDE.md` - Guide for judges
- **Deployment Guide**: `deployment/cloud-run/README.md` - Cloud deployment

## 🤝 Contributing

This is a capstone project submission. For questions or issues, please refer to the project documentation.

## 📄 License

This project is licensed under the MIT License — see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini API for AI-powered insights
- Flask for web framework
- Pandas for data manipulation

---

**Made with ❤️ for data quality**
