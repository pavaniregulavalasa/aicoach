#!/bin/bash
# Backend startup script

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Please create one first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    echo "# LLM Configuration" > .env
    echo "LLM_MODE=local" >> .env
    echo "LLM_MODEL=qwen2.5:7b" >> .env
    echo "# For remote: LLM_MODE=remote, LLM_API_KEY=your-key, LLM_BASE_URL=your-url" >> .env
    echo "✅ Created .env file with defaults. Edit it if needed."
fi

echo "🚀 Starting Backend Server..."
echo "📍 Backend will be available at: http://127.0.0.1:8000"
echo "📚 API docs at: http://127.0.0.1:8000/docs"
echo ""

uvicorn services.main:app --host 127.0.0.1 --port 8000

