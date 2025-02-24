
from PIL import Image, ImageDraw

def create_grid_image(width=2048, height=2048, cell_size=128, line_color=(50, 50, 50)):
    # Create a new image with a dark background
    image = Image.new('RGB', (width, height), (20, 20, 20))
    draw = ImageDraw.Draw(image)
    
    # Draw vertical lines
    for x in range(0, width, cell_size):
        draw.line([(x, 0), (x, height)], fill=line_color)
    
    # Draw horizontal lines
    for y in range(0, height, cell_size):
        draw.line([(0, y), (width, y)], fill=line_color)
    
    return image

if __name__ == '__main__':
    grid = create_grid_image()
    grid.save('static/base_map.jpg', 'JPEG')
