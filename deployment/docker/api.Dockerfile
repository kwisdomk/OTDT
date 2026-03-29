FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Environment variables for demo mode
ENV MAXIMO_MOCK_MODE=true
ENV SYSTEM_ACTIVE=true
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Made with Bob
