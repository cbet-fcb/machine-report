import pytest
from textProcessor import Normalizer

@pytest.fixture
def nlp_engine():
    from nlp import NLPEngine
    return NLPEngine()

@pytest.mark.parametrize(
    "text, expected_tokens",
    [
        ("0..0", ["0.0"]),
        (".0..0", ["0.0"]),
        (".0..0.", ["0.0", '.']),
        (".0..0..", ["0.0", '..']),
    ]
)
def test_malformed_floats_are_normalized(nlp_engine, text, expected_tokens):
    normalized_text = Normalizer().normalize_floats_in_text(text)
    output = nlp_engine.handle_text(normalized_text)
    tokens = output["tokens"]
    assert tokens == expected_tokens, f"Expected {expected_tokens}, got {tokens}"
