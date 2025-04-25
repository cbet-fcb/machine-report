from pydantic import BaseModel, Field
from ocr import *

class OCRResultFilterer(BaseModel):
    
    pass

class OCRHandler(OCR):
    text_data: str = Field(default=None, description="Unfiltered data from OCR")
    # Run first (to get the value)

    def handleOCRTextData(self) -> dict:
        ocr_result = self.run_ocr()
        lines = []
        for region in ocr_result:
            for line in region:
                text = line[1][0]  # line = [ [box], [text, confidence] ]
                lines.append(text)

        self.text_data = "\n".join(lines)
        return {
            "text_data": self.text_data
        }
    
    def filterTextData(self) -> dict:
        
        pass

if __name__ == '__main__':
    handler = OCRHandler(path='test1.png').handleOCRTextData()
    print(handler['text_data'])
    pass