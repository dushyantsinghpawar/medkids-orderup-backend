FROM python:3.12-slim

WORKDIR /app

# Needed for psycopg2 / Postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh || true

EXPOSE 8000
CMD ["bash", "start.sh"]
