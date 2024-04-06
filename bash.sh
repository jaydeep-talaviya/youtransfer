#!/bin/bash

# Check Python version and install virtualenv if not installed
if [[ $(python3 --version 2>&1) =~ "Python 3" ]]; then
    echo "Python 3 detected"
    if ! command -v virtualenv &> /dev/null; then
        echo "Installing virtualenv..."
        pip install virtualenv
    fi
else
    echo "Python 3 is required"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    virtualenv venv
fi

# Activate virtual environment based on OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    source venv/bin/activate
elif [[ "$OSTYPE" == "darwin"* ]]; then
    source venv/bin/activate
elif [[ "$OSTYPE" == "msys" ]]; then
    source venv/Scripts/activate
else
    echo "Unsupported OS"
    exit 1
fi

# Install dependencies from requirements.txt
echo "Installing dependencies..."
pip install -r requirements.txt

# Start Django server
echo "Starting Django server..."
python manage.py runserver &

# Start Celery command (replace with your actual Celery command)
echo "Starting Celery..."
celery -A youtransfer worker -l info
