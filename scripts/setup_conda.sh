#!/bin/bash

# AlphaLoop Core - Conda Environment Setup Script
# This script creates a conda environment and installs the project

set -e  # Exit on any error

echo "🚀 Setting up AlphaLoop Core conda environment..."

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed or not in PATH"
    echo "Please install conda first: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Check if environment already exists
if conda env list | grep -q "alphaloop-core"; then
    echo "⚠️  Environment 'alphaloop-core' already exists"
    read -p "Do you want to remove it and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing environment..."
        conda env remove -n alphaloop-core
    else
        echo "✅ Using existing environment"
    fi
fi

# Create environment from yml file
echo "📦 Creating conda environment from environment.yml..."
conda env create -f environment.yml

# Activate environment
echo "🔧 Activating environment..."
eval "$(conda shell.bash hook)"
conda activate alphaloop-core

# Install the project in development mode
echo "📥 Installing project in development mode..."
poetry install

# Install pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
pre-commit install

echo "✅ Setup complete!"
echo ""
echo "To activate the environment:"
echo "  conda activate alphaloop-core"
echo ""
echo "To run tests:"
echo "  make test"
echo ""
echo "To start the API:"
echo "  make run-api"
echo ""
echo "To run linting:"
echo "  make lint"
