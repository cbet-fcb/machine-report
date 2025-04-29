import re
from typing import List, Dict
from rapidfuzz import process, fuzz

class UnitExtractor:
    def __init__(self):
        self.known_units = {
            "pcs", "kg", "g", "mg", "bpm", "m", "s", "cm", "mm",
            "hz", "l", "ml", "pcs/min", "m/s", "kg/cm²", "mm/s"
        }
        self.learned_units = set()
        self.similarity_threshold = 80

    def extract_units(self, tokens: List[str]) -> Dict:
        unit_pairs = []
        annotations = []

        for i, token in enumerate(tokens):
            label, matched_unit = self._label_token(token, tokens, i)
            annotations.append((token, label))

            # Check for value + unit pattern
            if i > 0 and tokens[i-1].replace(',', '').replace('.', '').isdigit() and label == "UNIT":
                value = tokens[i-1]
                unit_pairs.append({
                    "value": value,
                    "unit": matched_unit or token
                })

        return {
            "annotations": annotations,
            "unit_pairs": unit_pairs
        }

    def _label_token(self, token: str, tokens: List[str], i: int):
        normalized = self._normalize_token(token)

        if self._is_known_unit(normalized):
            return "UNIT", normalized

        if self._looks_like_unit(normalized):
            self.learned_units.add(normalized)
            return "UNIT", normalized

        # Fuzzy matching
        best_match, score, _ = process.extractOne(
            normalized, self.known_units, scorer=fuzz.ratio
        )
        if score >= self.similarity_threshold:
            self.learned_units.add(best_match)
            return "UNIT", best_match

        if i > 0 and tokens[i-1].isdigit():
            if len(normalized) <= 6 and normalized.isalpha():
                self.learned_units.add(normalized)
                return "UNIT", normalized

        return "WORD", None

    def _is_known_unit(self, token):
        return token in self.known_units or token in self.learned_units

    def _looks_like_unit(self, token):
        return re.match(r'^[a-zA-Z]{1,5}/[a-zA-Z0-9]{1,5}$', token) is not None

    def _normalize_token(self, token: str) -> str:
        return re.sub(r'[^\w/]', '', token.lower())
