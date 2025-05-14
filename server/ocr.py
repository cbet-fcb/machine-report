from objects import *
from paddleocr import PaddleOCR
import cv2
import os
import json

import requests 
import numpy as np
from urllib.parse import urlparse
from paddleocr import PaddleOCR
import cv2
from matplotlib import pyplot as plt
import concurrent.futures
from utils import *
import math
from collections import defaultdict

from imageHandler import ImageHandler

from collections import defaultdict
from typing import Optional, Any, Tuple

class OCREngine:
    def __init__(self, paddle_ocr_instance: Optional[PaddleOCR] = None):
        """
        A wrapper around the PaddleOCR engine to run OCR on image arrays.

        This class uses PaddleOCR with angle classification enabled and English language support.
        """
        self.ocr_engine = paddle_ocr_instance or PaddleOCR(use_angle_cls=True, lang='en', show_log=False)

    def run_ocr(self, image_array: Any) -> str:
        """
        Run OCR engine and group text into lines.
        """
        ocr_res = self.ocr_engine.ocr(image_array, cls=True)
        return self.process_ocr_output(ocr_res)

    def process_ocr_output(self, ocr_result: list) -> str:
        """
        Process the raw OCR output to group text by lines.
        Returns empty string if nothing is found.
        """
        if not ocr_result:
            return ""

        grouped_lines = self.group_text_lines(ocr_result)
        if not grouped_lines:
            return ""

        try:
            grouped_text = " ".join(
                " ".join(word.get("text", "") for word in line.get("words", []))
                for line in grouped_lines
            )
            return grouped_text.strip()
        except Exception as e:
            # Optionally log the problematic structure
            raise ValueError(f"Failed to format OCR result: {e}")

    def compute_angle(self, box):
        (x1, y1), (x2, y2) = box[0], box[3]
        return math.atan2(y2 - y1, x2 - x1)

    def project_point_onto_angle(self, point, angle):
        x, y = point
        return x * math.cos(angle) + y * math.sin(angle)

    def group_text_lines(self, results, y_threshold=10):
        """
        Group OCR word boxes into text lines with angle-aware projection.
        """
        if not results or not isinstance(results, list) or not results[0]:
            raise ValueError("OCR results are empty or malformed")

        lines = defaultdict(list)

        for item in results[0]:
            if len(item) != 2:
                continue  # skip malformed entries

            box, (text, confidence) = item

            if not text:
                continue  # skip empty text

            try:
                angle = self.compute_angle(box)
                center = tuple(sum(p[i] for p in box) / 4.0 for i in (0, 1))
                projected_y = self.project_point_onto_angle(center, angle)

                matched_key = next((k for k in lines if abs(k - projected_y) <= y_threshold), None)
                key = matched_key if matched_key is not None else projected_y

                lines[key].append({
                    "text": text,
                    "confidence": round(confidence, 4)
                })
            except Exception as e:
                print(f"Skipping malformed box: {e}")
                continue

        grouped_lines = []
        for idx, (_, words) in enumerate(sorted(lines.items(), key=lambda x: x[0]), start=1):
            grouped_lines.append({"line_number": idx, "words": words})

        return grouped_lines


if __name__ == '__main__':
    test = OCREngine()
    test_image = "test1.png"
    image = cv2.imread(test_image)
    print(test.run_ocr(image))
