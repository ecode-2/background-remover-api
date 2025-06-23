from flask import Flask, request, send_file
from rembg import remove
from PIL import Image
import io
import requests
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Background Removal API is running!"

@app.route('/removebg', methods=['POST'])
def remove_background():
    try:
        image_url = request.form.get('image_url')
        bg_color = request.form.get('bg_color', 'FFFFFF')
        crop = request.form.get('crop', 'true').lower() == 'true'
        
        # Download image
        response = requests.get(image_url)
        input_image = Image.open(io.BytesIO(response.content))
        
        # Remove background
        output_image = remove(input_image)
        
        # Add white background
        if bg_color and bg_color != 'transparent':
            bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (0, 2, 4))
            background = Image.new('RGB', output_image.size, bg_rgb)
            background.paste(output_image, mask=output_image.split()[-1])
            output_image = background
        
        # Auto-crop if requested
        if crop:
            bbox = output_image.getbbox()
            if bbox:
                margin_px = int(min(output_image.size) * 0.1)
                bbox = (
                    max(0, bbox[0] - margin_px),
                    max(0, bbox[1] - margin_px),
                    min(output_image.size[0], bbox[2] + margin_px),
                    min(output_image.size[1], bbox[3] + margin_px)
                )
                output_image = output_image.crop(bbox)
        
        # Return processed image
        img_io = io.BytesIO()
        output_image.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
    
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
