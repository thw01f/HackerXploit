FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (libmagic, libpq, clamav client library)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libmagic1 \
    clamav \
    clamav-daemon \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--worker-class", "gevent", "-w", "2", "-b", "0.0.0.0:5000", "run:app"]
