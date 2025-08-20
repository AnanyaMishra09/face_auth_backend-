# The simpler app.py without liveness detection

import os
import base64
import io
import numpy as np
import jwt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
from PIL import Image
import face_recognition

load_dotenv()
app = Flask(__name__)
CORS(app)

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
JWT_SECRET = os.environ.get("JWT_SECRET")

def process_base64_image(base64_string):
    if "," in base64_string:
        base64_string = base64_string.split(',')[1]
    try:
        decoded_data = base64.b64decode(base64_string)
        image_stream = io.BytesIO(decoded_data)
        pil_image = Image.open(image_stream)
        image_np = np.array(pil_image)
        face_locations = face_recognition.face_locations(image_np)
        if not face_locations:
            return None
        face_encodings = face_recognition.face_encodings(image_np, face_locations)
        return face_encodings[0]
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    photos = data.get("photos")
    encodings = []
    for photo_b64 in photos:
        encoding = process_base64_image(photo_b64)
        if encoding is not None:
            encodings.append(encoding)
    if not encodings:
        return jsonify({"error": "No faces detected."}), 400
    avg_encoding = np.mean(encodings, axis=0).tolist()
    try:
        supabase.table('users').insert({
            "name": data.get("name"), "email": data.get("email"), "phone": data.get("phone"), "face_encoding": avg_encoding
        }).execute()
    except Exception as e:
        return jsonify({"error": f"Could not register user. Error: {e}"}), 500
    return jsonify({"message": "User registered successfully!"}), 201

@app.route("/find-user", methods=["POST"])
def find_user():
    data = request.get_json()
    name = data.get("name")
    response = supabase.table('users').select("name").eq('name', name).execute()
    if not response.data:
        return jsonify({"error": "User not found."}), 404
    return jsonify({"message": "User found."}), 200

@app.route("/verify-face", methods=["POST"])
def verify_face():
    data = request.get_json()
    name = data.get("name")
    photo_b64 = data.get("photo")
    response = supabase.table('users').select("face_encoding").eq('name', name).execute()
    if not response.data:
        return jsonify({"error": "User not found."}), 404
    stored_encoding = np.array(response.data[0]['face_encoding'])
    live_encoding = process_base64_image(photo_b64)
    if live_encoding is None:
        return jsonify({"error": "No face detected."}), 400
    is_match = face_recognition.compare_faces([stored_encoding], live_encoding, tolerance=0.4)[0]
    if is_match:
        payload = {'name': name, 'exp': datetime.utcnow() + timedelta(hours=24)}
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return jsonify({"message": "Login successful!", "token": token}), 200
    else:
        return jsonify({"error": "Face verification failed."}), 401

if __name__ == "__main__":
    app.run(debug=True, port=5001)
