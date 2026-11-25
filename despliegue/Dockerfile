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
# Modelo de visión experimental y su imagen de ejemplo, publicados por el flujo «Entrenar modelo de visión» (IE-04).
# ADD descarga de nuevo en cada construcción, así Render toma la versión más reciente del release.
ADD https://github.com/rivasnico356-png/colorrectal-sim/releases/download/modelo-vision/vision.onnx modelos/vision.onnx
ADD https://github.com/rivasnico356-png/colorrectal-sim/releases/download/modelo-vision/vision.json modelos/vision.json
ADD https://github.com/rivasnico356-png/colorrectal-sim/releases/download/modelo-vision/ejemplo-kvasir.jpg modelos/ejemplo-kvasir.jpg
RUN useradd -m appuser && mkdir -p media estudios && chown appuser media estudios && chmod -R a+rX modelos
USER appuser
EXPOSE 8000
# Prepara la base (esquema, administrador inicial y caso de demostración) y arranca la API.
CMD ["sh", "-c", "python -m app.preparar && uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
