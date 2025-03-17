FROM python:3.9
WORKDIR /code

# Install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache --upgrade -r /code/requirements.txt

# Copy application code and .env file
COPY ./backend /code/backend
COPY .env /code/.env

ENV PYTHONPATH=/code
ENV PORT=8004

CMD ["sh", "-c", "uvicorn backend.api.app:app --host 0.0.0.0 --port ${PORT}"]