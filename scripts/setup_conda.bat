@echo off
REM AlphaLoop Core - Conda Environment Setup Script (Windows)
REM This script creates a conda environment and installs the project

echo 🚀 Setting up AlphaLoop Core conda environment...

REM Check if conda is available
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Conda is not installed or not in PATH
    echo Please install conda first: https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

REM Check if environment already exists
conda env list | findstr "alphaloop-core" >nul
if %errorlevel% equ 0 (
    echo ⚠️  Environment 'alphaloop-core' already exists
    set /p choice="Do you want to remove it and recreate? (y/N): "
    if /i "%choice%"=="y" (
        echo 🗑️  Removing existing environment...
        conda env remove -n alphaloop-core
    ) else (
        echo ✅ Using existing environment
    )
)

REM Create environment from yml file
echo 📦 Creating conda environment from environment.yml...
conda env create -f environment.yml

REM Activate environment
echo 🔧 Activating environment...
call conda activate alphaloop-core

REM Install the project in development mode
echo 📥 Installing project in development mode...
poetry install

REM Install pre-commit hooks
echo 🔗 Installing pre-commit hooks...
pre-commit install

echo ✅ Setup complete!
echo.
echo To activate the environment:
echo   conda activate alphaloop-core
echo.
echo To run tests:
echo   make test
echo.
echo To start the API:
echo   make run-api
echo.
echo To run linting:
echo   make lint
echo.
pause
