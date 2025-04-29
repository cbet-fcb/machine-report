from imageToText import *
import pytest

def test_image_to_text():
    itth = ImageToTextHandler()
    result = itth.run_image_to_text_handler("../../Automation/test/test60.jpg")
    
    assert 'tokens' in result
    assert 'entities' in result
    assert isinstance(result['tokens'], list)
    assert isinstance(result['entities'], list)