from ocr import OCR
from pydantic import BaseModel, Field
import spacy
import time

class NLP:
    def __init__(self, en_core_type="en_core_web_lg"):
        """
        ARGS:
            en_core_type:
                Fastest: 'en_core_web_sm' (12ms for 200char)
                Medium: 'en_core_web_lg' (20ms for 200char)
        """
        self.nlp = spacy.load(en_core_type)
        pass

    def handle_text(self, text: str) -> dict:
        doc = self.nlp(text)

        entities = [(ent.text, ent.label_) for ent in doc.ents]

        return {
            "text": text,
            "tokens": [token.text for token in doc],
            "entities": entities,
            "pos_tags": [(token.text, token.pos_) for token in doc],
        }
        
    
    pass



if __name__ == '__main__':
    nlp = NLP()
    text = "This is an example input with about 200 characters. It tests the processing speed of a small spaCy model, mainly used for basic NLP tasks such as tokenization, tagging, and named entity recognition."

    start = time.perf_counter()

    res = nlp.handle_text(text)
    print(res)

    end = time.perf_counter()

    print(f"Processed in {(end - start)*1000:.2f} ms")
