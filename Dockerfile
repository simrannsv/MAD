FROM python:3.11-slim

WORKDIR /app

# Install Ollama
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://ollama.com/install.sh | sh

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Start Ollama in background and run app
CMD ollama serve & sleep 5 && ollama pull llama3.2 && python app.py

