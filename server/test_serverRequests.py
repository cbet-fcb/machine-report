import os
import pytest
import requests
import json

test_dir = "test/machine3"

@pytest.mark.parametrize("image_file", [
    f for f in os.listdir(test_dir) if f.endswith('.jpg')
])
def test_stream_process_image(image_file):
    url = "http://localhost:5000/streamProcessImage"
    filepath = os.path.join(test_dir, image_file)
    
    with open(filepath, 'rb') as f:
        files = {'file': (image_file, f, 'image/jpeg')}
        response = requests.post(url, files=files, stream=True)

        assert response.status_code == 200

        error_found = False
        progress_done_found = False
        progress_updates = []
        final_data = None

        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue
            try:
                # Properly parse JSON; eval can be unsafe
                json_data = json.loads(line[5:].strip())

                if "error" in json_data:
                    error_found = True
                if json_data.get("progress") == 100 or "done" in json_data.get("msg", "").lower():
                    final_data = json_data.get("data", {})

                if "progress" in json_data:
                    progress_updates.append(json_data["progress"])

            except Exception:
                continue

        assert not error_found, "Error was returned in the stream"
        assert progress_updates == [0, 10, 60, 70, 80, 90, 100], "Progress updates are incorrect"

        if final_data and isinstance(final_data, dict):
            pcs_info = final_data.get("pcs/min", {})
            unit = pcs_info.get("unit", "")
            valid_units = {"p", "bpm", "pcs/min"}
            assert unit.lower() in valid_units, f"Invalid unit '{unit}' detected in final output: {pcs_info}"

