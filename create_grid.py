from PIL import Image, ImageDraw, ImageFont
import os

def create_grid_image(width=4096, height=4096, cell_size=128, 
                      line_color=(50, 50, 50), background_color=(20, 20, 20),
                      line_width=2, draw_labels=False, font_path=None, font_size=16):
    """
    Create a grid image with specified dimensions and cell size.

    Parameters:
      width, height      : Dimensions of the image.
      cell_size          : Size of each cell.
      line_color         : Color for grid lines (RGB tuple).
      background_color   : Background color (RGB tuple).
      line_width         : Width of the grid lines.
      draw_labels        : Whether to draw cell coordinate labels.
      font_path          : Path to a TTF font file (optional).
      font_size          : Font size for labels.

    Returns:
      A PIL Image object with the generated grid.
    """
    # Create a new image with the given background color.
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # Load a font if labels are enabled.
    if draw_labels:
        try:
            font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
        except Exception as e:
            font = ImageFont.load_default()
            print(f"Could not load custom font: {e}")

    # Draw vertical grid lines (include right edge)
    for x in range(0, width + 1, cell_size):
        draw.line([(x, 0), (x, height)], fill=line_color, width=line_width)

    # Draw horizontal grid lines (include bottom edge)
    for y in range(0, height + 1, cell_size):
        draw.line([(0, y), (width, y)], fill=line_color, width=line_width)

    # Optionally, draw coordinate labels in each cell.
    if draw_labels:
        for row in range(0, height, cell_size):
            for col in range(0, width, cell_size):
                label = f"({col//cell_size}, {row//cell_size})"
                # Use textbbox to calculate text size
                bbox = draw.textbbox((0, 0), label, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_x = col + (cell_size - text_width) / 2
                text_y = row + (cell_size - text_height) / 2
                draw.text((text_x, text_y), label, fill=(200, 200, 200), font=font)

    return image

if __name__ == '__main__':
    os.makedirs("static", exist_ok=True)
    grid = create_grid_image(draw_labels=True)
    grid.save("static/base_map.jpg", "JPEG")
