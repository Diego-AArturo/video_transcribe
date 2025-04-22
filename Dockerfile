FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala Git y limpia la caché de apt
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos del proyecto al contenedor
COPY . .

RUN pip install --no-cache-dir torch==2.1.2+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Instala dependencias desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que correrá la API
EXPOSE 8000

# Comando para ejecutar la API
CMD ["gunicorn", "--workers", "2", "--threads", "2", "--worker-class", "gthread", "--bind", "0.0.0.0:8000", "app:app", "--timeout", "6000"] 
