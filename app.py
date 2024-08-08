from flask import Flask, request, jsonify
import os
from pdf2image import convert_from_path
from PIL import Image
import cv2

app = Flask(__name__)

# Function to convert PDF to images
def pdf_to_images(pdf_path):
    images = convert_from_path(pdf_path)
    return images

# Function to extract QR data from an image using OpenCV
def extract_qr_data(image_path):
    image = cv2.imread(image_path)
    qr_detector = cv2.QRCodeDetector()
    data, points, _ = qr_detector.detectAndDecode(image)
    
    if points is not None:
        return [{'data': data, 'type': 'QR_CODE'}]
    
    return []

@app.route('/read-qr', methods=['POST'])
def read_qr():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    filename = file.filename

    if filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
        return jsonify({'error': 'Unsupported file type'}), 400

    # Save the file to a temporary location
    temp_path = os.path.join('/tmp', filename)
    file.save(temp_path)

    # Handle PDF files
    if filename.lower().endswith('.pdf'):
        images = pdf_to_images(temp_path)
        data = []
        for img in images:
            temp_image_path = temp_path + '.png'
            img.save(temp_image_path)
            qr_data = extract_qr_data(temp_image_path)
            if qr_data:
                data.append(qr_data)
            os.remove(temp_image_path)
        os.remove(temp_path)
    else:
        data = extract_qr_data(temp_path)
        os.remove(temp_path)

    if not data:
        return jsonify({'error': 'Failed to extract QR data'}), 500

    return jsonify(data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
