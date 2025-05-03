#!/bin/bash

# Check if venv exists, if not create it.
if [ ! -d "application-env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv application-env
fi

# Activate the venv.
source application-env/bin/activate

# Install dependencies if needed
pip install -r requirements.txt

# Run the Flask app
python3 run.py
