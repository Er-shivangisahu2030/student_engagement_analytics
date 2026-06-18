#!/bin/bash

# Student Engagement Analytics - Quick Start Script
# This script sets up and runs the entire pipeline

set -e

echo "======================================================================"
echo "  📊 Student Engagement & Learning Streak Analytics Platform"
echo "======================================================================"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $python_version found"

# Create virtual environment
echo ""
echo "📦 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Check .env file
echo ""
echo "🔐 Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✓ .env created. Please edit with your database credentials:"
    echo "  nano .env"
    echo ""
    read -p "  Continue after configuring? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ .env file found"
fi

# Run the ETL pipeline
echo ""
echo "🚀 Starting ETL Pipeline..."
echo "======================================================================"

cd src
python -m pipeline.main_pipeline

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo "✅ ETL Pipeline completed successfully!"
    echo "======================================================================"
    echo ""
    echo "📊 Starting Streamlit Dashboard..."
    echo "Dashboard will open at: http://localhost:8501"
    echo ""
    cd ..
    streamlit run dashboard/streamlit_app.py
else
    echo ""
    echo "======================================================================"
    echo "❌ ETL Pipeline failed. Check logs for details."
    echo "Log file: data/logs/pipeline.log"
    echo "======================================================================"
    exit 1
fi
