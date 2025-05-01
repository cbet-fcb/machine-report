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
    def __init__(self):
        self.ocr_engine = PaddleOCR(use_angle_cls=True, lang='en', debug=False, show_log=False)

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

        # Loop through each line in the OCR result
        for line in ocr_result:
            for word_info in line:
                text = word_info[1][0]  # Extracting the text from the tuple (coordinates, (text, confidence))

                # Ensure text is a string before appending it
                if isinstance(text, str):
                    extracted_text.append(text)
                else:
                    # If text is not a string, convert it to a string or handle it accordingly
                    extracted_text.append(str(text))

        # Join the text into a single string, separated by spaces
        return " ".join(extracted_text)

if __name__ == '__main__':
    test = OCREngine(path="test1.png")
    print(str(test.run_ocr()))