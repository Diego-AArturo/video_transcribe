#audio_writer.py

import whisper
# import google.generativeai as genai
from moviepy import VideoFileClip
import json
import logging

# Cargar modelo Whisper
model = whisper.load_model("base")

# Configurar Gemini API


def video2audio(path_in: str, path_out: str):
    """Extrae el audio de un video y lo guarda en MP3."""
    try:
        video_clip = VideoFileClip(path_in)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(f'{path_out}.mp3')
    except Exception as e:
        logging.error(f"Error extracting audio: {e}")

def transcribe_audio(file_path: str):
    """Transcribe audio usando Whisper y retorna segmentos con timestamps."""
    result = model.transcribe(file_path, task="transcribe")
    return [{"start": s["start"], "end": s["end"], "text": s["text"]} for s in result["segments"]]

# def refine_text_with_ai(segments: list):
#     """Mejora la redacción de todos los segmentos en una sola solicitud."""
#     API_KEY = ' '
#     genai.configure(api_key=API_KEY)
#     if not segments:
#         return segments

#     model_g = genai.GenerativeModel("models/gemini-1.5-flash")
#     texts = "\n".join([s["text"] for s in segments])

#     response = model_g.generate_content(texts)
#     corrected_texts = response.text.split("\n")

#     for i in range(min(len(segments), len(corrected_texts))):
#         segments[i]["text"] = corrected_texts[i]

#     return segments

def audio2json(file_path: str, out_path: str, ai: bool = False):
    """Procesa audio a texto y genera un JSON con timestamps."""
    logging.info("Transcribing audio...")
    segments = transcribe_audio(file_path)

    # if ai:
    #     segments = refine_text_with_ai(segments)

    with open(out_path, 'w', encoding='utf-8') as json_file:
        json.dump(segments, json_file, ensure_ascii=False, indent=4)

    return segments
