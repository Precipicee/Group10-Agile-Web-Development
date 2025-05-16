#!/bin/bash

# Check if venv exists, if not create it.
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the venv.
source venv/bin/activate

# Install dependencies if not installed
pip install -r requirements.txt

# Run the Flask app
python3 app.py
