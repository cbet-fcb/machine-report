from pydantic import BaseModel, Field
from utils import *
from urllib.parse import urlparse
from typing import Optional
import cv2
import requests
import re
import numpy as np
import base64

from objects import CURRENT_VERSION

class ImageHandler(BaseModel):
    id: str = Field(default_factory=generateRandomString, alias="_id", description="ID")
    path: str = Field(..., description="Supports rel/abs path, url")
    version: int = Field(default=CURRENT_VERSION, alias="_version", description="Backward compatibility")

    def is_base64_encoding(self) -> bool:
        return self.path.startswith("data:image/")

    def is_url(self) -> bool:
        parsed = urlparse(self.path)
        return parsed.scheme in ("http", "https")

    def load_image(self) -> Optional[np.ndarray]:
        try:
            if self.is_url():
                response = requests.get(self.path)
                response.raise_for_status()
                image_np = np.asarray(bytearray(response.content), dtype=np.uint8)
                return cv2.imdecode(image_np, cv2.IMREAD_COLOR)

            elif self.is_base64_encoding():
                base64_str = re.sub('^data:image/.+;base64,', '', self.path)
                image_data = base64.b64decode(base64_str)
                image_np = np.frombuffer(image_data, np.uint8)
                return cv2.imdecode(image_np, cv2.IMREAD_COLOR)

            else:
                return cv2.imread(self.path)

        except Exception as e:
            print(f"[Error] Failed to load image: {e}")
            return None
