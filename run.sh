#!/bin/bash

# Quant App Startup Script
# This script sets up and runs the quantitative trading dashboard

echo "=========================================="
echo "  Quant Trading Analytics Dashboard"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1)
echo "Found: $python_version"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || . venv/bin/activate
echo ""

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "Dependencies installed."
echo ""

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    echo "Creating data directory..."
    mkdir -p data
    echo "Data directory created."
    echo ""
fi

# Display instructions
echo "=========================================="
echo "  Starting Dashboard..."
echo "=========================================="
echo ""
echo "The dashboard will open in your browser at:"
echo "  http://localhost:8501"
echo ""
echo "To use the dashboard:"
echo "  1. Select 'Live Stream' or 'Upload OHLC'"
echo "  2. Configure symbols (e.g., btcusdt,ethusdt)"
echo "  3. Adjust analytics parameters"
echo "  4. View real-time charts and analytics"
echo ""
echo "To stop the server, press Ctrl+C"
echo ""
echo "=========================================="
echo ""

# Run Streamlit
streamlit run app.py
