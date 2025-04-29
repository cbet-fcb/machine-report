import pytest
from ocr import *

def test_ocr():
    test = OCR(path="test1.png").run_ocr()
    assert test is not (not None)