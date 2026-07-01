from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
import uuid 
import io
import base64
import numpy as np
from PIL import Image
import os

import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array

app = Flask(__name__)
# Replace your current CORS line with this:
CORS(app, resources={r"/api/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])

DB_PATH = "database/verte.db"

print("Loading TensorFlow MobileNetV2 Model...")

# Replace with the actual path to your saved model file (.h5, .keras, or folder path)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, '..', 'AI_model', 'scripts', 'verte_model.keras')
MODEL = tf.keras.models.load_model(MODEL_PATH)

# CRITICAL: These must match the exact alphabetical order of the folders 
# your model was trained on! Update these to match your dataset.
CLASS_NAMES = ['battery', 'biological', 'brown-glass', 'cardboard', 'clothes', 'glass', 'green-glass', 'metal', 'paper', 'plastic', 'shoes', 'trash', 'white-glass']
# Map your model's 13 classes to the three categories
CATEGORY_MAP = {
    'battery': 'landfill',      # Or 'hazardous' if you want to be more specific
    'biological': 'compostable',
    'brown-glass': 'recyclable',
    'cardboard': 'recyclable',
    'clothes': 'landfill',      # Often hard to recycle
    'glass': 'recyclable',
    'green-glass': 'recyclable',
    'metal': 'recyclable',
    'paper': 'recyclable',
    'plastic': 'plastic',       # You might want to handle plastic separately
    'shoes': 'landfill',
    'trash': 'landfill',
    'white-glass': 'recyclable'
}
print("Model loading..")
print("Model loading....")
print("Model loading.......")
print("Model loaded successfully🐻🐻‍❄️🐼!")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def preprocess_image(image_data, is_base64=False):
    """Converts image to the exact mathematical format MobileNetV2 expects."""
    try:
        if is_base64:
            if "," in image_data:
                image_data = image_data.split(",")[1]
            image_bytes = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(image_bytes))
        else:
            img = Image.open(image_data)

        # Convert to RGB (in case someone uploads a PNG with transparency)
        img = img.convert('RGB')
        
        # MobileNetV2 standard input size is 224x224
        img = img.resize((224, 224)) 
        
        # Convert image to numpy array
        img_array = img_to_array(img)
        
        # Expand dimensions to create a "batch" of 1: (1, 224, 224, 3)
        img_array = np.expand_dims(img_array, axis=0) 
        
        # Apply MobileNetV2's specific scaling (-1 to 1)
        processed_image = preprocess_input(img_array)
        
        return processed_image
    except Exception as e:
        print(f"Error processing image: {e}")
        return None
    
# --- SERVING TEMPLATE ---
@app.route('/')
def index():
    return render_template('index.html')

# --- AUTH ROUTES ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    avatar = data.get('avatar')
    try:
        conn = get_db_connection()
        cursor = conn.execute("INSERT INTO users (username, password, avatar) VALUES (?, ?, ?)", 
                              (username, password, avatar))
        user_id = cursor.lastrowid
        conn.execute("INSERT INTO user_progress (user_id) VALUES (?)", (user_id,))
        conn.execute("INSERT INTO user_stats (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "User registered successfully!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "Username already exists!"}), 400
    
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if user and user['password'] == password:
        return jsonify({"message": "Login successful!", "username": user['username'], "avatar": user['avatar']}), 200
    return jsonify({"message": "Invalid credentials!"}), 401

