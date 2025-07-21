#!/bin/bash
# Quick start script for Desktop Commander UI

echo "🚀 Starting Desktop Commander UI..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt --quiet

# Check if Ollama is running
echo ""
echo "🔍 Checking services..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running. Starting Ollama in background..."
    echo "   (You may need to run 'ollama serve' manually in another terminal)"
fi

# Run the setup test
echo ""
python test_setup.py

# If tests pass, start the app
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Starting Desktop Commander UI..."
    echo "   Open your browser to: http://127.0.0.1:7860"
    echo "   Press Ctrl+C to stop"
    echo ""
    python app.py
else
    echo ""
    echo "❌ Please fix the issues above before running the app."
    echo "   You can manually start with: python app.py"
fi