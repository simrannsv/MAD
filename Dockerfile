# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port 8005
EXPOSE 8005

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "llm_server.py"]

