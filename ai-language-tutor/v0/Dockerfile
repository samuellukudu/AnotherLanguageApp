FROM python:3.11.7-slim-bullseye

# Create a non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ backend/

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the API server
CMD ["uvicorn", "backend.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
