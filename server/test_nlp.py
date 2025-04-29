from nlp import *
import pytest

import pytest
from nlp import NLP

# Create a fixture for reusable NLP instance
@pytest.fixture
def nlp_engine():
    return NLP(en_core_type="en_core_web_lg")

@pytest.mark.parametrize(
    "text, expected_count",
    [
        ("Hello world!", 3),
        ("Apple is buying a startup.", 6),
        ("Test driven development is important.", 6),
    ]
)
def test_tokens_is_equal_to_count_of_words(nlp_engine, text, expected_count):
    output = nlp_engine.handle_text(text)
    assert len(output["tokens"]) == expected_count

def test_entity_cardinal_exists(nlp_engine):
    text = "There are 3 apples on the table."
    output = nlp_engine.handle_text(text)

    entity_labels = [label for _, label in output["entities"]]
    assert "CARDINAL" in entity_labels
