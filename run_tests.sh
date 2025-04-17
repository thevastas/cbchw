#!/bin/bash
# Run all tests for the Event Communication System

# Install the package in development mode
echo "Installing package in development mode..."
pip install -e .

# Make sure pytest and coverage tools are installed
echo "Ensuring test dependencies are installed..."
pip install pytest pytest-asyncio pytest-cov

# Run all tests with coverage report
echo "Running tests with coverage..."
python -m pytest -v

echo "All tests completed."
