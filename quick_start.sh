#!/bin/bash
# Quick Start Script for Carpool RideShare App

echo "🚗 RideShare - Carpool Pricing Application"
echo "==========================================="
echo ""

# Check Python installation
echo "✓ Checking Python installation..."
python --version

# Create virtual environment (optional but recommended)
echo ""
echo "✓ Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
echo "✓ Installing dependencies..."
pip install -r requirements.txt

# Run the app
echo ""
echo "✓ Launching Streamlit app..."
echo ""
echo "📱 App running at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the app"
echo ""

streamlit run carpool_streamlit_app.py
