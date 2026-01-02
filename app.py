from flask import Flask, request, send_from_directory
import os
import json

app = Flask(__name__)

# ---------- helpers ----------
def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

# ---------- setup ----------
os.makedirs("videos", exist_ok=True)

# ---------- routes ----------

@app.route("/")
def home():
    return "Server is running"

# 1. Create customer
@app.route("/create-customer", methods=["POST"])
def create_customer():
    customer_id = request.json["customer_id"]

    customers = load_json("customers.json")
    customers[customer_id] = {}

    save_json("customers.json", customers)
    os.makedirs(f"videos/{customer_id}", exist_ok=True)

    return {"message": "customer created"}

# 2. Register device
@app.route("/register-device", methods=["POST"])
def register_device():
    device_id = request.json["device_id"]
    customer_id = request.json["customer_id"]

    devices = load_json("devices.json")
    devices[device_id] = customer_id

    save_json("devices.json", devices)
    return {"message": "device registered"}

# 3. Upload video
@app.route("/upload", methods=["POST"])
def upload():
    customer_id = request.form.get("customer_id")
    file = request.files.get("video")

    if not customer_id or not file:
        return {"error": "missing customer_id or video"}, 400

    # ✅ CREATE FOLDER IF IT DOES NOT EXIST
    os.makedirs(f"videos/{customer_id}", exist_ok=True)

    path = f"videos/{customer_id}/{file.filename}"
    file.save(path)

    return {"message": "uploaded"}


# 4. Assign video to device
assignments = {}

@app.route("/assign", methods=["POST"])
def assign():
    device_id = request.json["device_id"]
    video = request.json["video"]

    assignments[device_id] = video
    return {"message": "assigned"}

# 5. Device fetches video
@app.route("/get-video/<device_id>")
def get_video(device_id):
    devices = load_json("devices.json")

    if device_id not in devices:
        return {"error": "unknown device"}, 404

    if device_id not in assignments:
        return {"error": "no video"}, 404

    customer_id = devices[device_id]
    video = assignments[device_id]

    return {
        "video_url": f"/videos/{customer_id}/{video}"
    }

# 6. Serve video
@app.route("/videos/<customer_id>/<filename>")
def serve_video(customer_id, filename):
    return send_from_directory(f"videos/{customer_id}", filename)

# ---------- run ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

