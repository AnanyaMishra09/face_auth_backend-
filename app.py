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

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Enable Cross-Origin Resource Sharing to allow frontend communication
CORS(app)

# --- Initialize Supabase Client ---
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# --- JWT & Admin Configuration ---
JWT_SECRET = os.environ.get("JWT_SECRET")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

# --- Helper Function to process images ---
def process_base64_image(base64_string):
    """Decodes a base64 string and returns a face encoding."""
    # The string might come with a prefix "data:image/jpeg;base64,", remove it
    if "," in base64_string:
        base64_string = base64_string.split(',')[1]
    
    try:
        decoded_data = base64.b64decode(base64_string)
        image_stream = io.BytesIO(decoded_data)
        pil_image = Image.open(image_stream)
        
        # Convert PIL image to numpy array for face_recognition
        image_np = np.array(pil_image)
        
        # Find face locations and encodings
        face_locations = face_recognition.face_locations(image_np)
        if not face_locations:
            return None # No face found
            
        face_encodings = face_recognition.face_encodings(image_np, face_locations)
        return face_encodings[0] # Return the encoding of the first face found
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

# --- API Routes ---

## 1. Registration Route
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    photos = data.get("photos") # List of base64 strings

    if not all([name, email, photos]):
        return jsonify({"error": "Missing required fields."}), 400

    encodings = []
    for photo_b64 in photos:
        encoding = process_base64_image(photo_b64)
        if encoding is not None:
            encodings.append(encoding)
    
    if not encodings:
        return jsonify({"error": "No faces could be detected in the provided photos."}), 400

    # Average the encodings to get a more robust representation
    avg_encoding = np.mean(encodings, axis=0).tolist() # Convert to list for JSON serialization

    try:
        # Insert user data into Supabase
        user_data, count = supabase.table('users').insert({
            "name": name,
            "email": email,
            "phone": phone,
            "face_encoding": avg_encoding
        }).execute()

    except Exception as e:
        # This handles potential database errors, like a duplicate name or email
        return jsonify({"error": f"Could not register user. Error: {e}"}), 500

    return jsonify({"message": "User registered successfully!"}), 201


## 2. Login Step 1: Find User
@app.route("/find-user", methods=["POST"])
def find_user():
    data = request.get_json()
    name = data.get("name")
    
    if not name:
        return jsonify({"error": "Username is required."}), 400
        
    response = supabase.table('users').select("name").eq('name', name).execute()
    
    if not response.data:
        return jsonify({"error": "User not found."}), 404
        
    return jsonify({"message": "User found. Proceed with face verification."}), 200

## 3. Login Step 2: Verify Face and Get Token
@app.route("/verify-face", methods=["POST"])
def verify_face():
    data = request.get_json()
    name = data.get("name")
    photo_b64 = data.get("photo")

    if not all([name, photo_b64]):
        return jsonify({"error": "Username and photo are required."}), 400

    # Get the user's stored encoding from the database
    response = supabase.table('users').select("face_encoding").eq('name', name).execute()
    if not response.data:
        return jsonify({"error": "User not found."}), 404
    
    stored_encoding_list = response.data[0]['face_encoding']
    stored_encoding = np.array(stored_encoding_list)

    # Process the live photo
    live_encoding = process_base64_image(photo_b64)
    if live_encoding is None:
        return jsonify({"error": "No face detected in the provided image."}), 400

    # NEW, STRICTER LINE
    is_match = face_recognition.compare_faces([stored_encoding], live_encoding, tolerance=0.4)[0]
    
    if is_match:
        # Generate JWT token
        payload = {
            'name': name,
            'exp': datetime.utcnow() + timedelta(hours=24) # Token expires in 24 hours
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return jsonify({"message": "Login successful!", "token": token, "user": {"name": name}}), 200
    else:
        return jsonify({"error": "Face verification failed. Please try again."}), 401

## 4. Admin Login
@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        payload = {
            'role': 'admin',
            'exp': datetime.utcnow() + timedelta(hours=8)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return jsonify({"message": "Admin login successful!", "token": token}), 200
    else:
        return jsonify({"error": "Invalid admin credentials."}), 401


if __name__ == "__main__":
    app.run(debug=True, port=5001)
