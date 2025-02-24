
from flask import Flask, send_file
from PIL import Image
import io
import os
import math

app = Flask(__name__)

# Load and cache the base map image
BASE_MAP = None
if os.path.exists("static/base_map.jpg"):
    BASE_MAP = Image.open("static/base_map.jpg")
    # Convert RGBA to RGB if needed
    if BASE_MAP.mode in ('RGBA', 'LA'):
        BASE_MAP = BASE_MAP.convert('RGB')

@app.route('/tiles/<int:z>/<int:x>/<int:y>.png')
def get_tile(z, x, y):
    if BASE_MAP is None:
        return "No base map found", 404
        
    # Get image dimensions
    img_width, img_height = BASE_MAP.size
    
    # Calculate tile size and scale
    tile_size = 256
    scale = 2 ** z
    
    # Calculate pixel coordinates
    px = (x % scale) * tile_size
    py = (y % scale) * tile_size
    
    # Scale image to zoom level
    scaled_width = img_width * (scale / max(scale, img_width/tile_size))
    scaled_height = img_height * (scale / max(scale, img_height/tile_size))
    
    # Create tile
    try:
        if px < scaled_width and py < scaled_height:
            tile = BASE_MAP.resize((int(scaled_width), int(scaled_height)))
            tile = tile.crop((px, py, px + tile_size, py + tile_size))
        else:
            # Return empty tile if outside image bounds
            tile = Image.new('RGB', (tile_size, tile_size), 'lightgray')
    except Exception:
        tile = Image.new('RGB', (tile_size, tile_size), 'lightgray')
    
    # Convert to PNG
    img_io = io.BytesIO()
    tile.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
