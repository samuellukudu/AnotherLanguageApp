# Development stage
FROM python:3.10-slim AS development

WORKDIR /code

# Install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache --upgrade -r /code/requirements.txt

# Copy application code and .env file
COPY ./backend /code/backend
COPY .env /code/.env

ENV PYTHONPATH=/code

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/ || exit 1

# Development command with hot reload
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

# Production stage
FROM python:3.10-slim AS production

WORKDIR /code

# Install production dependencies only
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache --upgrade -r /code/requirements.txt

# Copy application code
COPY ./backend /code/backend

ENV PYTHONPATH=/code
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/ || exit 1

# Production command without reload for better performance
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001"]