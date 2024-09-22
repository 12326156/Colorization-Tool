from flask import Flask, request, render_template, send_file
from PIL import Image
import numpy as np
import io
import cv2
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)


executor = ThreadPoolExecutor(max_workers=5)

def colorize_image(image_rgb):
    try:
        
        image_lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)

        L = image_lab[:, :, 0]
        AB = image_lab[:, :, 1:]

       
        colorized_image_lab = np.zeros_like(image_lab)
        colorized_image_lab[:, :, 0] = L
        colorized_image_lab[:, :, 1:] = 0  

        
        colorized_image_rgb = cv2.cvtColor(colorized_image_lab, cv2.COLOR_LAB2RGB)

        return colorized_image_rgb

    except Exception as e:
        print("Error:", e)
        return None


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/colorize', methods=['POST'])
def colorize():
    
    if 'image' not in request.files:
        return "No image uploaded", 400

    
    uploaded_image = request.files['image']

    try:
        
        img = Image.open(uploaded_image)

       
        img_array = np.array(img)

        
        if len(img_array.shape) < 2:
            return "Invalid image format", 400

       
        if len(img_array.shape) == 3 and img_array.shape[2] == 4:
            img_array = img_array[:, :, :3]

        if len(img_array.shape) == 2:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)

        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        task = loop.run_in_executor(executor, colorize_image, img_array)
        colorized_img = loop.run_until_complete(task)

        if colorized_img is not None:
           
            colorized_img = Image.fromarray(colorized_img)

            
            output_stream = io.BytesIO()
            colorized_img.save(output_stream, format='PNG')
            output_stream.seek(0)

           
            return send_file(output_stream, mimetype='image/png')
        else:
            return "Failed to colorize the image", 500
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
