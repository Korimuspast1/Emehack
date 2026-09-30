FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpng-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --no-cache-dir \
    python-telegram-bot \
    fastapi \
    uvicorn \
    aiohttp \
    requests \
    pillow \
    jinja2 \
    pydantic

ENV BOT_TOKEN="7389083158:AAEz8Dqw0WPn6RBu4rzGDXWtBaU_pVEKLmM"
ENV WEB_HOST="0.0.0.0"
ENV WEB_PORT="8080"
ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["python3", "run.py"]
