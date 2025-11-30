#!/bin/bash
# Simple script to run the Take-Home Test Generator API

echo "🚀 Starting Take-Home Test Generator API..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one from .env.example"
    echo "   cp .env.example .env"
    echo "   Then edit .env and add your GEMINI_API_KEY"
    exit 1
fi

# Check if GEMINI_API_KEY is set
if ! grep -q "GEMINI_API_KEY=.\+" .env; then
    echo "⚠️  GEMINI_API_KEY not set in .env file"
    echo "   Please edit .env and add your API key"
    exit 1
fi

echo "✅ Environment configured"
echo ""
echo "Starting FastAPI server..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🔍 Alternative docs: http://localhost:8000/redoc"
echo ""

# Run the server
python -m backend.main
