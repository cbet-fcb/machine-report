import re
from typing import List, Dict, Tuple
from rapidfuzz import process, fuzz

import re
from typing import List, Tuple, Dict
from rapidfuzz import fuzz, process


class IDExtractor:
    def __init__(self):
        self.known_ids = {
            "Machine 1", "Machine 2", "Machine 3", "Machine 4",
            "Machine 5", "Machine 6", "Machine 7", "Machine 8",
            "Machine 9", "Machine 10", "Machine 11", "Machine 12",
            "Machine 13"
        }
        self.learned_ids = set()
        self.similarity_threshold = 85  # High to avoid false positives

    def extract_ids(self, tokens: List[str]) -> Dict:
        id_matches = []
        annotations = []

        i = 0
        while i < len(tokens):
            token = tokens[i]
            label, matched_id = self._label_token(token, tokens, i)

            annotations.append((token, label))

            if label == "ID":
                id_matches.append(matched_id)
                # If it was a combined "Machine + number", skip the next token
                if i < len(tokens) - 1 and token.lower() == "machine" and tokens[i + 1].isdigit():
                    i += 1

            i += 1

        return {
            "annotations": annotations,
            "id_matches": id_matches
        }

    def _label_token(self, token: str, tokens: List[str], i: int) -> Tuple[str, str]:
        normalized = self._normalize_token(token)

        # Try exact known match
        if self._is_known_id(normalized):
            return "ID", normalized

        # Try "Machine" + number pattern
        if i < len(tokens) - 1 and token.lower() == "machine" and tokens[i + 1].isdigit():
            combined = f"{token.title()} {tokens[i + 1]}"
            if self._is_known_id(combined):
                return "ID", combined

        # Fuzzy match if nothing else worked
        best_match, score, _ = process.extractOne(
            normalized, self.known_ids, scorer=fuzz.ratio
        )
        if score >= self.similarity_threshold:
            self.learned_ids.add(best_match)
            return "ID", best_match

        return "WORD", None

    def _is_known_id(self, token: str) -> bool:
        return token in self.known_ids or token in self.learned_ids

    def _normalize_token(self, token: str) -> str:
        return re.sub(r'[^\w\s]', '', token).title()

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
        i = 0

        while i < len(tokens):
            token = tokens[i]
            combined_token = token

            # Try combining next token(s) if they exist
            if i + 2 < len(tokens) and tokens[i+1] in {"/", "-"}:
                combined_token = f"{token}/{tokens[i+2]}"
                normalized_combined = self._normalize_token(combined_token)

                best_match, score, _ = process.extractOne(
                    normalized_combined, self.known_units, scorer=fuzz.ratio
                )

                if score >= self.similarity_threshold:
                    label = "UNIT"
                    matched_unit = best_match
                    annotations.append((combined_token, label))

                    # Check for value before combined unit
                    if i > 0 and tokens[i-1].replace(',', '').replace('.', '').isdigit():
                        unit_pairs.append({
                            "value": tokens[i-1],
                            "unit": matched_unit
                        })

                    i += 3  # Skip the combined tokens
                    continue

            # Fallback to normal single-token labeling
            label, matched_unit = self._label_token(token, tokens, i)
            annotations.append((token, label))

            # Check for value + unit pattern
            if i > 0 and tokens[i-1].replace(',', '').replace('.', '').isdigit() and label == "UNIT":
                unit_pairs.append({
                    "value": tokens[i-1],
                    "unit": matched_unit or token
                })

            i += 1

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
    
class Normalizer:
    def __init__(self):
        pass

    def convert_ocr_result_alphabets_to_small_letter(self, text: str) -> str:
        """
        Converts all alphabetic characters in the OCR result to lowercase.
        This helps normalize OCR output for consistent processing.
        """
        if not isinstance(text, str):
            raise TypeError("Input must be a string.")
        return text.lower()

class TextProcessor:
    def __init__(self):
        self.unit_extractor = UnitExtractor()
        self.id_extractor = IDExtractor()

    def process_text(self, nlp_output: dict) -> dict:
        tokens = nlp_output.get('tokens', [])

        units_info = self.unit_extractor.extract_units(tokens)
        ids_info = self.id_extractor.extract_ids(tokens)

        res = {}
        res['unit_info'] = units_info
        res['ids_info'] = ids_info

        return res
    
if __name__ == '__main__':
    pass