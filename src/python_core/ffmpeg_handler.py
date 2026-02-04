import os
import shutil
import ffmpeg
from pathlib import Path

class MediaProcessor:
    def __init__(self, ffmpeg_path: str, temp_dir: Path):
        self.ffmpeg_path = ffmpeg_path
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def extract_audio(self, video_path: str, start: float, end: float) -> Path:
        file_prefix = f"audio_{int(start * 1000)}"
        audio_output = self.temp_dir / f"{file_prefix}.mp3"
        
        duration = end - start + 0.1
        
        try:
            (
                ffmpeg
                .input(video_path, ss=start)
                .output(str(audio_output), t=duration, acodec='libmp3lame', ab='128k')
                .overwrite_output()
                .run(cmd=self.ffmpeg_path, capture_stdout=True, capture_stderr=True)
            )
            return audio_output
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            print(f"FFmpeg error: {error_message}")
            raise