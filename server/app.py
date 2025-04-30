from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from serverRequests import ServerRequests
sr = ServerRequests()

@app.route('/processImageToMachineReport', methods=['POST'])
def processImageToMachineReport():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    data = request.get_json(silent=True)
    if not data or 'path' not in data:
        return jsonify({'error': 'JSON must include a "path" key'}), 400

    image_path = data['path']
    try:
        result = sr.processImageToMachineReport(image_path)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
