from mongoDb import mongoDb
from dateutil import parser
# import datetime
from utils import *
import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Tuple, Dict, List, Any
from urllib.parse import urlparse
import requests
import numpy as np
import cv2
import base64
import re

db = mongoDb()

class Version:
    def __init__(self, major: int, minor: int, patch: int):
        self.major = major
        self.minor = minor
        self.patch = patch
        pass

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"
    
    @staticmethod
    def unpack_version(version: str) -> tuple[int, int, int]:
        try:
            major, minor, patch = map(int, version.strip().split('.'))
            return major, minor, patch
        except ValueError:
            raise ValueError(f"Invalid version string: '{version}'. Expected format: 'X.Y.Z'")

CURRENT_VERSION = Version(0, 0, 1)

#  MACHINE REPORT BUILDER
#       IMAGE(INPUT STREAM)
#           ||
#          \  /
#           \/
#          OCR (CAN BE SKIP) # Flag
#           ||
#          \  /
#           \/
#        NORMALIZER (CAN BE SKIP) # Flag
#           ||
#          \  /
#           \/
#          NLP<-------TEXT(INPUT STREAM)
#           ||
#          \  /
#           \/
#      TEXTPROCESSOR
#           ||
#          \  /
#           \/
#         OUTPUT

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
    id: str = Field(default_factory=generateRandomString, alias="_id", )
    targets: List[Tuple[str, str]] = Field(..., description="Find the target as value pair")
    input: Dict[str, Any] = Field(..., description="Input as output of NLP")
    output: Dict[str, Any] = Field(default_factory=dict, description="Output as Machine Report")

    @field_validator('input')
    @classmethod
    def validate_nlp_output_keys(cls, value):
        REQUIRED_KEYS = {"unit_info"}
        missing = REQUIRED_KEYS - value.keys()
        if missing:
            raise ValueError(f"Missing required NLP keys: {missing}")
        return value

    
    
class MachineReportInputWrapper(BaseModel):
    image_path : str = Field(default=None, description="supports Path, url")
    raw_text: str = Field(default=None, descriptions="Raw text") 

    def provide_flag(self) -> dict[str, bool]:
        """
        Automatically sets the flags for members that has value in it
        """
        return {k: v is not None for k, v in vars(self).items()}

class MachineReportBuilder:
    def __init__(self, input: MachineReportInputWrapper, list_of_targets: list[tuple[str, str]]):
        self.input_wrapper = input
        self.flags = input.provide_flag()
        self.targets = list_of_targets

    @staticmethod
    def __image_to_unprocessed_text(image_path: str) -> str:
        """
        CONVERT IMAGE TO RAW TEXT (text might be joined inappropriately)
        """
        from ocr import OCREngine
        from imageHandler import ImageHandler
        
        image_handler = ImageHandler(path=image_path)
        image_array = image_handler.load_image()
        if not image_array.any():
            raise ValueError(f'Processing {truncate_string(image_path)} to an image array failed')
        
        res = OCREngine().run_ocr(image_array=image_array)
        if not res:
            raise ValueError('Processing image array to unprocessed text failed')
        
        return res

    @staticmethod
    def __unprocessed_to_processed_text(text: str) -> dict:
        """
        CONVERT RAW TEXT TO PROCESSED TEXT (separation exists)
        """
        from textProcessor import Normalizer
        from nlp import NLPEngine

        if not text:
            raise ValueError('Text should not be empty')
        lower_cased_text = Normalizer().convert_ocr_result_alphabets_to_small_letter(text)
        
        processed_text = NLPEngine().handle_text(lower_cased_text)
        if not processed_text:
            raise ValueError('Processing from lower-cased text to processed-text failed')
        
        return processed_text
    
    @staticmethod
    def __processed_text_to_machine_report(targets: list[tuple[str, str]], nlp_output_as_input: dict[str, any]) -> dict[str, any]:
        """
        CONVERT PROCESSED TEXT TO MACHINE REPORT (check if target exist then paste it)    
        """
        from textProcessor import TextProcessor
        from machineReportHandler import MachineReportHandler

        text_processor = TextProcessor()
        data = text_processor.process_text(nlp_output=nlp_output_as_input)

        mr = MachineReportHandler(targets=targets, input=data)

        return mr.generate_machine_report()
        pass


    def process_image(self) -> dict:
        print('Processing image...')
        res = {}
        
        process_begins_at = datetime.datetime.now()

        first_stage = self.__image_to_unprocessed_text(self.input_wrapper.image_path) 
        
        second_stage = self.__unprocessed_to_processed_text(first_stage)

        third_stage = self.__processed_text_to_machine_report(self.targets, second_stage) 

        res['process_begins_at'] = process_begins_at
        res['unprocessed_text'] = first_stage
        res['processed_text'] = second_stage
        res['machine_report'] = third_stage
        res['process_ends_at'] = datetime.datetime.now()
        res['version'] = Version(0, 0, 1).__str__()
        
        print('Done processing image')
        return res

    def process_text(self) -> dict:
        print('Processing text...')

        res = {}

        process_begins_at = datetime.datetime.now()

        cache_text = self.input_wrapper.raw_text
        first_stage = self.__unprocessed_to_processed_text(cache_text)

        second_stage = self.__processed_text_to_machine_report(self.targets, first_stage)

        res['process_begins_at'] = process_begins_at
        res['unprocessed_text'] = cache_text
        res['processed_text'] = first_stage
        res['machine_report'] = second_stage
        res['process_ends_at'] = datetime.datetime.now()
        res['version'] = Version(0, 0, 1).__str__()

        print('Done processing text')
        return res


    def build(self) -> list[dict]:
        result = []
        if self.flags.get('raw_text'):
            result.append({'source': 'raw_text', **self.process_text()})

        if self.flags.get('image_path'):
            result.append({'source': 'image_path', **self.process_image()})
        
        
        return result

if __name__ == '__main__':
    input = MachineReportInputWrapper(image_path='test/test41.jpg', raw_text='400 pcs/min  asdoadjiowaosd iasdiawjid machine 1')
    mrb = MachineReportBuilder(
        input=input,
        list_of_targets=[
            TargetMaker.make_target("pcs/min"),
            TargetMaker.make_target("bpm", "bpm to pcs/min")
        ]
    )
    res = mrb.build()
    raw_text_output = res[0]
    image_path_output = res[1]
    print("Raw text: ", raw_text_output.get('machine_report'), "\n")
    print("Image path: ",image_path_output.get('machine_report'))
    pass