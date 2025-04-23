FROM python:3.10
WORKDIR /code

# Install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache --upgrade -r /code/requirements.txt

# Copy application code
COPY ./backend /code/backend

ENV PYTHONPATH=/code

# Expose API port
EXPOSE 8001

# Use env var for port when run via docker compose
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${API_PORT:-8001} --reload"]