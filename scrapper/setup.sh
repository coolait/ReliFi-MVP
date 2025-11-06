#!/bin/bash
# Quick setup script for Rideshare Data Scraper

echo "=================================="
echo "Rideshare Data Scraper Setup"
echo "=================================="

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env file with your database credentials!"
fi

# Create necessary directories
mkdir -p logs
mkdir -p data

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your database credentials"
echo "2. Create PostgreSQL database: createdb rideshare_data"
echo "3. Initialize database: python3 -c 'from database.models import init_database; init_database()'"
echo "4. Run scraper: python3 main.py"
echo ""
echo "For more information, see README.md"
