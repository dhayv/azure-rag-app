#!/bin/bash

# Activate virtual environment and run the FastAPI app
echo "🚀 Starting RAG AI App..."

# Activate virtual environment
source .venv/bin/activate

# Run the FastAPI app with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000 