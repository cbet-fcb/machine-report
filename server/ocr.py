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

class OCR(Image):
    def run_ocr(self) -> dict:
        image = self.load_image()
        if image is None:
            raise ValueError(f'Failed to load image from: {self.path}')

        ocr = PaddleOCR(use_angle_cls=True, lang='en', debug=False, show_log=False)
        ocr_res = ocr.ocr(image, cls=True)
        processed_text = self.process_ocr_output(ocr_res)
        return {"text": processed_text}
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
    test = OCR(path="test1.png")
    print(str(test.run_ocr()))

# def run_ocr(image_input, font_path='C:/Windows/Fonts/arial.ttf', show=True, save_json=True, json_path='ocr_output.json'):
#     image = load_image(image_input)
#     if image is None:
#         raise ValueError(f"Failed to load image from: {image_input}")

#     ocr = PaddleOCR(use_angle_cls=True, lang='en', debug=False, show_log=False)
#     return ocr.ocr(image, cls=True)

#     # import postprocessing
#     # ocr_data = postprocessing.group_text_lines(results=results)
#     # full_text = "\n".join(" ".join(w['text'] for w in line['words']) for line in ocr_data)

#     # ocr_result = postprocessing.ocr_results_to_text(full_text)
#     # print(full_text)

#     # import targets
#     # target = targets.MACHINE_REPORT

#     # keyword_values = postprocessing.extract_text_value(ocr_data, targets=target)

#     # ocr_data = group_text_lines(results=results)

#     # # # Extract keyword values (targeted data only)
#     # keyword_values = extract_keyword_values(ocr_data)

#     # import machinereport
#     # data = machinereport.parse_machine_report(results)
         
#     # if save_json:
#     #     combined = {
#     #         "data": data
#     #     }
#     #     with open(json_path, 'w', encoding='utf-8') as f:
#     #         json.dump(combined, f, ensure_ascii=False, indent=2)
#     #     print(f"✅ OCR results (targeted data) saved to {json_path}")

#     # boxes = [line[0] for line in results[0]]
#     # txts = [line[1][0] for line in results[0]]
#     # scores = [line[1][1] for line in results[0]]
#     # image_with_boxes = draw_ocr(image, boxes, txts, scores, font_path=font_path)
    
#     # if show:
#     #     plt.imshow(cv2.cvtColor(image_with_boxes, cv2.COLOR_BGR2RGB))
#     #     plt.axis('off')
#     #     plt.show()

#     # img_name = os.path.splitext(os.path.basename(image_input))[0]
#     # return {
#     #     "name": img_name,
#     #     "data": data,
#     #     "preview": image_with_boxes  # keep the drawn image in memory
#     # }

# def process_batched_images_to_ocr(image_paths, font_path, save_json=True, json_dir='test'):
#     os.makedirs(json_dir, exist_ok=True)
#     all_results = {}

#     previews = []    
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         futures = []
#         for idx, image_path in enumerate(image_paths):
#             filename = os.path.basename(image_path)
#             extracted_name, _ = os.path.splitext(filename)

#             json_path = os.path.join(json_dir, f"{extracted_name}.json")
#             futures.append(executor.submit(run_ocr,
#                 image_input=image_path,
#                 font_path=font_path,
#                 save_json=save_json,
#                 json_path=json_path,
#                 show=False            # ← disable all GUI calls in worker threads
#             ))

#         for future in concurrent.futures.as_completed(futures):
#             result = future.result()
#             all_results.update({result["name"]: result["data"]})
#             previews.append(result["preview"])

#     return all_results