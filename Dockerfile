FROM python:3.12-slim

ENV RUNNING_IN_DOCKER=1

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y --no-install-recommends fontconfig wget curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=5000

EXPOSE 5000

CMD ["python", "app.py"]
