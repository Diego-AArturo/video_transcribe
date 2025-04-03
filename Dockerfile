# Usa una imagen oficial de Python como base
FROM python:3.10

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . .

# Instala dependencias desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que correrá la API
EXPOSE 8000

# Comando para ejecutar la API
CMD ["gunicorn", "--workers", "2", "--threads", "2", "--worker-class", "gthread", "--bind", "0.0.0.0:8000", "app:app", "--timeout", "300"]
