import os
from flask import Flask, render_template, request, send_file
from stegano import lsb, exifHeader  # <--- Added exifHeader import
from werkzeug.utils import secure_filename

app = Flask(__name__)

# CONFIGURATION
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/encode', methods=['POST'])
def encode():
    # 1. Get the Image and Message
    image = request.files['image']
    message = request.form['message']
    
    if not image or not message:
        return "Error: Please upload an image and type a message."

    # 2. Save the original image temporarily
    filename = secure_filename(image.filename)
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(original_path)

    # Prepare the output path
    secret_filename = "secret_" + filename
    secret_path = os.path.join(app.config['UPLOAD_FOLDER'], secret_filename)

    # 3. Check format and Hide the message
    try:
        if filename.lower().endswith('.png'):
            # PNG: Use LSB (Pixel Hiding)
            secret_image = lsb.hide(original_path, message)
            secret_image.save(secret_path)
            
        elif filename.lower().endswith(('.jpg', '.jpeg')):
            # JPG: Use ExifHeader (Metadata Hiding)
            # Note: exifHeader.hide automatically saves the file to secret_path
            exifHeader.hide(original_path, secret_path, secret_message=message)
        
        else:
            return "Error: Only PNG and JPG files are supported."

        # 4. Send it back to the user
        return send_file(secret_path, as_attachment=True)

    except Exception as e:
        return f"Encoding Error: {str(e)}"

@app.route('/decode', methods=['POST'])
def decode():
    # 1. Get the "Secret" image
    image = request.files['secret_image']
    
    if not image:
        return "Error: Please upload an image."

    # 2. Save it temporarily so we can read it
    filename = secure_filename(image.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(file_path)

    # 3. Reveal the hidden message based on format
    hidden_message = "No hidden message found."
    
    try:
        if filename.lower().endswith('.png'):
            # PNG: Reveal from pixels
            hidden_message = lsb.reveal(file_path)
            
        elif filename.lower().endswith(('.jpg', '.jpeg')):
            # JPG: Reveal from metadata
            hidden_message = exifHeader.reveal(file_path)
            
            # Exif reveal sometimes returns bytes, so we decode it to string
            if isinstance(hidden_message, bytes):
                hidden_message = hidden_message.decode()

    except Exception as e:
        hidden_message = f"Error decoding image: {str(e)}"

    if not hidden_message:
        hidden_message = "No hidden message found in this image!"

    return f"<h1>Decoded Message:</h1> <p>{hidden_message}</p> <a href='/'>Go Back</a>"

if __name__ == '__main__':
    app.run(debug=True)