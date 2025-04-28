# worker.py
import os
import redis
from rq import Worker, Queue, Connection

# Nombre de las colas que quieres escuchar
listen = ['default']

# Dirección de conexión a Redis
redis_url = os.getenv('REDIS_URL', 'redis://redis:6379')

# Crear conexión
conn = redis.from_url(redis_url)

def start_worker():
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work(
            burst=False,         # Escuchar continuamente
            with_scheduler=False # No usar programación de trabajos, solo ejecución directa
        )

if __name__ == '__main__':
    start_worker()

