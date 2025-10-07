from flask import Flask, request, jsonify
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_FILE = os.path.join(os.path.dirname(__file__), "database", "db_users.json")


# Helper Function to load JSON File 

def load_users():
    if not os.path.exists(DB_FILE): # checks if file at path exsits --> if not --> return default value
        return {"users": []}
    with open(DB_FILE, "r") as f:
        return json.load(f)

# Helper to save JSON file
def save_users(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

#Endpoint ot add a new user 

@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.get_json() 
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    
    users_data = load_users()

    for u in users_data["users"]: 
        if u["email"] == email: 
            return jsonify({"error": "User already exists"}), 400
        
    #Otherwise add new user 

    users_data["users"].append({
        "email": email, 
        "password": password
    })

    save_users(users_data)

    return jsonify({"message": "User added successfully"}), 200

#Login Endpoint
@app.route("/login", methods=["POST"])
def login(): 
    data = request.get_json()
    if not data: 
        return jsonify({"error": "Missing JSON data"}), 400
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    users_data = load_users()
    for u in users_data["users"]:
        if u["email"] == email and u["password"] == password:
            return jsonify({"message": "Login successful"}), 200
        

    return jsonify({"error": "Invalid email or password"}), 401


@app.route("/forgot_password", methods=["POST"])
def forgot_password():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON data"}), 400

    email = data.get("email")
    new_password = data.get("new_password")

    if not email or not new_password:
        return jsonify({"error": "Email and new password required"}), 400

    users_data = load_users()
    users_list = users_data.get("users", [])

    # Flag to check if user exists
    user_found = False
    for u in users_list:
        if u["email"] == email:
            u["password"] = new_password  # Update password
            user_found = True
            break

    if not user_found:
        return jsonify({"error": "User not found"}), 404

    # Save updated users to JSON
    save_users(users_data)

    return jsonify({"message": "Password updated successfully"}), 200


@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files found in request'}), 400

    uploaded_files = request.files.getlist('files')

    if not uploaded_files:
        return jsonify({'error': 'No files uploaded'}), 400

    for file in uploaded_files:
        print(f"Received: {file.filename}")

    return jsonify({'status': 'success', 'message': f'{len(uploaded_files)} file(s) received!'})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)