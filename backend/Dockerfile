FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
# La carpeta de estudios se crea con dueño appuser para que el volumen de docker-compose herede ese permiso.
RUN useradd -m appuser && mkdir -p /app/estudios && chown appuser:appuser /app/estudios
USER appuser
EXPOSE 8000
# Aplica los scripts nuevos de db/ (montada en docker-compose) y arranca la API.
CMD ["sh", "-c", "python -m app.preparar && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
