from mongoDb import mongoDb
from dateutil import parser
# import datetime
from utils import *
import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Tuple, Dict, List
from urllib.parse import urlparse
import requests
import numpy as np
import cv2
import base64
import re

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
    id: str = Field(default_factory=generateRandomString, alias="_id", description="id")
    path: str = Field(default=None, description="Path, URL, or base64 of image")

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

class TargetMaker:
    @staticmethod
    def make_target(unit_name: str, alias: str = "") -> Tuple[str, str]:
        """
        If alias is "", the alias will be the unit_name
        """
        if not unit_name:
            raise ValueError('Unit name or alias must not be empty')
        return unit_name, alias or unit_name

class MachineReport(BaseModel):
    targets: List[Tuple[str, str]] = Field(..., description="Find the target as value pair")
    nlp_output: Dict = Field(..., description="NLP Output")


    @field_validator('nlp_output')
    @classmethod
    def validate_nlp_output_keys(cls, value):
        REQUIRED_KEYS = {"tokens", "entities", "units_info"}
        missing = REQUIRED_KEYS - value.keys()  
        if missing:
            raise ValueError(f"Missing required NLP keys: {missing}")
        return value

    def does_targets_exist(self) -> List[str]:
        found = []
        for unit, alias in self.targets:
            if any(p['unit'] == unit for p in self.nlp_output.get('units_info', {}).get('unit_pairs', [])):
                found.append(alias)
        return found

    def get_unit_pair(self) -> List[Dict[str, str]]:
        return self.nlp_output.get("units_info", {}).get("unit_pairs", [])

    def get_value(self) -> List[str]:
        return [p['value'] for p in self.get_unit_pair()]

    def generate_machine_report(self) -> Dict[str, Dict]:
        result = {}
        for unit, alias in self.targets:
            for pair in self.get_unit_pair():
                if pair["unit"] == unit:
                    result[alias] = pair
                    break
        return result

if __name__ == '__main__':
    report = MachineReport(
        targets=[TargetMaker.make_target("pcs/min", "")],
        nlp_output={
            "tokens": ["Speed", "200", "pcs/min"],
            "entities": [],
            "units_info": {
                "annotations": [("200", "WORD"), ("pcs/min", "UNIT")],
                "unit_pairs": [{"value": "200", "unit": "pcs/min"}]
            }
        }
    )
    print(report.generate_machine_report())

