#!/bin/bash

# AI Tax Buddy - Quick Setup Script
# This script automates the setup process

set -e  # Exit on error

echo "🇦🇺 AI Tax Buddy - Quick Setup"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.10 or higher is required"
    echo "   Current version: $python_version"
    exit 1
fi
echo "✅ Python $python_version detected"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"
echo ""


# Setup environment file
echo "Setting up environment configuration..."
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Skipping."
else
    cp .env.example .env
    echo "✅ .env file created from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API key!"
    echo "   Required: OPENAI_API_KEY or ANTHROPIC_API_KEY"
fi
echo ""

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p chroma_db
mkdir -p logs
echo "✅ Directories created"
echo ""

# Run configuration check
echo "Checking configuration..."
python main.py info 2>/dev/null || echo "⚠️  Please configure your .env file before running"
echo ""

echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API key:"
echo "   nano .env"
echo ""
echo "2. Start chatting:"
echo "   python main.py chat"
echo ""
echo "3. Or try a single query:"
echo "   python main.py query \"Can I claim my home office expenses?\""
echo ""
echo "For help, see:"
echo "  - QUICKSTART.md"
echo "  - README.md"
echo "  - SETUP.md"
echo ""
