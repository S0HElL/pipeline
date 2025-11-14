import os
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple
import textwrap
import re

# Define a default font path. This should be a common, readable font.
# If a specific font file is available, it should be used.
# For now, we'll use a common system font name or a placeholder.
# A good choice for manga is a clean, sans-serif font.
# NOTE: The user may need to provide a font file (e.g., 'data/manga_font.ttf')
DEFAULT_FONT_PATH = "fonts/Wild Words Roman.ttf"

def get_font(size: int) -> ImageFont.FreeTypeFont:
    """Loads a font at the specified size with fallback."""
    try:
        return ImageFont.truetype(DEFAULT_FONT_PATH, size)
    except IOError:
        # Try a fallback font with better Unicode support
        try:
            return ImageFont.truetype("animeace2_reg.otf", size)
        except IOError:
            print(f"Warning: Could not load fonts. Falling back to default PIL font.")
            return ImageFont.load_default()

def calculate_font_size(draw: ImageDraw.ImageDraw, text: str, box_width: int, box_height: int, max_size: int = 50, min_size: int = 10) -> Tuple[int, str]:
    """
    Task 5.1.3 & 5.2.1: Calculates the largest font size that allows the wrapped text to fit 
    within the bounding box. Returns the best size and the wrapped text.
    """
    best_size = min_size
    best_wrapped_text = text
    
    # Binary search for the best fit
    for size in range(min_size, max_size + 1):
        font = get_font(size)
        
        # 1. Wrap the text based on the current font size and box width
        # We need to estimate the max characters per line for the wrapper
        
        # For now, we'll use a simple character-based heuristic for max_chars_per_line
        try:
            # Measure the width of a single character (e.g., 'W')
            char_width = draw.textbbox((0, 0), 'W', font=font)[2]
        except Exception:
            # Fallback for older PIL versions or default font
            char_width = font.getsize('W')[0]
            
        if char_width == 0:
            # If font size is too small to measure, break
            break 
            
        # Heuristic multiplier for better wrapping. Reduced from 1.5 to 1.2 to encourage
        # more line breaks for tall speech bubbles, as requested by the user.
        max_chars_per_line = max(1, int(box_width / char_width * 1.0))
        # Allow breaking long words (like 'SWIMSUIT') to prevent text from going out of bounds.
        # This is a common practice in manga typesetting (Task 5.3.4).
        wrapper = textwrap.TextWrapper(width=max_chars_per_line, break_long_words=False)
        wrapped_text = '\n'.join(wrapper.wrap(text=text))
        
        # 2. Measure the wrapped text's total height
        # Use textbbox for accurate size calculation
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_height = bbox[3] - bbox[1]
        
        # Use a 10% buffer for line spacing (leading) to prevent lines from being too close.
        if text_height * 1.1 <= box_height:
            best_size = size
            best_wrapped_text = wrapped_text
        else:
            # Stop when the text no longer fits
            break
            
    return best_size, best_wrapped_text

def render_text(image_pil: Image.Image, translated_text: str, bounding_box: Tuple[int, int, int, int], padding: int = 5) -> Image.Image:
    """
    Task 5.1.4: Renders the translated English text onto the image at the 
    specified bounding box coordinates.
    
    Args:
        image_pil: The PIL Image object (e.g., the inpainted image).
        translated_text: The English text to render.
        bounding_box: (x_min, y_min, x_max, y_max) of the original text bubble.
        padding: Padding inside the bounding box.
        
    Returns:
        The modified PIL Image object.
    """
    draw = ImageDraw.Draw(image_pil)
    x_min, y_min, x_max, y_max = bounding_box
    
    # First normalize full-width periods and ellipsis to ASCII
    translated_text = translated_text.replace('．', '.').replace('…', '.')

    # Remove spaces between periods first, then collapse multiple periods
    translated_text = re.sub(r'\.\s+\.', '..', translated_text)  # Replace ". ." with ".."
    translated_text = re.sub(r'\.{3,}', '...', translated_text)   # Then collapse 3+ periods
            
    # Calculate available space for text
    box_width = x_max - x_min - 2 * padding
    box_height = y_max - y_min - 2 * padding
    
    if box_width <= 0 or box_height <= 0:
        print(f"Warning: Bounding box is too small for text rendering: {bounding_box}")
        return image_pil

    # 1. Calculate appropriate font size and get wrapped text (Task 5.1.3 & 5.2.1)
    font_size, wrapped_text = calculate_font_size(draw, translated_text, box_width, box_height)
    font = get_font(font_size)
    
    # 2. Calculate centered text position (Task 5.2.2)
    # Get the total size of the wrapped text
    bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate center coordinates for the text block within the padded box
    # Center X: (Box_Center_X) - (Text_Width / 2)
    # Center Y: (Box_Center_Y) - (Text_Height / 2)
    
    box_center_x = x_min + (x_max - x_min) / 2
    box_center_y = y_min + (y_max - y_min) / 2
    
    text_x = int(box_center_x - text_width / 2)
    text_y = int(box_center_y - text_height / 2)
    
    # 3. Render the text with a white outline (Task 5.2.4)
    outline_color = "white"
    text_color = "black"
    outline_width = 2
    
    # Draw outline
    for x_offset in range(-outline_width, outline_width + 1):
        for y_offset in range(-outline_width, outline_width + 1):
            # Skip the center position, which is the main text
            if x_offset != 0 or y_offset != 0:
                draw.text((text_x + x_offset, text_y + y_offset), wrapped_text, font=font, fill=outline_color, align='center')

    # Draw main text
    draw.text((text_x, text_y), wrapped_text, font=font, fill=text_color, align='center')
    
    return image_pil

if __name__ == '__main__':
    # Placeholder for testing
    print("Text renderer module created. Ready for integration and testing.")
    # Example usage would require a sample image and a bounding box
    # from PIL import Image
    # img = Image.new('RGB', (800, 600), color = 'white')
    # box = (100, 100, 400, 200)
    # text = "Hello World, this is a long sentence that needs to be wrapped."
    # img = render_text(img, text, box)
    # img.save("data/text_render_test.png")