@app.route('/api/guest-login', methods=['POST'])
def guest_login():
    guest_username = f"Guest_{uuid.uuid4().hex[:6]}"
    conn = get_db_connection()
    cursor = conn.execute("INSERT INTO users (username, password, is_guest) VALUES (?, ?, ?)", (guest_username, None, 1))
    user_id = cursor.lastrowid
    conn.execute("INSERT INTO user_progress (user_id) VALUES (?)", (user_id,))
    conn.execute("INSERT INTO user_stats (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"username": guest_username, "message": "Guest login successful"}), 201

# --- DASHBOARD & SCAN ROUTES ---
@app.route('/api/user/<username>', methods=['GET'])
def get_dashboard_data(username):
    conn = get_db_connection()
    query = """
        SELECT u.total_xp, p.current_streak, s.total_items_sorted, 
               p.daily_progress, p.daily_goal 
        FROM users u
        LEFT JOIN user_progress p ON u.id = p.user_id
        LEFT JOIN user_stats s ON u.id = s.user_id
        WHERE u.username = ?
    """
    row = conn.execute(query, (username,)).fetchone()
    conn.close()
    if row:
        data = dict(row)
        return jsonify({
            "total_xp": data.get('total_xp') or 0,
            "streak": data.get('current_streak') or 0,
            "items_sorted": data.get('total_items_sorted') or 0,
            "daily_progress": data.get('daily_progress') or 0,
            "daily_goal": data.get('daily_goal') or 5
        }), 200
    return jsonify({"error": "User data not found"}), 404

@app.route('/api/scans/<username>', methods=['GET'])
def get_user_scans(username):
    conn = get_db_connection()
    query = "SELECT item_name, points_earned, timestamp FROM scans WHERE username = ? ORDER BY timestamp DESC LIMIT 5"
    scans = conn.execute(query, (username,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in scans])

# --- GAMIFIED AI ROUTE ---
@app.route('/api/classify', methods=['POST'])
def classify_item():
    image_data = None
    is_base64 = False
    username = request.args.get('username') or "Guest"

    # Extract payload
    if request.is_json:
        data = request.get_json() or {}
        image_data = data.get('image')
        username = data.get('username', username)
        is_base64 = True
    else:
        if 'image' in request.files:
            image_data = request.files['image']
            username = request.form.get('username', username)

    if not image_data:
        return jsonify({"valid": False, "error": "No image data uploaded"}), 400
    
    processed_image = preprocess_image(image_data, is_base64)
    if processed_image is None:
        return jsonify({"valid": False, "error": "Invalid image format"}), 400

    try:
        # Run inference
        predictions = MODEL.predict(processed_image)
        predicted_index = np.argmax(predictions[0])
        confidence = float(np.max(predictions[0]))
        predicted_material = CLASS_NAMES[predicted_index]
        
        # Look up the category using the map
        category = CATEGORY_MAP.get(predicted_material, 'unknown')

        # Build response based on confidence threshold
        if confidence > 0.65:
            ai_prediction = {
                'valid': True, 
                'material': predicted_material, 
                'category': category, 
                'confidence': round(confidence * 100, 2)
            }
        else:
            ai_prediction = {
                'valid': False, 
                'material': 'unknown', 
                'category': 'none',
                'confidence': round(confidence * 100, 2)
            }

        return jsonify(ai_prediction)

    except Exception as e:
        print(f"Model prediction error: {e}")
        return jsonify({"valid": False, "error": "AI classification failed"}), 500

@app.route('/api/quiz/reward', methods=['POST'])
def reward_user():
    data = request.get_json() or {}
    username = data.get('username')
    item_name = data.get('material', 'Unknown Item')
    points = data.get('points', 10)

    if not username:
        return jsonify({"error": "Username context required"}), 400

    conn = get_db_connection()
    
    # Check if user exists
    user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if not user:
        conn.close()
        return jsonify({"error": "User does not exist"}), 404
        
    user_id = user['id']

    # Update database statistics
    conn.execute("UPDATE users SET total_xp = total_xp + ? WHERE id = ?", (points, user_id))
    conn.execute("UPDATE user_stats SET total_items_sorted = total_items_sorted + 1 WHERE user_id = ?", (user_id,))
    conn.execute("UPDATE user_progress SET daily_progress = daily_progress + 1 WHERE user_id = ?", (user_id,))
    
    # Log the scan event to scan history table
    conn.execute("INSERT INTO scans (username, item_name, points_earned) VALUES (?, ?, ?)", 
                 (username, item_name, points))
    
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": f"Successfully gained {points} XP!"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)