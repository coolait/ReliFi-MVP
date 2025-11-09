#!/bin/bash
# Quick test script to verify local setup

echo "🧪 Testing Local Setup..."
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 installed: $(python3 --version)"
else
    echo "❌ Python 3 not found"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js installed: $(node --version)"
else
    echo "❌ Node.js not found"
    exit 1
fi

# Check if virtual environment exists
if [ -d "scrapper/venv" ]; then
    echo "✅ Python virtual environment exists"
else
    echo "⚠️  Python virtual environment not found (run: cd scrapper && python3 -m venv venv)"
fi

# Check if node_modules exists
if [ -d "client/node_modules" ]; then
    echo "✅ Node.js dependencies installed"
else
    echo "⚠️  Node.js dependencies not installed (run: cd client && npm install)"
fi

# Check if .env file exists
if [ -f "scrapper/.env" ]; then
    echo "✅ .env file exists"
else
    echo "⚠️  .env file not found (copy scrapper/env.example to scrapper/.env)"
fi

echo ""
echo "✅ Setup check complete!"
echo ""
echo "To start the application:"
echo "  1. Terminal 1: cd scrapper && source venv/bin/activate && python3 api_server.py"
echo "  2. Terminal 2: cd client && npm start"
