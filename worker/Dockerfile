FROM python:3.13-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir psycopg2-binary pika

COPY engine/ ./engine/
COPY worker/ ./worker/

WORKDIR /app/worker

CMD ["python", "worker.py"]
