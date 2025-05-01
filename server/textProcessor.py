import re
from typing import List, Dict, Tuple
from rapidfuzz import process, fuzz

import re
from typing import List, Tuple, Dict
from rapidfuzz import fuzz, process


class IDExtractor:
    def __init__(self):
        self.known_ids = {f"Machine {i}" for i in range(1, 14)}
        self.learned_ids = set()
        self.similarity_threshold = 85

    def extract_ids(self, tokens: List[str]) -> Dict:
        tokens = self._split_compound_tokens(tokens)
        id_matches = []
        annotations = []

        i = 0
        while i < len(tokens):
            matched_id, skip = self._attempt_fuzzy_machine_id(tokens, i)

            if matched_id:
                annotations.append((tokens[i], "ID"))
                id_matches.append(matched_id)
                i += skip + 1
                continue

            label, matched_id = self._label_token(tokens[i])
            annotations.append((tokens[i], label))
            if label == "ID":
                id_matches.append(matched_id)
            i += 1

        print("Extracted IDs:", id_matches)
        print("Annotations:", annotations)

        return {
            "annotations": annotations,
            "id_matches": id_matches
        }

    def _label_token(self, token: str) -> Tuple[str, str]:
        normalized = self._normalize_token(token)

        if normalized == "Machine":
            return "WORD", None

        return "WORD", None

    def _attempt_fuzzy_machine_id(self, tokens: List[str], i: int) -> Tuple[str, int]:
        token = tokens[i]
        normalized = self._normalize_token(token)

        if normalized != "Machine":
            return None, 0

        for offset in range(1, 3):
            j = i + offset
            if j < len(tokens):
                next_token = tokens[j]
                if next_token.isdigit():
                    candidate = f"Machine {next_token}"
                    if self._is_known_id(candidate):
                        return candidate, offset
        return None, 0

    def _normalize_token(self, token: str) -> str:
        token = re.sub(r'[^\w\s]', '', token).lower()
        corrected = self._fuzzy_correct(token, targets=["machine"])
        return corrected.title()

    def _fuzzy_correct(self, token: str, targets: List[str]) -> str:
        if not token:
            return token
        best_match, score, _ = process.extractOne(token, targets, scorer=fuzz.ratio)
        if score >= self.similarity_threshold:
            if token.lower() != best_match.lower():
                print(f"Corrected '{token}' → '{best_match}' (score={score})")
            return best_match
        return token

    def _is_known_id(self, token: str) -> bool:
        return token in self.known_ids or token in self.learned_ids

    def _split_compound_tokens(self, tokens: List[str]) -> List[str]:
        split_tokens = []
        for token in tokens:
            match = re.match(r'(machine)(\d+)', token.lower())
            if match:
                split_tokens.extend([match.group(1), match.group(2)])
            else:
                split_tokens.append(token)
        return split_tokens
    
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