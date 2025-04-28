from mongoDb import mongoDb
from dateutil import parser
import datetime
from utils import *
import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union, List

db = mongoDb()

class TestModel(BaseModel):
    id: Optional[str] = Field(default=None, alias='_id')
    a: str = Field(default=None, description='testA')
    b: str = Field(default=None, description='testB')
    c: str = Field(default=None, description='testC')
    d: str = Field(default=None, description='testD')
    e: str = Field(default=None, description='testE')
    f: str = Field(default=None, description='testF')

    def print_all(self):
        print(self.a + self.b + self.c + self.d + self.e + self.f)
        pass

    def print_a(self):
        print(self.a)
        pass

    def print_b(self):
        print(self.b)
        pass

    def print_c(self):
        print(self.c)
        pass

    def print_d(self):
        print(self.d)
        pass

    def print_e(self):
        print(self.e)
        pass

    def print_f(self):
        print(self.f)
        pass

class Image(BaseModel):
    id: str = Field(default=lambda: generateRandomString(), alias="_id", description="id")
    path: str = Field(default=None, description="URL of image")

    def is_base64_encoding(self) -> bool:
        return self.path.startswith("data:image/")
    
    def is_url(self) -> bool:
        from urllib.parse import urlparse
        parsed = urlparse(self.path)
        return parsed.scheme in ("http", "https")
    
    def load_image(self) -> any:
        import requests
        import numpy as np
        import cv2
        import base64
        import re

        if self.is_url():
            response = requests.get(self.path)
            image_np = np.asarray(bytearray(response.content), dtype=np.uint8)
            return cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        #TODO: Implement working base64 encoded image
        elif self.is_base64_encoding():
            # Extract base64 string from the Data URL
            base64_str = re.sub('^data:image/.+;base64,', '', self.path)
            image_data = base64.b64decode(base64_str)
            image_np = np.frombuffer(image_data, np.uint8)
            return cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        else:
            return cv2.imread(self.path)

class Text(BaseModel):
    text: str = Field(default=None, description="Text")

    def get_text(self):
        return self.text

if __name__ == '__main__':
    image = Image(path="test1.png")

    data = image.load_image()
    
    print(data)
    pass

