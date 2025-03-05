#app.py
from flask import Flask, request, jsonify
import json
from video import process_video

app = Flask(__name__)

@app.route('/', methods=['GET'])
def inicio():
    return 'InsectID'

@app.route('/video2text', methods=['POST'])
def enviar_url():
    url = request.form.get('url')
    if not url:
        return jsonify({"error": "No URL found in the request"}), 400

    try:
        result = process_video(url)
        if not result:
            return jsonify({"error": "Transcription failed"}), 500
    except Exception as e:
        return jsonify({"error": "An error occurred while processing the video", "details": str(e)}), 500

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0')


