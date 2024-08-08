# from flask import Flask, request, jsonify
# import requests
# import os
# from pdf2image import convert_from_path
# from PIL import Image
# import cv2
# import numpy as np
# from pyzbar.pyzbar import decode
# from io import BytesIO

# app = Flask(__name__)

# # Function to convert PDF to images
# def pdf_to_images(pdf_path):
#     images = convert_from_path(pdf_path)
#     return images

# # Function to extract QR data from an image
# def extract_qr_data(image_path):
#     image = cv2.imread(image_path)
#     barcodes = decode(image)
#     qr_data = []

#     for barcode in barcodes:
#         barcode_data = barcode.data.decode('utf-8')
#         qr_data.append({'data': barcode_data, 'type': barcode.type})

#     return qr_data

# @app.route('/read-qr', methods=['POST'])
# def read_qr():
#     if 'url' not in request.json:
#         return jsonify({'error': 'No URL provided'}), 400

#     file_url = request.json['url']
#     filename = os.path.basename(file_url)
#     file_extension = os.path.splitext(filename)[1].lower()

#     if file_extension not in ['.png', '.jpg', '.jpeg', '.pdf']:
#         return jsonify({'error': 'Unsupported file type'}), 400

#     # Download the file
#     response = requests.get(file_url)
#     if response.status_code != 200:
#         return jsonify({'error': 'Failed to download file'}), 400

#     # Save the file to a temporary location
#     temp_path = os.path.join('/tmp', filename)
#     with open(temp_path, 'wb') as f:
#         f.write(response.content)

#     # Handle PDF files
#     if file_extension == '.pdf':
#         images = pdf_to_images(temp_path)
#         data = []
#         for img in images:
#             temp_image_path = temp_path + '.png'
#             img.save(temp_image_path)
#             qr_data = extract_qr_data(temp_image_path)
#             if qr_data:
#                 data.append(qr_data)
#             os.remove(temp_image_path)
#         os.remove(temp_path)
#     else:
#         data = extract_qr_data(temp_path)
#         os.remove(temp_path)

#     if not data:
#         return jsonify({'error': 'Failed to extract QR data'}), 500

#     return jsonify(data)

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, request, jsonify
import os
from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np
from pyzbar.pyzbar import decode

app = Flask(__name__)

# Function to convert PDF to images
def pdf_to_images(pdf_path):
    images = convert_from_path(pdf_path)
    return images

# Function to extract QR data from an image
def extract_qr_data(image_path):
    image = cv2.imread(image_path)
    barcodes = decode(image)
    qr_data = []

    for barcode in barcodes:
        barcode_data = barcode.data.decode('utf-8')
        qr_data.append({'data': barcode_data, 'type': barcode.type})

    return qr_data

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

# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


