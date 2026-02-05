import re
import spacy
from wordfreq import zipf_frequency

class TextAnalyzer:
    def __init__(self):
        self.nlp_en = spacy.load("en_core_web_sm")
        self.nlp_pl = spacy.load("pl_core_news_sm")

    def find_rarest_word_token(self, doc):
        candidates = []
        for token in doc:
            if token.is_punct or token.is_space or token.pos_ == "PROPN" or len(token.text) < 3:
                continue
            score = zipf_frequency(token.lemma_, 'en')
            candidates.append((token, score))
        
        if not candidates:
            return None
        return min(candidates, key=lambda x: x[1])[0]

    def get_phrase_pair(self, text_en: str, text_pl: str, translator):
        
        doc_en = self.nlp_en(text_en)
        rare_token = self.find_rarest_word_token(doc_en)
        if not rare_token:
            return None, None

        english_phrase_span = None
        for chunk in doc_en.noun_chunks:
            if rare_token.i >= chunk.start and rare_token.i < chunk.end:
                english_phrase_span = chunk
                break
        if not english_phrase_span:
            english_phrase_span = doc_en[rare_token.i : rare_token.i+1]
        final_en_text = english_phrase_span.text
    
        translated_phrase = translator.translate(final_en_text).lower()
        doc_pl = self.nlp_pl(text_pl)
        
        doc_trans = self.nlp_pl(translated_phrase)
        trans_root = None
        for token in doc_trans:
            if token.dep_ == "ROOT" or token.pos_ == "NOUN":
                trans_root = token
                break
        if not trans_root: trans_root = doc_trans[0]
        trans_root_lemma = trans_root.lemma_.lower()

        real_root_token = None
        for token in doc_pl:
            if token.lemma_.lower() == trans_root_lemma:
                real_root_token = token
                break
        if not real_root_token:
            return final_en_text, None

        good_indices = {real_root_token.i}
        
        for child in real_root_token.children:
            if child.pos_ in ['ADJ', 'NUM', 'DET', 'PROPN'] or (child.pos_ == 'NOUN' and child.dep_ == 'nmod'):
                good_indices.add(child.i)
            elif child.dep_ in ['case', 'cc', 'punct', 'mark']:
                continue

        sorted_indices = sorted(list(good_indices))
        
        words = []
        for i in sorted_indices:
            words.append(doc_pl[i].text)

        final_pl_text = doc_pl[sorted_indices[0]:sorted_indices[-1]+1].text

        return final_en_text, final_pl_text

    def highlight_phrase(self, full_text: str, phrase_to_highlight: str):
        if not phrase_to_highlight:
            return full_text
        pattern = re.compile(rf'({re.escape(phrase_to_highlight)})', re.IGNORECASE)
        return pattern.sub(r'<b style="color:#ff6666">\1</b>', full_text)