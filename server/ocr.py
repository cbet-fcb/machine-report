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

from imageHandler import ImageHandler

class OCREngine:
    def __init__(self, paddle_ocr_instance: Optional[PaddleOCR] = None):
        """
        A wrapper around the PaddleOCR engine to run OCR on image arrays.

        This class uses PaddleOCR with angle classification enabled and English language support.

        Side Effects:
        -------------
        - On the first run, PaddleOCR will automatically download pretrained detection and recognition models 
        to the default cache directory (typically ~/.paddleocr or ~/.paddle).
        - This behavior can be controlled by explicitly passing model directories via `det_model_dir` and `rec_model_dir`.

        Notes:
        ------
        - To eliminate download behavior in production environments or tests, consider pre-downloading the models 
        and pointing PaddleOCR to the correct paths.
        - All inputs must be numpy image arrays (e.g., as returned by cv2 or PIL).

        Example:
        --------
            ocr = OCREngine()
            text = ocr.run_ocr(image_array)
        """
        self.ocr_engine = paddle_ocr_instance or PaddleOCR(use_angle_cls=True, lang='en', show_log=False)

    def run_ocr(self, image_array: Any) -> str:
        """
        Run ocr engine
        """
        ocr_res = self.ocr_engine.ocr(image_array, cls=True)
        
        return self.process_ocr_output(ocr_res)
        
    def process_ocr_output(self, ocr_result: list) -> str:
        """
        Process the raw OCR output to prepare text for NLP tasks.
        - Extract text
        - Clean up unwanted characters
        - Combine the text into a single string
        """
        extracted_text = []

        for line in ocr_result:
            for word_info in line:
                text = word_info[1][0]  # Extracting the text from the tuple (coordinates, (text, confidence))

                if isinstance(text, str):
                    extracted_text.append(text)
                else:
                    extracted_text.append(str(text))

        return " ".join(extracted_text)

if __name__ == '__main__':
    test = OCREngine(path="test1.png")
    print(str(test.run_ocr()))