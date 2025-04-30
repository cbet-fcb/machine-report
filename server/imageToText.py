from ocr import OCR
from nlp import NLP
from textProcessor import TextProcessor, Normalizer
# To instantiate: 
#   path: for Image
#   en_core_type: for NLP

class ImageToTextHandler:
    def __init__(self):
        self.nlp = NLP()
        self.ocr = OCR()
        self.normalizer = Normalizer()
        self.text_processor = TextProcessor()
        pass

    def run_image_to_text_handler(self, path: str) -> dict:
        if not path:
            raise ValueError('Path cannot be "None"') 
        self.ocr.path = path
        
        unprocessed_text = self.ocr.run_ocr()
        all_lower_case_text = self.normalizer.convert_ocr_result_alphabets_to_small_letter(unprocessed_text)
        nlp_handled_dict = self.nlp.handle_text(all_lower_case_text)
        processed_text = self.text_processor.process_text(nlp_handled_dict)
        return processed_text



if __name__ == '__main__':
    itth = ImageToTextHandler()
    count = 0
    path="../../Automation/test/test60.jpg"
    print(f'{count}--------------------------------------{count}')
    print(f'path = {path}')
    count += 1
    key = 'units_info'

    res = itth.run_image_to_text_handler(path=path)
    print(res[key])

    path="../../Automation/test/test70.jpg"
    print(f'{count}--------------------------------------{count}')
    print(f'path = {path}')
    count += 1
    
    res = itth.run_image_to_text_handler(path)
    print(res[key])
    
    path="../../Automation/test/test47.jpg"
    print(f'{count}--------------------------------------{count}')
    print(f'path = {path}')
    count += 1
    res = itth.run_image_to_text_handler(path)
    print(res[key])

    path="../../Automation/test/test58.jpg"
    print(f'{count}--------------------------------------{count}')
    print(f'path = {path}')
    count += 1
    
    res = itth.run_image_to_text_handler(path="../../Automation/test/test58.jpg")
    print(res[key])

    print(f'{count}--------------------------------------{count}')
