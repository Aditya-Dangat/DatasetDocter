#!/bin/bash
# DatasetDoctor - Bootstrap and Run Script (CLI mode)
# For command-line usage with dataset files

set -e

echo "🏥 DatasetDoctor - CLI Mode"
echo "==========================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required"
    exit 1
fi

# Create venv if doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install dependencies
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create directories
mkdir -p uploads outputs logs traces

# Create .env if doesn't exist
if [ ! -f ".env" ]; then
    echo "GOOGLE_API_KEY=" > .env
fi

# Run CLI
if [ -z "$1" ]; then
    python3 src/main.py --help
else
    python3 src/main.py "$1"
fi

