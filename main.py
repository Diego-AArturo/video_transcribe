from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
from rq import Queue
import logging
import json
import uuid
import asyncio
from video import process_video

app = FastAPI()

# Configurar Redis y RQ
redis_conn = redis.Redis(host="redis", port=6379)
task_queue = Queue(connection=redis_conn)

class VideoRequest(BaseModel):
    url: str

@app.post("/video2text")
async def enviar_url(request: VideoRequest):
    url = request.url
    if not url:
        raise HTTPException(status_code=400, detail="No URL found in the request")
    
    try:
        task_id = uuid.uuid4().hex
        job = task_queue.enqueue(process_video, url, job_id=task_id, job_timeout=6000)

        timeout_seconds = 6000  # 1 hora máximo
        poll_interval = 5       # esperar 5 segundos entre chequeos

        elapsed = 0
        while elapsed < timeout_seconds:
            job.refresh()
            try:
                json.dumps(job.result)
            except Exception as e:
                logging.error(f"El resultado del job no es JSON serializable: {e}")
                raise HTTPException(status_code=500, detail="Job result is not valid JSON")

            if job.is_finished:
                return job.result
            if job.is_failed:
                raise HTTPException(status_code=500, detail=f"Job failed: {job.exc_info}")

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise HTTPException(status_code=504, detail="Timeout: job did not complete in time")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/")
def inicio():
    return {"message": "video2text API"}

