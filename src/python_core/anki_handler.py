import os
import requests
from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class AnkiMedia:
    path: str
    filename: str
    fields: List[str]

@dataclass
class AnkiNote:
    deckName: str
    fields: dict
    modelName: str = "Basic"
    audio: Optional[List[AnkiMedia]] = None
    picture: Optional[List[AnkiMedia]] = None
    tags: Optional[List[str]] = None

class AnkiClient:
    def __init__(self, url: str):
        self.url = url

    def _invoke(self, action: str, **params):
        payload = {
            "action": action,
            "version": 6,
            "params": params
        }
        try:
            response = requests.post(self.url, json=payload).json()
            if len(response) != 2:
                raise Exception("Unexpected number of fields in response")
            if 'error' not in response:
                raise Exception("Missing error field in response")
            if response['error'] is not None:
                raise Exception(f"Anki error: {response['error']}")
            return response['result']
        except Exception as e:
            print(f"Error invoking Anki action {action}: {e}")
            return None
        
    def add_note(self, note: AnkiNote):
        return self._invoke("addNote", note=asdict(note))