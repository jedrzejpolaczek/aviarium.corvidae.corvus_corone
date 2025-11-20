FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 CMD curl -f http://localhost:8005/health || exit 1

EXPOSE 8005
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]