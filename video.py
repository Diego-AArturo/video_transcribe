#video.py
import subprocess
import os
import logging
import json
from pathlib import Path
from audio_writer import audio2json, video2audio
import requests
from urllib.parse import urlparse
import uuid


# Configuración de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

CHUNK_DURATION = 1620 #30 minutos por segmento

def split_video(video_path, chunk_duration=CHUNK_DURATION):
    """Divide un video en fragmentos de duración específica usando ffmpeg."""
    output_pattern = "chunk_%03d.mp4"
    logging.info(f"Splitting {video_path} into chunks of {chunk_duration} seconds...")

    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-analyzeduration", "2147483647",  # mayor análisis para detectar parámetros
                "-probesize", "2147483647",
                "-i", str(video_path),
                "-c", "copy",
                "-map", "0",
                "-segment_time", str(chunk_duration),
                "-f", "segment",
                "-reset_timestamps", "1",
                output_pattern
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        logging.info(result.stdout)
        logging.debug(result.stderr)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during video splitting: {e.stderr}")
        return []

    chunks = sorted(Path().glob("chunk_*.mp4"))
    if not chunks:
        logging.error("No video chunks were created after splitting.")
    return chunks

def download_from_s3_streaming(url, chunk_size=8192, output_path="video.mp4"):
    """
    Descarga un archivo desde S3 en modo streaming sin cargarlo completamente en memoria.
    """
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise Exception(f"Error descargando video: {response.status_code}")

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)

    return output_path

def process_video(video_url,ai=False):
    unique_id = uuid.uuid4().hex[:8]
    path_video = Path(f"video_{unique_id}.mp4")
    
    if not path_video.exists():
        path_video = Path(f"video_{unique_id}.mp4.webm")
    path_json = Path(f"video_{unique_id}.json")
    
    temp_files = []  # Para manejar la limpieza de archivos al final

    try:
        logging.info(f"Downloading video from: {video_url}")
        result = download_from_s3_streaming(video_url, output_path=str(path_video))
        logging.info(result)

        if not path_video.exists() or path_video.stat().st_size == 0:
            logging.error("Downloaded video file is missing or empty.")
            return None

        video_chunks = split_video(path_video)
        if not video_chunks:
            logging.error("No video chunks were created.")
            return None

        combined_data = []
        for idx, chunk in enumerate(video_chunks):
            chunk_mp3 = chunk.with_suffix(".mp3")
            chunk_json = chunk.with_suffix(".json")
            temp_files.extend([chunk, chunk_mp3, chunk_json])

            logging.info(f"Processing chunk {idx + 1}/{len(video_chunks)}: {chunk}")

            video2audio(str(chunk), str(chunk_mp3.stem))
            if not chunk_mp3.exists() or chunk_mp3.stat().st_size == 0:
                logging.error(f"Audio extraction failed for chunk {chunk}.")
                continue

            audio2json(str(chunk_mp3), str(chunk_json),ai)
            if not chunk_json.exists() or chunk_json.stat().st_size == 0:
                logging.error(f"Transcription failed for chunk {chunk}.")
                continue

            with open(chunk_json, "r", encoding="utf-8") as file:
                combined_data.extend(json.load(file))

        if not combined_data:
            logging.error("No data was processed from the video chunks.")
            return None

        with open(path_json, "w", encoding="utf-8") as file:
            json.dump(combined_data, file, ensure_ascii=False, indent=4)

        logging.info("Processing complete. JSON saved.")

        # Limpieza de archivos temporales
        for temp_file in temp_files:
            try:
                temp_file.unlink(missing_ok=True)
            except Exception as e:
                logging.warning(f"Could not delete {temp_file}: {e}")
        
        if path_video.exists():
            path_video.unlink(missing_ok=True)        
        if path_json.exists():
            path_json.unlink(missing_ok=True)

        return combined_data

    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    return None





