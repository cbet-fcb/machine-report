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

from ocr import OCREngine
from imageHandler import ImageHandler
from nlp import NLPEngine
from textProcessor import Normalizer, TextProcessor
from machineReportHandler import MachineReportHandler

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

#  MACHINE REPORT BUILDER
#       IMAGE(INPUT STREAM)
#           ||
#          \  /
#           \/
#          OCR
#           ||
#          \  /
#           \/
#        NORMALIZER 
#           ||
#          \  /
#           \/
#          NLP
#           ||
#          \  /
#           \/
#     TEXT PROCESSOR
#           ||
#          \  /
#           \/
#     MACHINE REPORT
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
            raise ValueError('Unit name or alias must not be empty. If error persists, please add a feedback.')
        if alias == "":
            alias = unit_name
        return unit_name, alias

class TimerUtils:
    @staticmethod
    def make_timer(hour: float, minute: float, second: float) -> Tuple[int, int, float]:
        """
        Normalize overflowing time into a (h, m, s) tuple, clamped to 24 hours max.
        """
        total_seconds = hour * 3600 + minute * 60 + second

        if total_seconds >= 86400:
            raise ValueError("Interval cannot exceed 24 hours.")

        h = int(total_seconds // 3600)
        total_seconds %= 3600
        m = int(total_seconds // 60)
        s = round(total_seconds % 60, 6)

        return h, m, s

    @staticmethod
    def normalize_to_interval(dt: datetime.datetime, interval: datetime.timedelta) -> datetime:
        """
        Snap the given datetime to the start of the nearest interval, in Philippine Time (UTC+8).
        """
        # Set Philippine Time Zone (UTC+8)
        pht = datetime.timezone(datetime.timedelta(hours=8))
        
        # Ensure the datetime is in PHT (if not already aware)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=pht)  # Make it aware if it's naive
        
        # Ensure epoch is in PHT
        epoch = datetime.datetime(1970, 1, 1, tzinfo=pht)
        
        # Calculate the number of seconds since the epoch
        seconds_since_epoch = (dt - epoch).total_seconds()
        interval_seconds = interval.total_seconds()
        
        # Snap to the nearest interval
        snapped_seconds = (seconds_since_epoch // interval_seconds) * interval_seconds
        
        # Return the snapped time in PHT
        return epoch + datetime.timedelta(seconds=snapped_seconds)

class MachineReportInputWrapper(BaseModel):
    image_path : str = Field(default=None, description="supports Path, url")
    raw_text: str = Field(default=None, descriptions="Raw text") 

    def provide_flag(self) -> dict[str, bool]:
        return {k: v is not None for k, v in vars(self).items()}

class MachineReportBuilder:
    def __init__(
        self, 
        input: MachineReportInputWrapper, 
        list_of_targets: list[tuple[str, str]],
        version: Version = Version(0, 0, 1),
        image_handler: Optional[ImageHandler] = None, 
        ocr_engine: Optional[OCREngine] = None,
        nlp_engine: Optional[NLPEngine] = None,
        normalizer: Optional[Normalizer] = None,
        text_processor: Optional[TextProcessor] = None,
        machine_report_handler: Optional[MachineReportHandler] = None,
    ):
        self.input_wrapper = input
        self.flags = self.input_wrapper.provide_flag()
        if not any(self.flags.values()):
            raise ValueError("Either 'image_path' or 'raw_text' must be provided. If error persists, please add a feedback.")

        
        self.version = version
        if self.flags.get('image_path'):
            self.ocr_engine = ocr_engine or OCREngine()
            self.image_handler = image_handler or ImageHandler()
        self.nlp_engine = nlp_engine or NLPEngine()
        self.normalizer = normalizer or Normalizer()
        self.text_processor = text_processor or TextProcessor()
        self.machine_report_handler = machine_report_handler or MachineReportHandler()
        
        if not list_of_targets:
            raise ValueError('Must have targets') 
        self.machine_report_handler.add_targets(list_of_targets)

    def image_to_unprocessed_text(self, image_path: str) -> str:
        """
        Converts an image to raw OCR text. The raw text may have inappropriate joins, 
        hence the naming (unprocessed).

        Args:
            image_path (str): The path to the image file to be processed.

        Returns:
            str: The raw OCR text extracted from the image.

        Raises:
            ValueError: If the image path is empty, the image fails to load, 
                        or OCR processing fails.
        """
        if not image_path.strip():
            raise ValueError('No image is given. If error persists, please add a feedback.')
            
        image_array = self.image_handler.load_image(image_path)
        if not image_array.any():
            raise ValueError(f'It cannot load the image, please send image-formatted file (jpg/jpeg, png, etc.). If error persists, please add a feedback.')
        
        res = self.ocr_engine.run_ocr(image_array=image_array)
        if res == "":
            raise ValueError('The captured image shows no text. If error persists, please add a feedback.')
        
        return res

    def unprocessed_to_processed_text(self, text: str) -> dict:
        """
        CONVERT RAW TEXT TO PROCESSED TEXT (separating joined text happens here)
        """
        if not text:
            raise ValueError('No text is given. If error persists, please add a feedback.')
        
        processed_text = self.nlp_engine.handle_text(text)
        if not processed_text or not processed_text.get("tokens"):
            raise ValueError('The system cannot discern any useful data of the image provided. If error persists, please add a feedback.')
        
        return processed_text
    
    def processed_text_to_machine_report(self, targets: list[tuple[str, str]], nlp_output_as_input: dict[str, any]) -> dict[str, any]:
        """
        CONVERT PROCESSED TEXT TO MACHINE REPORT (get the targets)    
        """
        if not nlp_output_as_input or 'tokens' not in nlp_output_as_input:
            raise ValueError("The system cannot discern any useful data of the image provided. If error persists, please add a feedback.")

        data = self.text_processor.process_text(nlp_output=nlp_output_as_input)

        return self.machine_report_handler.generate_machine_report(data)
        pass

    
    @deprecated('use image_to_unprocessed_text -> unprocessed_to_processed_text -> processed_text_to_machine_report')
    def process_image(self) -> dict:
        print('Processing image...')
        res = {}
        
        process_begins_at = datetime.datetime.now()

        first_stage = self.image_to_unprocessed_text(self.input_wrapper.image_path) 
        
        second_stage = self.unprocessed_to_processed_text(first_stage)

        third_stage = self.processed_text_to_machine_report(self.targets, second_stage) 

        res['process_begins_at'] = process_begins_at
        res['unprocessed_text'] = first_stage
        res['processed_text'] = second_stage
        res['machine_report'] = third_stage
        res['process_ends_at'] = datetime.datetime.now()
        res['version'] = Version(0, 0, 1).__str__()
        
        print('Done processing image')
        return res

    @deprecated('use unprocessed_to_processed_text -> processed_text_to_machine_report')
    def process_text(self) -> dict:
        print('Processing text...')

        res = {}

        process_begins_at = datetime.datetime.now()

        cache_text = self.input_wrapper.raw_text
        first_stage = self.unprocessed_to_processed_text(cache_text)

        second_stage = self.processed_text_to_machine_report(self.targets, first_stage)

        res['process_begins_at'] = process_begins_at
        res['unprocessed_text'] = cache_text
        res['processed_text'] = first_stage
        res['machine_report'] = second_stage
        res['process_ends_at'] = datetime.datetime.now()
        res['version'] = Version(0, 0, 1).__str__()

        print('Done processing text')
        return res

    @deprecated('use image_to_unprocessed_text -> unprocessed_to_processed_text -> processed_text_to_machine_report')
    def build(self) -> list[dict]:
        result = []
        if self.flags.get('raw_text'):
            result.append({'source': 'raw_text', **self.process_text()})

        if self.flags.get('image_path'):
            result.append({'source': 'image_path', **self.process_image()})
        
        
        return result

if __name__ == '__main__':
    val = TimerUtils.normalize_to_interval(dt=datetime.datetime(), interval=datetime.timedelta(minutes=30))
    print(val)
    pass