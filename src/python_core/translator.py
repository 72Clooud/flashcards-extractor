from deep_translator import GoogleTranslator

class Translator:
    def __init__(self, source_lang: str = "en", target_lang: str = "pl"):
        self.translator = GoogleTranslator(source=source_lang, target=target_lang)

    def translate(self, text: str) -> str:
        if not text.strip():
            return ""
        
        try:
            translated_text = self.translator.translate(text)
            return translated_text
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    