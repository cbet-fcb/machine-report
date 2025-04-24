import os
import re
from collections import defaultdict


def group_text_lines(results, y_threshold=10):
    """
    Group OCR word boxes into text lines and return a structured list of lines.

    results[0]: iterable of (box, (text, confidence))
    y_threshold: max vertical distance to group words into same line
    Returns: list of dicts {"line_number": int, "words": [{"text": str, "confidence": float}, ...]}
    """
    lines = defaultdict(list)

    for box, (text, confidence) in results[0]:
        center_y = int(sum(pt[1] for pt in box) / 4.0)
        matched_key = next((k for k in lines if abs(k - center_y) <= y_threshold), None)
        key = matched_key if matched_key is not None else center_y
        lines[key].append({"text": text, "confidence": round(confidence, 4)})

    grouped_lines = []
    for idx, (_, words) in enumerate(sorted(lines.items(), key=lambda x: x[0]), start=1):
        grouped_lines.append({"line_number": idx, "words": words})

    return grouped_lines


def parse_machine_report(results):
    """
    Parse raw PaddleOCR results into:
      - bpm, mpm,
      - date components: year, month, day, hour, minute, second,
      - product_count and total_count (two largest 6+ digit numbers at line start).
    """
    grouped = group_text_lines(results)
    text_lines = [" ".join(w["text"] for w in line["words"]) for line in grouped]
    data = {}
    bpm_pat = re.compile(r"(\d+)\s*BPM", re.IGNORECASE)
    mpm_pat = re.compile(r"(\d+)\s*MPM", re.IGNORECASE)
    datetime_pat = re.compile(
        r"(\d{4})\s*(\d{1,2})\s*(\d{1,2})[\s,]+(\d{1,2}):(\d{2}):(\d{2})"
    )
    # Extract bpm, mpm, date/time first
    for line in text_lines:
        if 'bpm' not in data:
            m = bpm_pat.search(line)
            if m: data['bpm'] = int(m.group(1))
        if 'mpm' not in data:
            m = mpm_pat.search(line)
            if m: data['mpm'] = int(m.group(1))
        if not all(k in data for k in ('year','month','day','hour','minute','second')):
            m = datetime_pat.search(line)
            if m:
                data['year']   = int(m.group(1))
                data['month']  = int(m.group(2))
                data['day']    = int(m.group(3))
                data['hour']   = int(m.group(4))
                data['minute'] = int(m.group(5))
                data['second'] = int(m.group(6))
        if all(k in data for k in ('bpm','mpm','year','month','day','hour','minute','second')):
            break
    # Extract product and total counts: 6+ digit numbers at line start
    counts = []
    for line in text_lines:
        m = re.match(r"^(\d{6,})", line)
        if m: counts.append(int(m.group(1)))
    if counts:
        data['product_count'] = min(counts)
        data['total_count']   = max(counts)
    return data

