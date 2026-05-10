# Aarogya - HuggingFace Space (Docker SDK)
# Slim image: only ffmpeg for audio (no build tools - prebuilt wheels handle the rest)
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860 \
    HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
WORKDIR /home/user/app

COPY --chown=user requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY --chown=user . .

EXPOSE 7860
CMD ["python", "app.py"]
