# FaceAuth Backend 🚀

This repository contains the backend server for **FaceAuth**, a modern, passwordless authentication system that uses facial recognition.  
Built with **Python, Flask, and the face-recognition library**, this API handles user registration, face encoding, and secure verification.

---

## ✨ Features
- **Passwordless Authentication**: Securely register and log in using only your face.  
- **Face Encoding**: Converts user photos into unique 128-d vectors for secure storage and comparison.  
- **High-Accuracy Matching**: Strict tolerance level (0.4) ensures accurate differentiation between users.  
- **Secure JWT Issuance**: Issues JSON Web Tokens upon successful verification for session management.  
- **Scalable Database**: Uses **Supabase (PostgreSQL)** for reliable, scalable data storage.  
- **Ready for Deployment**: Preconfigured for free deployment on platforms like **Render**.  

---

## 🛠️ Tech Stack
- **Framework**: Flask  
- **Database**: Supabase (PostgreSQL)  
- **Computer Vision**: face-recognition (dlib)  
- **Authentication**: PyJWT  
- **WSGI Server**: Gunicorn  
- **Deployment**: Render  

---

## 📡 API Endpoints
All endpoints expect and return **JSON**.

| Method | Endpoint       | Description                                                                 |
|--------|---------------|-----------------------------------------------------------------------------|
| POST   | `/register`    | Creates a new user. Expects `name`, `email`, `phone`, and an array of base64 photos. |
| POST   | `/find-user`   | Checks if a user exists in the database. Expects a `name`.                  |
| POST   | `/verify-face` | Verifies a user's identity. Expects a `name` and a single base64 photo. Returns a **JWT** on success. |
| POST   | `/admin/login` | Admin login with email and password.                                        |

---

## ⚙️ Setup and Local Installation

### 1. Clone the Repository
```bash
git clone https://github.com/AnanyaMishra09/face_auth_backend-.git
cd face_auth_backend-
2. Create and Activate a Virtual Environment
bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Configure Environment Variables
Create a .env file in the root directory and add the following:

env
Copy
Edit
# Supabase project URL
SUPABASE_URL="https://your-project-id.supabase.co"

# Supabase anon (public) key
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV5b2xkdWx5YW9uZXRiaXdybmlhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU1MjkyODAsImV4cCI6MjA3MTEwNTI4MH0.XvJ73CXThVHXSaUvDTLosR5XV_RCutwcP49A_kCgdf0"

# Secret string for JWT signing
JWT_SECRET="abcdefghijklmnopqrstuvwxyz"

# Admin credentials
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="@Admin1234"
5. Run the Server
bash
Copy
Edit
flask run --port 5001
The API will now be running at:
👉 http://127.0.0.1:5001

🔑 Configuration
Supabase: Required for database storage.

JWT_SECRET: Ensure this is a long, random string for strong security.

Admin Login: Configurable via .env.
