#!/bin/bash
# DatasetDoctor - One-Command Run Script
# Judges can run this single command to start the application

set -e  # Exit on error

echo "🏥 DatasetDoctor - Starting..."
echo "================================"
echo ""

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
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create directories
mkdir -p uploads outputs logs traces
touch uploads/.gitkeep outputs/.gitkeep

# Create .env if doesn't exist
if [ ! -f ".env" ]; then
    echo "GOOGLE_API_KEY=" > .env
    echo "⚠️  Note: GOOGLE_API_KEY not set. AI features will be disabled."
fi

# Start the web UI
echo ""
echo "🚀 Starting DatasetDoctor Web UI..."
echo "   Open: http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo ""

python3 ui/app.py

