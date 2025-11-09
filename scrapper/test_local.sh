#!/bin/bash
# Helper script to test APIs locally with virtual environment

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run the test script
python3 test_apis_local.py

