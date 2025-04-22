# Video2Text API

Una API RESTful para la transcripción de videos largos (hasta 5 horas) desde URLs de S3, utilizando OpenAI Whisper y procesamiento asincrónico con Redis + RQ.

---

## Características

- Procesamiento asincrónico de videos mediante Redis y RQ.
- Extracción de audio con `ffmpeg` y `moviepy`.
- Transcripción de voz a texto usando el modelo Whisper de OpenAI.
- Soporte para videos grandes (>3 horas).
- Manejo automático de fragmentación de video por partes (chunks).
- Limpieza automática de archivos temporales.

---

## Requisitos

- Docker
- Docker Compose

---

## Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/tu_usuario/video_transcribe.git
cd video_transcribe
```

2. Construye e inicia los servicios (API, Redis, Worker):

```bash
docker-compose up --build
```

Esto levantará:

- `api` en `http://localhost:8000`
- `redis` en el puerto `6379`
- `worker` para tareas de fondo

---

## Endpoints

### `POST /video2text`

Inicia el procesamiento asincrónico de un video.

**Request:**

```json
{
  "url": "https://ruta-completa-al-video-en-s3"
}
```

**Response:**

```json
{
  "message": "Video processing started",
  "task_id": "f3ab12c7d3e24c2e"
}
```

---

### `GET /status/<task_id>`

Consulta el estado del procesamiento.

**Response (en progreso):**

```json
{
  "status": "started"
}
```

**Response (completo):**

```json
{
  "status": "finished",
  "result": [
    {
      "start": 0.0,
      "end": 5.2,
      "text": "Hola, bienvenidos a la transcripción."
    },
    ...
  ]
}
```

**Response (error):**

```json
{
  "status": "failed",
  "error": "Detalles del error"
}
```

---

## Notas técnicas

- Archivos descargados desde S3 se almacenan temporalmente como `video_<uuid>.mp4` y se eliminan después del procesamiento.
- Cada video se divide en fragmentos de 27 minutos (1620s) para facilitar el manejo en memoria.
- RQ maneja múltiples trabajos concurrentes desde `worker.py`.

---
