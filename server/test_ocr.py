import pytest
from ocr import *

ground_truth = {

}

def test_ocr():
    test = OCR(path="test1.png").run_ocr()
    expected_text = 'OCR results'
    actual_text, confidence = test[0][0][1] # This is stu... nice

    assert actual_text == expected_text, f"Expected '{expected_text}', but got '{actual_text}'"
    assert confidence >= 0.9, f"Expected confidence score to be greater than 0.9, but got a score of {confidence}"
