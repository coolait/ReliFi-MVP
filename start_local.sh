#!/bin/bash
# Quick start script for local development
# This script starts both the Python API server and React frontend

echo "🚀 Starting ReliFi MVP locally..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Function to start Python API server
start_api_server() {
    echo -e "${BLUE}📦 Starting Python API server...${NC}"
    cd scrapper
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies if needed
    if [ ! -f "venv/.installed" ]; then
        echo -e "${YELLOW}📥 Installing Python dependencies...${NC}"
        pip install -r requirements.txt
        touch venv/.installed
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  .env file not found. Creating from env.example...${NC}"
        if [ -f "env.example" ]; then
            cp env.example .env
            echo -e "${YELLOW}⚠️  Please edit scrapper/.env and add your API keys!${NC}"
        fi
    fi
    
    echo -e "${GREEN}✅ Starting API server on http://localhost:5001${NC}"
    python3 api_server.py
}

# Function to start React frontend
start_frontend() {
    echo -e "${BLUE}⚛️  Starting React frontend...${NC}"
    cd client
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📥 Installing Node.js dependencies...${NC}"
        npm install
    fi
    
    echo -e "${GREEN}✅ Starting frontend on http://localhost:3000${NC}"
    npm start
}

# Check if user wants to run both or just one
if [ "$1" == "api" ]; then
    start_api_server
elif [ "$1" == "frontend" ]; then
    start_frontend
else
    # Run both in separate terminals (macOS/Linux)
    if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo -e "${BLUE}Starting both servers in separate terminals...${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  You'll need two terminal windows:${NC}"
        echo -e "  1. API Server: http://localhost:5001"
        echo -e "  2. Frontend: http://localhost:3000"
        echo ""
        
        # Try to open new terminal windows (macOS)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            osascript -e 'tell application "Terminal" to do script "cd '"$(pwd)"'/scrapper && source venv/bin/activate && python3 api_server.py"' &
            sleep 2
            osascript -e 'tell application "Terminal" to do script "cd '"$(pwd)"'/client && npm start"' &
        else
            # Linux - use gnome-terminal or xterm
            if command -v gnome-terminal &> /dev/null; then
                gnome-terminal -- bash -c "cd $(pwd)/scrapper && source venv/bin/activate && python3 api_server.py; exec bash" &
                sleep 2
                gnome-terminal -- bash -c "cd $(pwd)/client && npm start; exec bash" &
            else
                echo -e "${YELLOW}⚠️  Please run in two separate terminals:${NC}"
                echo -e "  Terminal 1: ./start_local.sh api"
                echo -e "  Terminal 2: ./start_local.sh frontend"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Please run in two separate terminals:${NC}"
        echo -e "  Terminal 1: ./start_local.sh api"
        echo -e "  Terminal 2: ./start_local.sh frontend"
    fi
fi

