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
        job = task_queue.enqueue(process_video, url, job_id=task_id,job_timeout=14400)

        return jsonify({"message": "Video processing started", "task_id": job.id}), 202
    except Exception as e:
        return jsonify({"error": "An error occurred while processing the video", "details": str(e)}), 500

    

@app.route('/status/<task_id>')
def check_status(task_id):
    job = task_queue.fetch_job(task_id)
    if job is None:
        return jsonify({"error": "Job not found"}), 404

    if job.is_finished:
        return jsonify({"status": "finished", "result": job.result})
    elif job.is_failed:
        return jsonify({"status": "failed", "error": str(job.exc_info)})
    else:
        return jsonify({"status": job.get_status()})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
