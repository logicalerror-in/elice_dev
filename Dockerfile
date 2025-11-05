FROM python:3.11-slim
WORKDIR /app
COPY requirements* /app/
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
