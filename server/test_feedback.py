import requests
import pytest
import json

# The URL of your local Flask server
url = "http://localhost:5000/feedback"

# Sample data to be sent in the POST request
payload = {
    "_id": "681c0c1499ce0e627e3be2d6",  # Replace with a valid _id if necessary
    "feedback": True
}

# Expected response from the Flask server
expected_response = {
    "message": "Feedback successfully received",
    "data": payload
}

# Test function to post feedback

def test_post_feedback():
    url = "http://localhost:5000/feedback"

    response = requests.post(url, json=payload)
    
    assert response.status_code == 200
    assert "message" in response.json()
