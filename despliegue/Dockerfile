# Imagen única para el enlace público: compila el frontend y lo sirve desde la API (mismo origen, sin CORS).
# Se construye desde la raíz del repositorio: docker build -f despliegue/Dockerfile .
FROM node:20-alpine AS web
WORKDIR /web
ENV VITE_API_URL=/api/v1
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 ESQUEMA_DIR=/app/db WEB_DIR=/app/web PORT=8000
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY db ./db
COPY --from=web /web/dist ./web
RUN useradd -m appuser && mkdir -p media estudios && chown appuser media estudios
USER appuser
EXPOSE 8000
# Prepara la base (esquema, administrador inicial y caso de demostración) y arranca la API.
CMD ["sh", "-c", "python -m app.preparar && uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
