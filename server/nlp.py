from ocr import OCR
from pydantic import BaseModel, Field
import spacy
from spacy.tokenizer import Tokenizer
from spacy.util import compile_prefix_regex, compile_infix_regex, compile_suffix_regex
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

        infix_re = compile_infix_regex(
            self.nlp.Defaults.infixes +
            [
                r"(?<=[a-zA-Z])(?=\d)",  # Split letter -> digit
                r"(?<=\d)(?=[a-zA-Z])",  # Split digit -> letter
                r"(?<=\w)(?=[&:])",      # Split word -> (& or :)
                r"(?<=[&:])(?=\w)",      # Split (& or :) -> word
            ]
        )
        self.nlp.tokenizer = Tokenizer(
            self.nlp.vocab,
            rules=self.nlp.Defaults.tokenizer_exceptions,
            prefix_search=compile_prefix_regex(self.nlp.Defaults.prefixes).search,
            suffix_search=compile_suffix_regex(self.nlp.Defaults.suffixes).search,
            infix_finditer=infix_re.finditer,
            token_match=self.nlp.Defaults.token_match,
        )
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

if __name__ == '__main__':
    nlp = NLP()
    text = "This is an example input with about 200 characters. It tests the processing speed of a small spaCy model, mainly used for basic NLP tasks such as tokenization, tagging, and named entity recognition."

    start = time.perf_counter()

    res = nlp.handle_text(text)
    print(res)

    end = time.perf_counter()

    print(f"Processed in {(end - start)*1000:.2f} ms")
