import os
import time
from dotenv import load_dotenv
from ffmpeg_handler import MediaProcessor
from anki_handler import AnkiClient, AnkiNote, AnkiMedia
from translator import Translator
from pathlib import Path

load_dotenv()

PROJECT_ROOT = os.getenv("PROJECT_ROOT")
LOG_FILE = os.getenv("LOG_FILE")
FFMPEG_PATH = os.getenv("FFMPEG_PATH")
ANKI_URL = os.getenv("ANKI_URL")
DECK_NAME = os.getenv("DECK_NAME")
VIDEO_PATH = os.getenv("VIDEO_PATH")

def parse_line(line: str):
    parts = line.strip().split("|")
    if len(parts) != 4:
        raise ValueError("Invalid log line format")
    return parts[0], float(parts[1]), float(parts[2]), parts[3] # path, start_time, end_time, subtitle_text

def process_entry(line, anki_client: AnkiClient, media_processor: MediaProcessor, translator: Translator):
    data = parse_line(line)
    if not data:
        return
    video_path, start_time, end_time, subtitle_text = data
    translation = translator.translate(subtitle_text)

    try:
        audio_path = media_processor.extract_audio(video_path, start_time, end_time)
    except Exception as e:
        print(f"FFmpeg failed : {e}")
        return
    
    note = AnkiNote(
        deckName=os.getenv("DECK_NAME"),
        fields={
            "Front": subtitle_text,
            "Back": translation
        },
        modelName="Basic",
        audio=[AnkiMedia(
            path=str(audio_path.absolute()),
            filename=audio_path.name, 
            fields=["Back"]
        )]
    )

    if anki_client.add_note(note):
        print(f"Added note for subtitle at start_time {start_time:.3f}s")
    else:
        print(f"Failed to add note for subtitle at start_time {start_time:.3f}s")

def main():
    anki_client = AnkiClient(ANKI_URL)
    media_processor = MediaProcessor(FFMPEG_PATH, Path(PROJECT_ROOT) / "temp")
    translator = translator = Translator(source_lang="en", target_lang="pl")
    log_path = Path(LOG_FILE)
    
    if not log_path.exists():
        raise FileNotFoundError(f"Log file not found: {log_path}")

    with open(log_path, "r", encoding="utf-8") as f:
        f.seek(0, 2)

        while True:
            line = f.readline()
            print(line)
            if not line:
                print("No new line, waiting...")
                time.sleep(1)
                continue
                

            process_entry(line, anki_client, media_processor, translator)

if __name__ == "__main__":
    main()