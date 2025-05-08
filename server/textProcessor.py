import re
from typing import List, Dict, Tuple, Optional
from rapidfuzz import process, fuzz

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

    def _label_token(self, token: str) -> Tuple[str, str, str]:
        normalized = self._normalize_token(token)

        if normalized == "Machine":
            return "WORD", None

        return "WORD", None

    def _attempt_fuzzy_machine_id(self, tokens: List[str], i: int) -> Tuple[str, int]:
        # Case 1: "Machine" then digit
        if self._normalize_token(tokens[i]) == "Machine":
            for offset in range(1, 3):
                j = i + offset
                if j < len(tokens) and tokens[j].isdigit():
                    candidate = f"Machine {tokens[j]}"
                    if self._is_known_id(candidate):
                        return candidate, offset

        # Case 2: digit then "Machine"
        if tokens[i].isdigit() and i + 1 < len(tokens):
            if self._normalize_token(tokens[i + 1]) == "Machine":
                candidate = f"Machine {tokens[i]}"
                if self._is_known_id(candidate):
                    return candidate, 1

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
        self.similarity_threshold = 75

    def extract_units(self, tokens: List[str], max_distance: int = 2) -> Dict:
        unit_pairs = []
        annotations = []
        i = 0

        while i < len(tokens):
            token = tokens[i]
            combined_token = token

            corrected_token = self._fuzzy_correct(combined_token)
            # Try combining next token(s) if they exist
            if i + 2 < len(tokens) and tokens[i+1] in {"/", "-"}:
                corrected_next_token = self._fuzzy_correct(tokens[i+2])
                
                combined_token = f"{corrected_token}/{corrected_next_token}"
                normalized_combined = self._normalize_token(combined_token)

                best_match, score, _ = process.extractOne(
                    normalized_combined, self.known_units, scorer=fuzz.ratio
                )

                if score >= self.similarity_threshold:
                    label = "UNIT"
                    matched_unit = best_match
                    annotations.append((combined_token, label))

                    # Check for value before combined unit with distance
                    value, distance = self._find_nearest_numeric(tokens, i, max_lookback=max_distance)
                    if value:
                        unit_pairs.append({
                            "value": value,
                            "unit": matched_unit,
                            "distance": distance
                        })

                    i += 3  # Skip the combined tokens
                    continue

            # Fallback to normal single-token labeling
            label, matched_unit = self._label_token(token, tokens, i)
            annotations.append((token, label))

            # Check for value + unit pattern
            value, distance = self._find_nearest_numeric(tokens, i)
            if value and label == "UNIT":
                unit_pairs.append({
                    "value": value,
                    "unit": matched_unit or token,
                    "distance": distance
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

    def _fuzzy_correct(self, token: str) -> str:
        if not token:
            return token
        best_match, score, _ = process.extractOne(token, list(self.known_units), scorer=fuzz.ratio)
        if score >= self.similarity_threshold:
            return best_match
        return token

    def _find_nearest_numeric(self, tokens: List[str], index: int, max_lookback: int = 2) -> Tuple[Optional[str], Optional[int]]:
        for offset in range(1, max_lookback + 1):
            if index - offset >= 0:
                candidate = tokens[index - offset].replace(',', '').replace('.', '')
                if candidate.isdigit():
                    return tokens[index - offset], offset
        return None, None

    
class Normalizer:
    def __init__(self):
        pass

    def fix_leading_O_in_text(self, text: str, targets: list[tuple[str, str, str]]) -> str:
        """
        Corrects occurrences where 'O' is incorrectly interpreted as a letter instead of '0'.
        Applies the correction only if the word starts with 'O' followed by a valid unit.
        """
        # Split the text into words
        words = text.split()
        
        corrected_words = []

        # Iterate over the words
        for word in words:
            corrected_word = word
            print(f"Processing word: {word}")  # Debug: print word being processed

            # Check if the word starts with 'O' and follows the unit pattern
            if corrected_word.lower().startswith('o'):
                # Check each target unit
                for unit, _ in targets:
                    print(f"Checking if {word} starts with o{unit.lower()}")  # Debug: check each unit
                    # Ensure word has the unit following the 'O'
                    if corrected_word.lower().startswith(f"o{unit.lower()}"):
                        # Replace the leading 'O' with '0' and preserve the rest of the word
                        corrected_word = f"0{corrected_word[1:]}"  # Replace the first 'O' with '0'
                        print(f"Fixed word: {corrected_word}")  # Debug: print the fixed word
                        break  # Stop checking other units once a match is found

            corrected_words.append(corrected_word)

        # Rebuild the corrected text by joining words back together
        corrected_text = " ".join(corrected_words)
        return corrected_text
    
    def normalize_floats_in_text(self, text: str) -> str:
        """
        Normalize malformed float strings like 0..0, .0..0, etc., to standard float form.
        """
        return re.sub(r'(?<!\d)\.?(\d+)[.]+(\d+)(?!\d)', r'\1.\2', text)

    def remove_duplicate_decimal_points_in_float(self, tokens: list[str], max_digits: int = None) -> list[str]:
        cleaned_tokens = []
        for tok in tokens:
            if tok.count('.') > 1 and any(c.isdigit() for c in tok):
                normalized = self.normalize_floats_in_text(tok)
                if max_digits:
                    normalized = re.sub(r'\.(\d+)', lambda m: '.' + m.group(1)[:max_digits], normalized)
                cleaned_tokens.append(normalized)
            else:
                cleaned_tokens.append(tok)
        return cleaned_tokens


    def __check_if_target_sees_leading_zero_as_let_o(self, text: str, targets: list[tuple[str, str]]): ## Edge case #1: If it sees num 0 as let O
        affected_targets = []

        for field_name, alias in targets:
            for line in text.splitlines():
                if alias in line:
                    parts = line.split(alias)
                    if len(parts) > 1:
                        possible_value = parts[1].strip().split()[0]
                        if possible_value.startswith('O') and len(possible_value) > 1 and possible_value[1].isdigit():
                            affected_targets.append(field_name)
                            break

        return affected_targets
    

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