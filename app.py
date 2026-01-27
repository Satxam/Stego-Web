import os
import base64
import hashlib
from flask import Flask, render_template, request, send_file
from stegano import lsb, exifHeader
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet # <--- NEW: Import Fernet for encryption

app = Flask(__name__)

# CONFIGURATION
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- HELPER FUNCTIONS FOR ENCRYPTION ---

def generate_key(password):
    """
    Generates a 32-byte key from the user's password.
    We use SHA256 to ensure any password creates a valid Fernet key.
    """
    digest = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(digest)

def encrypt_message(message, password):
    key = generate_key(password)
    f = Fernet(key)
    # Encrypt the message (returns bytes, so we decode to string for steganography)
    encrypted_bytes = f.encrypt(message.encode())
    return encrypted_bytes.decode()

def decrypt_message(encrypted_message, password):
    try:
        key = generate_key(password)
        f = Fernet(key)
        # Decrypt the message
        decrypted_bytes = f.decrypt(encrypted_message.encode())
        return decrypted_bytes.decode()
    except Exception:
        # If decryption fails (wrong password or not encrypted)
        return None

# ---------------------------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/encode', methods=['POST'])
def encode():
    # 1. Get Image, Message AND Password
    image = request.files['image']
    message = request.form['message']
    password = request.form['password'] # <--- NEW: Get password
    
    if not image or not message:
        return "Error: Please upload an image and type a message."

    # 2. Save original temporarily
    filename = secure_filename(image.filename)
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(original_path)

    secret_filename = "secret_" + filename
    secret_path = os.path.join(app.config['UPLOAD_FOLDER'], secret_filename)

    # 3. Encrypt the message if a password exists
    if password:
        message = "ENC:" + encrypt_message(message, password) # Prefix to identify encrypted msgs

    # 4. Hide the message
    try:
        if filename.lower().endswith('.png'):
            secret_image = lsb.hide(original_path, message)
            secret_image.save(secret_path)
            
        elif filename.lower().endswith(('.jpg', '.jpeg')):
            exifHeader.hide(original_path, secret_path, secret_message=message)
        
        else:
            return "Error: Only PNG and JPG files are supported."

        return send_file(secret_path, as_attachment=True)

    except Exception as e:
        return f"Encoding Error: {str(e)}"

@app.route('/decode', methods=['POST'])
def decode():
    # 1. Get Image AND Password
    image = request.files['secret_image']
    password = request.form['password'] # <--- NEW: Get password
    
    if not image:
        return "Error: Please upload an image."

    # 2. Save temporarily
    filename = secure_filename(image.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(file_path)

    # 3. Reveal hidden data
    hidden_data = "No hidden message found."
    
    try:
        if filename.lower().endswith('.png'):
            hidden_data = lsb.reveal(file_path)
            
        elif filename.lower().endswith(('.jpg', '.jpeg')):
            hidden_data = exifHeader.reveal(file_path)
            if isinstance(hidden_data, bytes):
                hidden_data = hidden_data.decode()

    except Exception as e:
        return f"Error extracting data: {str(e)}"

    # 4. Decrypt logic
    if not hidden_data:
        return "No hidden message found in this image!"

    # Check if the message is encrypted (We look for our "ENC:" prefix)
    if hidden_data.startswith("ENC:"):
        if not password:
            return "This message is password protected. Please try again with a password."
        
        # Remove the prefix and attempt to decrypt
        encrypted_content = hidden_data[4:] 
        decrypted_message = decrypt_message(encrypted_content, password)
        
        if decrypted_message:
            hidden_data = decrypted_message
        else:
            return "Error: Wrong Password!"
    
    return f"<h1>Decoded Message:</h1> <p>{hidden_data}</p> <a href='/'>Go Back</a>"

if __name__ == '__main__':
    app.run(debug=True)