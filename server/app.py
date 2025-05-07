from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import os 

from objects import Version
APP_NAME = "IMAGE YIELDS OUTPUT TEXT"

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

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

uploaded_file_path = None

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/streamProcessImage', methods=['POST'])
def streamProcessImage():
    """Upload file and stream processing immediately."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        def generate():
            yield f"data: {{\"progress\": 0, \"msg\": \"File uploaded, beginning processing...\"}}\n\n"
            yield from sr.streamProcessImage(filename)

        return Response(stream_with_context(generate()), mimetype='text/event-stream')

    return jsonify({'error': 'File not allowed'}), 400

@app.route('/feedback', methods=['POST'])
def feedback():
    """
    Input stream for monitoring.
    If feedback (bool) is set to true, then it means the image and the output matches (good)
    else an edge case is detected (needed for debugging)
    """
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    res = {}
    
    data = request.get_json()

    feedback = data.get('feedback')
    if not feedback:
        return jsonify({'error': 'Feedback cannot be undefined'}), 400

    id = data.get('_id')
    if not id:
        return jsonify({'error': 'Id cannot be undefined'})

    res['picture_and_output_matches'] = feedback
    res['_id'] = id

    message = sr.feedback(id, feedback)
    return jsonify({'message': message, 'data': res}), 200


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)