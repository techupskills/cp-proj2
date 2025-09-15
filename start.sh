#!/bin/bash

# Start Ollama in background
ollama serve &

# Wait for Ollama to start
sleep 10

# Pull the model
ollama pull llama3.2

# Start Streamlit app
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
