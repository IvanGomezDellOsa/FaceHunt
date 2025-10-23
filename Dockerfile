FROM python:3.10-slim

LABEL maintainer="IvanGomezDellOsa <ivangomezdellosa@gmail.com>"
ENV CUDA_VISIBLE_DEVICES="-1"
ENV TF_CPP_MIN_LOG_LEVEL="2"
ENV TF_ENABLE_ONEDNN_OPTS="0"

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --upgrade yt-dlp

COPY . .

RUN mkdir -p videos

EXPOSE 7860

CMD ["python", "api_server.py"]