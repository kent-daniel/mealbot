import yt_dlp
# import whisper # No longer needed
import os
import json
import tempfile
from typing import Dict, Any, Optional
import re # Added for regex in convert_vtt_to_text, but will be removed

# Define a base directory for saving files
# This will be relative to the working directory of the application
SAVE_BASE_DIR = "data"

def download_audio(url: str, output_path: str) -> str:
    """
    Downloads audio from a given URL using yt-dlp.
    Returns the path to the downloaded audio file.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            return os.path.splitext(filename)[0] + '.mp3'
    except Exception as e:
        print(f"Error downloading audio: {e}")
        raise

def transcribe_audio(model, audio_path: str) -> Dict[str, Any]:
    """
    Transcribes audio from a given file using the Faster Whisper model.
    Returns the transcription result.
    """
    try:
        segments, info = model.transcribe(audio_path, beam_size=5)
        
        full_text = ""
        for segment in segments:
            full_text += segment.text
        
        return {"text": full_text, "language": info.language, "segments": [s._asdict() for s in segments]}
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        raise

def save_transcript_to_json(transcript: Dict[str, Any], output_path: str):
    """
    Saves the transcription result to a JSON file.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True) # Ensure directory exists
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(transcript, f, ensure_ascii=False, indent=4)
        print(f"Transcript saved to {output_path}")
    except Exception as e:
        print(f"Error saving transcript: {e}")
        raise

def extract_subtitles(url: str, output_base_path: str) -> Optional[str]:
    """
    Extracts subtitles from a given URL using yt-dlp.
    Returns the path to the downloaded subtitle file (e.g., .srt) if found, else None.
    """
    # yt-dlp will save subtitles with a name like <video_title>.<lang>.<ext>
    # We'll let yt-dlp determine the filename and then find it.
    
    # Use a temporary output template that yt-dlp will use to name the file
    # This will be in the same directory as output_base_path
    temp_output_template = os.path.join(os.path.dirname(output_base_path), "%(title)s.%(ext)s")

    ydl_opts = {
        'writeautomaticsub': True,
        'subtitlesformat': 'srt',
        'skip_download': True, # Don't download the video itself
        'outtmpl': temp_output_template, # This sets the base name for the output file
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            
            # yt-dlp typically appends the language code and extension to the outtmpl.
            # For example, if output_path is 'my_video_subtitles', and the language is 'en',
            # the file might be saved as 'my_video_subtitles.en.srt'.
            # We can try to infer the full path based on common yt-dlp behavior.

            # Get the base output directory and filename prefix
            output_dir = os.path.dirname(output_path) if os.path.dirname(output_path) else '.'
            filename_prefix = os.path.basename(output_path)

            # Check for the expected .srt file in the output directory
            # We'll look for files that start with our prefix and end with '.srt'
            for filename in os.listdir(output_dir):
                if filename.startswith(filename_prefix) and filename.endswith('.srt'):
                    return os.path.join(output_dir, filename)

    except yt_dlp.DownloadError as e:
        print(f"Error downloading subtitles: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    
    return None

def process_video_url(url: str, model=None) -> Dict[str, Any]:
    """
    Main pipeline to get transcript from URL.
    Prioritizes extracting subtitles, falls back to audio transcription.
    Accepts a pre-loaded Whisper model.
    """
    import uuid
    run_id = str(uuid.uuid4())

    save_dir = os.path.join(SAVE_BASE_DIR, run_id)
    os.makedirs(save_dir, exist_ok=True)

    transcript_output_path = os.path.join(save_dir, "transcript.json")
    
    print(f"Processing URL: {url}")

    # 1. Try to extract subtitles first
    subtitle_file = extract_subtitles(url, os.path.join(save_dir, "subtitle"))
    if subtitle_file:
        print(f"Subtitles found and downloaded to: {subtitle_file}")
        # Directly read the SRT file
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            transcript_text = f.read()
        
        transcript = {"text": transcript_text, "source": "subtitles"}
        save_transcript_to_json(transcript, transcript_output_path)
        print(f"Transcript saved from subtitles to: {transcript_output_path}")
        return {
            "transcript": transcript,
            "transcript_file_path": transcript_output_path,
            "source": "subtitles"
        }
    else:
        print("No subtitles found, falling back to audio transcription.")
        # 2. Fallback to audio download and transcription
        # The model is passed from main.py, so no need to load it here
        # if model is None:
        #     print("Loading Whisper model for audio transcription...")
        #     model = whisper.load_model("tiny")
        #     print("Whisper model loaded.")

        audio_output_path = os.path.join(save_dir, "audio")
        audio_file = download_audio(url, audio_output_path)
        print(f"Audio downloaded to: {audio_file}")

        transcript = transcribe_audio(model, audio_file)
        print("Audio transcribed.")

        save_transcript_to_json(transcript, transcript_output_path)
        print(f"Transcript saved from audio to: {transcript_output_path}")

        return {
            "transcript": transcript,
            "audio_file_path": audio_file,
            "transcript_file_path": transcript_output_path,
            "source": "audio_transcription"
        }
