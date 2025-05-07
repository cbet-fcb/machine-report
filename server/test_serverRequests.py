import os
import json
import pytest
from serverRequests import ServerRequests

test_dir = os.path.join(os.path.dirname(__file__), 'test')
sr = ServerRequests()

def load_groundtruth(image_file):
    base_name = os.path.splitext(image_file)[0]
    json_file = f"{base_name}_groundtruth.json"
    json_path = os.path.join(test_dir, json_file)

    if not os.path.exists(json_path):
        return None

    with open(json_path, 'r') as f:
        return json.load(f)

@pytest.mark.parametrize("image_file", [
    f for f in os.listdir(test_dir) if f.endswith('.jpg')
])
def test_process_stream_image(image_file):
    pass

# def test_machine_report_output_without_id(image_file):
#     image_path = os.path.join(test_dir, image_file)
#     groundtruth = load_groundtruth(image_file)

#     if groundtruth is None:
#         pytest.skip(f"No ground truth for {image_file}")

#     result = sr.processImageToMachineReport(image_path)

#     for key in ['bpm-pcs/min', 'pcs/min']:
#         gt_entry = groundtruth.get(key)
#         result_entry = result.get(key)

#         if gt_entry and result_entry:
#             gt_value = gt_entry.get('value')
#             result_value = result_entry.get('value')

#             assert float(result_value) == float(gt_value), (
#                 f"Mismatch for {key} in {image_file}: expected {gt_value}, got {result_value}"
#             )
#         else:
#             assert gt_entry is None and result_entry is None, (
#                 f"Expected no data for {key} in {image_file}, but got result={result_entry} or groundtruth={gt_entry}"
#             )
