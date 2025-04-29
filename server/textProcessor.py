import re

class Normalizer:
    def __init__(self):
        pass
    
    def __remove_extra_whitespace(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text)

    def convert_text_to_lower_case(self, text: str) -> str:
        lowercase = text.strip().lower()
        return self.__remove_extra_whitespace(lowercase) 
    
    def convert_text_to_upper_case(self, text: str) -> str:
        uppercase = text.strip().upper()
        return self.__remove_extra_whitespace(uppercase)

import re
from typing import List, Dict

class UnitExtractor:
    def __init__(self):
        self.known_units = {"pcs", "kg", "g", "mg", "bpm", "m", "s", "cm", "mm", "hz", "l", "ml"}
        self.learned_units = set()

    def extract_units(self, tokens: List[str]) -> Dict:
        unit_pairs = []
        annotations = []

        for i, token in enumerate(tokens):
            label = self._label_token(token, tokens, i)
            annotations.append((token, label))

            # Check for value + unit pattern
            if i > 0 and tokens[i-1].replace(',', '').replace('.', '').isdigit() and label == "UNIT":
                value = tokens[i-1]
                unit = token
                unit_pairs.append({
                    "value": value,
                    "unit": unit
                })

        return {
            "annotations": annotations,
            "unit_pairs": unit_pairs
        }

    def _label_token(self, token, tokens, i):
        token_clean = token.lower()

        if self._is_known_unit(token_clean):
            return "UNIT"
        if self._looks_like_unit(token_clean):
            self.learned_units.add(token_clean)
            return "UNIT"
        if i > 0 and tokens[i-1].isdigit():
            if len(token_clean) <= 6 and token_clean.isalpha():
                self.learned_units.add(token_clean)
                return "UNIT"
        return "WORD"

    def _is_known_unit(self, token):
        return token in self.known_units or token in self.learned_units

    def _looks_like_unit(self, token):
        return re.match(r'^[a-zA-Z]{1,5}/[a-zA-Z0-9]{1,5}$', token) is not None


class TextProcessor:
    def __init__(self):
        self.unit_extractor = UnitExtractor()

    def normalize_text(self, nlp_output: dict) -> dict:
        tokens = nlp_output.get('tokens', [])
        units_info = self.unit_extractor.extract_units(tokens)
        
        nlp_output['units_info'] = units_info
        return nlp_output
