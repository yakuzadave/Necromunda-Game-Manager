
from flask import Flask, send_file
from PIL import Image
import io
import os

app = Flask(__name__)

# Load and cache the base map image
BASE_MAP = Image.open("static/base_map.jpg") if os.path.exists("static/base_map.jpg") else None

@app.route('/tiles/<int:z>/<int:x>/<int:y>.png')
def get_tile(z, x, y):
    if BASE_MAP is None:
        return "No base map found", 404
        
    # Calculate tile size based on zoom level
    tile_size = 256
    scale = 2 ** z
    
    # Calculate pixel coordinates
    px = x * tile_size
    py = y * tile_size
    
    # Extract tile from base image
    tile = BASE_MAP.crop((px, py, px + tile_size, py + tile_size))
    
    # Convert to PNG
    img_io = io.BytesIO()
    tile.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
