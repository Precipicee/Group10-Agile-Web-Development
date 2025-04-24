#!/bin/bash

# Check if venv exists, if not create it.
if [ ! -d "application-env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv application-env
fi

# Activate the venv.
source application-env/bin/activate

# Run the application.
python3 weather.py