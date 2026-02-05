import os
import re
import time
from dotenv import load_dotenv
from text_analyzer import TextAnalyzer
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

def clear_temp_folder(temp_folder: Path) -> None:
    if temp_folder.exists() and temp_folder.is_dir():
        for item in temp_folder.iterdir():
            if item.is_file():
                item.unlink()

def clear_old_logs(log_file: Path) -> None:
    if log_file.exists():
        log_file.unlink()
    log_file.touch()

def parse_line(line: str) -> tuple[str, float, float, str]:
    parts = line.strip().split("|")
    if len(parts) != 4:
        raise ValueError("Invalid log line format")
    return parts[0], float(parts[1]), float(parts[2]), parts[3] # path, start_time, end_time, subtitle_text

def process_entry(line, anki_client: AnkiClient, media_processor: MediaProcessor, translator: Translator, text_analyzer: TextAnalyzer):
    data = parse_line(line)
    if not data:
        return
    video_path, start_time, end_time, subtitle_text = data
    full_translation_pl = translator.translate(subtitle_text)

    phrase_en, phrase_pl = text_analyzer.get_phrase_pair(subtitle_text, full_translation_pl, translator)

    highlighted_front = subtitle_text
    highlighted_back = full_translation_pl

    if phrase_en:
        highlighted_front = text_analyzer.highlight_phrase(subtitle_text, phrase_en)
    
    if phrase_pl:
        highlighted_back = text_analyzer.highlight_phrase(full_translation_pl, phrase_pl)
    else:
        doc_en = text_analyzer.nlp_en(subtitle_text)
        rare_token = text_analyzer.find_rarest_word_token(doc_en)
        if rare_token:
             rare_pl = translator.translate(rare_token.text)
             highlighted_back = text_analyzer.highlight_phrase(full_translation_pl, rare_pl)
    try:
        audio_path = media_processor.extract_audio(video_path, start_time, end_time)
    except Exception as e:
        print(f"FFmpeg failed : {e}")
        return

    note = AnkiNote(
        deckName=os.getenv("DECK_NAME"),
        fields={
            "Front": highlighted_front,
            "Back": highlighted_back
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
    clear_temp_folder(Path(PROJECT_ROOT) / "temp")
    clear_old_logs(Path(LOG_FILE))
    
    text_analyzer = TextAnalyzer()
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
            if not line:
                time.sleep(1)
                continue
                

            process_entry(line, anki_client, media_processor, translator, text_analyzer)

if __name__ == "__main__":
    main()