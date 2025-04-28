import os
import json
import argparse
import requests
import numpy as np
from urllib.parse import urlparse
from paddleocr import PaddleOCR, draw_ocr
import cv2
from matplotlib import pyplot as plt
from collections import defaultdict
import re
import concurrent.futures

# === Utility Functions ===

def get_image_paths(input_path: str):
    if os.path.isdir(input_path):
        return [
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'))
        ]
    else:
        return [input_path]


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


def is_url(path: str) -> bool:
    parsed = urlparse(path)
    return parsed.scheme in ("http", "https")


def load_image(input_path: str):
    if is_url(input_path):
        response = requests.get(input_path)
        image_np = np.asarray(bytearray(response.content), dtype=np.uint8)
        return cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    else:
        return cv2.imread(input_path)


# === OCR Functions ===

from rapidfuzz import fuzz

def extract_keyword_values(grouped_lines, target):
    found = {}
    lines = [" ".join([word['text'] for word in line['words']]) for line in grouped_lines]

    # Target phrases
    # 
    # targets = {
    #   "Initial text lookup" : 
    #       {
    #        "stopAtWhat": int | str | (default)any /*This means stop at the initial text lookup*/,
    #        "timeToLive": (e.g.. 10, 20, 40), 
    #        "lookScope": (default)both/*Do i traverse positive indexing or negative indexing*/ | ahead | back,
    #        "findSpecifics": (default)None/*Useful for multiple targets in a single line*/ | ["Initial text lookup": {...}, ...], 
    #       },
    #   ...
    # }

    targets = {
        "Delivery Receipt": "delivery receipt",
        "Total Amount Due": "total amount due",
        "RP": "rp"
    }

    # Match based on fuzzy score
    best_scores = {key: (None, 0, -1) for key in targets}

    for i, line in enumerate(lines):
        for key, phrase in targets.items():
            score = fuzz.partial_ratio(line.lower(), phrase)
            if score > 85 and score > best_scores[key][1]:
                best_scores[key] = (line.strip(), score, i)

    # Extract values
    for key, (line_text, score, idx) in best_scores.items():
        if not line_text:
            continue
        found[key] = line_text

        if key == "Total Amount Due":
            match = re.search(r"[\d,\.]+", line_text)
            if match:
                found[key] = match.group(0)
            elif idx + 1 < len(lines):
                next_line_match = re.search(r"[\d,\.]+", lines[idx + 1])
                if next_line_match:
                    found[key] = next_line_match.group(0)


    for i, line_text in enumerate(lines):
        lower_line = line_text.lower()

        # --- Combined check for line containing both CODE and RP ---
        if "#1-CODE#" in line_text and ("rp" in lower_line or "RP" in line_text):
            # Extract CODE
            code_match = re.search(r"#\d+-CODE#\s*(\w+)", line_text)
            if code_match:
                found["Code"] = code_match.group(1)

            # Extract RP after CODE
            rp_match = re.search(r"RP[ \*\w\-]*", line_text, re.IGNORECASE)
            if rp_match:
                found["RP"] = rp_match.group(0).strip()

        # --- Backup: check for standalone RP if not found yet ---
        if "RP" not in found and fuzz.partial_ratio(lower_line, "rp") > 20:
            rp_match = re.search(r"\bRP[ \*\w\-]*", line_text, re.IGNORECASE)
            if rp_match:
                found["RP"] = rp_match.group(0).strip()

        # --- Backup: check for standalone CODE if not found yet ---
        if "CODE" not in found and "#1-CODE#" in line_text:
            code_match = re.search(r"#\d+-CODE#\s*(\w+)", line_text)
            if code_match:
                found["Code"] = code_match.group(1)


    return found

def run_ocr(image_input, font_path='C:/Windows/Fonts/arial.ttf', show=True, save_json=True, json_path='ocr_output.json'):
    image = load_image(image_input)
    if image is None:
        raise ValueError(f"Failed to load image from: {image_input}")


    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    results = ocr.ocr(image, cls=True)
    

    ocr_data = group_text_lines(results=results)

    # Extract keyword values (targeted data only)
    keyword_values = extract_keyword_values(ocr_data)

    if save_json:
        combined = {
            "keyword_values": keyword_values
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(combined, f, ensure_ascii=False, indent=2)
        print(f"✅ OCR results (targeted data) saved to {json_path}")

    if show:
        boxes = [line[0] for line in results[0]]
        txts = [line[1][0] for line in results[0]]
        scores = [line[1][1] for line in results[0]]
        image_with_boxes = draw_ocr(image, boxes, txts, scores, font_path=font_path)
        plt.imshow(cv2.cvtColor(image_with_boxes, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.show()

    return keyword_values


def process_images_batch(image_paths, font_path, save_json=True, json_dir='test'):
    os.makedirs(json_dir, exist_ok=True)
    all_results = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for idx, image_path in enumerate(image_paths):
            filename = os.path.basename(image_path)
            extracted_name, _ = os.path.splitext(filename)

            json_path = os.path.join(json_dir, f"{extracted_name}.json")
            futures.append(executor.submit(run_ocr, image_input=image_path, font_path=font_path, save_json=save_json, json_path=json_path))

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            all_results.update(result)

    return all_results


# === Main Script ===

def main():
    parser = argparse.ArgumentParser(description='Run PaddleOCR on a local image or URL.')
    parser.add_argument('--image', required=True, help='Path to local image or URL, or directory of images')
    parser.add_argument('--json-dir', default='ocr_output', help='Directory to save output JSON files')
    parser.add_argument('--font', default='C:/Windows/Fonts/arial.ttf', help='Path to .ttf font for drawing')
    parser.add_argument('--no-show', action='store_true', help="Don't display OCR result image")
    args = parser.parse_args()

    image_paths = get_image_paths(args.image)
    print(f"Processing {len(image_paths)} images...")

    # Processing image                  (Preprocessing stage for OCR)  # RUNTIME OPERATION

    process_images_batch(image_paths=image_paths, font_path=args.font, save_json=True, json_dir=args.json_dir)
    
    # Processing text output of OCR     (Postprocessing stage for OCR) # RUNTIME OPERATION

    print("✅ All images processed successfully.")


if __name__ == '__main__':
    main()
