from collections import defaultdict
from rapidfuzz import fuzz
import re



def group_text_lines(results, y_threshold=10):
    lines = defaultdict(list)

    for line in results[0]:
        box, (text, confidence) = line
        center_y = sum([point[1] for point in box]) / 4.0
        center_y = int(center_y)

        matched_line = None
        for key in lines:
            if abs(key - center_y) <= y_threshold:
                matched_line = key
                break

        if matched_line is not None:
            lines[matched_line].append({"text": text, "confidence": round(confidence, 4)})
        else:
            lines[center_y].append({"text": text, "confidence": round(confidence, 4)})

    sorted_lines = sorted(lines.items(), key=lambda x: x[0])

    return [
        {"line_number": idx + 1, "words": line}
        for idx, (_, line) in enumerate(sorted_lines)
    ]

def ocr_results_to_csv(results):
    lines = []
    for line in results:
        if not line: continue
        text_line = " ".join(lines[0])

def ocr_results_to_text(results):
    lines = []
    for line in results:
        if not line: continue
        text_line = " ".join(lines[0])
        lines.append(text_line)
    return "\n".join(lines)

def make_target(
    target,                  # list of lookup keys (required)
    lookup=None,             # list of lookup keys (default = target)
    ttl=0,                   # time-to-live in lines
    repeat=0,                # how many times to repeat lookup
    traversalMethod="both",  # "both" | "ahead" | "back"
    grouped=False,           # group until newline only if True
    findSpecific=None,       # nested targets
    depth=0,                 # recursion depth
    title=None,              # optional key for output
    exact=False,             # exact match flag
):
    """
    Construct and return a target (key, meta) where:
      - 'lookup' is a list of terms to match in sequence
      - numericType: if lookup items are int/float, extract numeric values
    """
    # Determine lookup sequence
    lookup = lookup or target
    numericType = None
    # Detect numeric lookups
    if all(isinstance(item, (int, float)) for item in lookup):
        numericType = type(lookup[0])
        lookup = [str(item) for item in lookup]
        exact = True

    # Normalize nested specifics
    if findSpecific is None:
        specifics = {}
    else:
        if not isinstance(findSpecific, list):
            findSpecific = [findSpecific]
        specifics = dict(findSpecific)

    meta = {
        "target":         target,
        "lookup":         lookup,
        "numericType":    numericType,
        "timeToLive":     ttl,
        "repeat":         repeat,
        "traversalMethod":traversalMethod,
        "grouped":        grouped,
        "findSpecifics":  specifics,
        "depth":          depth,
        "title":          title,
        "exact":          exact,
    }
    key = title or (target[0] if isinstance(target, (list, tuple)) else target)
    return key, meta


def extract_text_value(grouped_lines, targets):
    """
    Extract values by matching 'lookup' terms in each target, sequentially.
    """
    lines = [" ".join(w['text'] for w in line['words']) for line in grouped_lines]
    best_hits = {k: (None, 0, -1) for k in targets}
    for i, line in enumerate(lines):
        low = line.lower()
        for k, meta in targets.items():
            for term in meta['lookup']:
                term_str = str(term).lower()
                if meta.get('exact'):
                    score = 100 if term_str in low else 0
                else:
                    score = fuzz.partial_ratio(low, term_str)
                if score > best_hits[k][1]:
                    best_hits[k] = (line, score, i)

    found = {}
    for k, meta in targets.items():
        raw_line, score, idx = best_hits[k]
        if not raw_line:
            continue
        out_key = meta.get('title') or k
        # 1) Extract substring after first lookup term
        substr = raw_line
        first = str(meta['lookup'][0])
        pos = substr.lower().find(first.lower())
        if pos >= 0:
            substr = substr[pos + len(first):].strip()
        # 2) For each subsequent lookup term, cut off at that term
        for term in meta['lookup'][1:]:
            t = str(term)
            p = substr.lower().find(t.lower())
            if p >= 0:
                substr = substr[:p].strip()
                break
        # 3) Numeric extraction if needed
        numType = meta.get('numericType')
        if numType:
            pat = r"\d+" if numType is int else r"\d+\.?\d*"
            m = re.search(pat, substr)
            if m:
                try:
                    found[out_key] = numType(m.group())
                    continue
                except:
                    pass
        # 4) Default: full substring
        found[out_key] = substr
        # 5) Handle nested
        for sk, sm in meta.get('findSpecifics', {}).items():
            nested = extract_text_value(grouped_lines, {sk: sm})
            found.update(nested)
    return found


def extract_value_with_limit(lines, idx, stop_at, ttl, scope):
    import re
    def extract_by_type(text, et):
        pattern = r"\d+" if et is int else r"[\d,]*\.?\d*"
        match = re.search(pattern, text)
        if not match:
            return None  # Explicitly return None if nothing is found
        number = match.group(0).replace(',', '')
        try:
            return et(number)
        except:
            return None

    def matches_stop(text):
        if stop_at == 'any':
            return True
        if isinstance(stop_at, str):
            return stop_at.lower() in text.lower()
        if stop_at in (int, float):
            num = extract_by_type(text, stop_at)
            if not num:
                return False
            try:
                _ = type(stop_at)(num.replace(',', '')) 
                return True
            except:
                return False
        return False
    directions = []
    if scope in ('ahead', 'both'):
        directions.append(1)
    if scope in ('back', 'both'):
        directions.append(-1)
    for d in directions:
        pos, steps = idx, 0
        while 0 <= pos < len(lines) and (ttl is None or steps < ttl):
            line = lines[pos]
            if matches_stop(line):
                if stop_at in (int, float):
                    value = extract_by_type(line, type(stop_at))
                    if value is not None:
                        return value
                m = re.search(r"[\d,\.]+", line)
                return m.group(0) if m else line
            pos += d
            steps += 1
    return lines[idx]

if __name__ == '__main__':
    pass