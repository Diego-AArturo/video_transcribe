#app.py
from flask import Flask, request, jsonify
import json
from rq import Queue
import redis
import uuid
from video import process_video

app = Flask(__name__)
redis_conn = redis.Redis(host='redis', port=6379)
task_queue = Queue(connection=redis_conn)

@app.route('/', methods=['GET'])
def inicio():
    return 'video2text'

@app.route('/video2text', methods=['POST'])
def enviar_url():
    url = request.json.get('url', None)
    if not url:
        return jsonify({"error": "No URL found in the request"}), 400 

    try:
        task_id = uuid.uuid4().hex
        job = task_queue.enqueue(process_video, url, job_id=task_id, timeout=3600)

        # Esperar hasta 1 hora por la finalización del trabajo
        result = job.wait(timeout=3600)

        if job.is_failed:
            return jsonify({"error": "Job failed", "details": str(job.exc_info)}), 500

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while processing the video", "details": str(e)}), 500
    



if __name__ == '__main__':
    app.run(host='0.0.0.0')
