from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)
VIDEO_FOLDER = "videos"
ASSIGNMENTS = {}

os.makedirs(VIDEO_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Server is running"

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["video"]
    path = os.path.join(VIDEO_FOLDER, file.filename)
    file.save(path)
    return {"message": "uploaded", "filename": file.filename}

@app.route("/assign", methods=["POST"])
def assign():
    data = request.json
    ASSIGNMENTS[data["device_id"]] = data["video"]
    return {"message": "assigned"}

@app.route("/get-video/<device_id>")
def get_video(device_id):
    if device_id not in ASSIGNMENTS:
        return {"error": "no video"}, 404
    return {"video_url": f"/videos/{ASSIGNMENTS[device_id]}"}

@app.route("/videos/<filename>")
def serve_video(filename):
    return send_from_directory(VIDEO_FOLDER, filename)

import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
