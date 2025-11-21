import os
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple
import textwrap
import re
import pyphen

# Initialize the English hyphenation dictionary
# This is done once to avoid overhead
HYPHENATOR = pyphen.Pyphen(lang='en_US')

# Define a default font path. This should be a common, readable font.

DEFAULT_FONT_PATH = "fonts/animeace2_reg.otf"

def get_font(size: int) -> ImageFont.FreeTypeFont:
    """Loads a font at the specified size with fallback."""
    try:
        return ImageFont.truetype(DEFAULT_FONT_PATH, size)
    except IOError:
        # Try a fallback font with better Unicode support
        try:
            return ImageFont.truetype("Wild Words Roman.ttf", size)
        except IOError:
            print(f"Warning: Could not load fonts. Falling back to default PIL font.")
            return ImageFont.load_default()


def break_long_word(word: str, max_width: int, draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont) -> str:
    bbox = draw.textbbox((0, 0), word, font=font)
    w = bbox[2] - bbox[0]
    if w <= max_width:
        return word

    hyphen_positions = HYPHENATOR.positions(word)
    if not hyphen_positions:
        # No hyphenation points → force break somewhere reasonable
        # We'll let caller handle failure
        return word

    # Try longest valid prefix first
    for i in reversed(hyphen_positions):
        prefix = word[:i] + '-'
        if draw.textbbox((0, 0), prefix, font=font)[2] <= max_width:
            return word[:i] + '-\n' + word[i:]

    # If no hyphenated version fits → give up (font too big)
    return word
def calculate_font_size(draw: ImageDraw.ImageDraw, text: str, box_width: int, box_height: int, max_size: int = 80, min_size: int = 10) -> Tuple[int, str]:
    """
    Binary search for the largest font size that fits, with intelligent word breaking.
    """
    best_size = min_size
    best_wrapped_text = text
    
    # Actual binary search
    low, high = min_size, max_size
    
    while low <= high:
        size = (low + high) // 2
        font = get_font(size)
        
        # Try wrapping with this font size
        result = wrap_text_with_breaking(draw, text, box_width, box_height, font)
        
        if result is None:
            # Doesn't fit, try smaller
            high = size - 1
        else:
            # Fits! Try larger
            best_size = size
            best_wrapped_text = result
            low = size + 1
            
   
    return best_size, best_wrapped_text

def wrap_text_with_breaking(draw: ImageDraw.ImageDraw, text: str, box_width: int, box_height: int, font: ImageFont.FreeTypeFont) -> str | None:
    words = text.split()
    lines = []
    current_line_words = []

    def get_text_width(t: str) -> int:
        return draw.textbbox((0, 0), t, font=font)[2] - draw.textbbox((0, 0), t, font=font)[0]

    for word in words:
        # Test adding the word with a space (unless it's the first word in line)
        test_line = ' '.join(current_line_words + [word]) if current_line_words else word
        test_width = get_text_width(test_line)

        if test_width <= box_width:
            # It fits → keep building the line
            current_line_words.append(word)
            continue

        # Line is full → flush current line
        if current_line_words:
            lines.append(' '.join(current_line_words))
            current_line_words = []

        # Now try to place the current word on a new line
        word_width = get_text_width(word)
        if word_width <= box_width:
            current_line_words.append(word)
        else:
            # Word is too long → hyphenate
            broken = break_long_word(word, box_width, draw, font)
            if '\n' not in broken:
                # Even first fragment doesn't fit → this font size is impossible
                return None

            parts = broken.split('\n')
            # All parts except last go on their own lines
            for part in parts[:-1]:
                if get_text_width(part) > box_width:
                    return None  # Shouldn't happen if break_long_word is correct
                lines.append(part)
            # Last part starts the next line
            current_line_words = [parts[-1]]

    # Don't forget the last line
    if current_line_words:
        lines.append(' '.join(current_line_words))

    wrapped = '\n'.join(lines)

    # === Accurate vertical fit check ===
    try:
        # PIL 8+ has multiline_textbbox
        total_bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, align='center')
        total_height = total_bbox[3] - total_bbox[1]
    except AttributeError:
        # Fallback: estimate line height
        line_height = font.getsize('hg')[1]  # ascent + descent approximation
        total_height = len(lines) * line_height * 1.2

    if total_height > box_height:
        return None

    # Final horizontal safety check
    for line in lines:
        if get_text_width(line) > box_width:
            return None

    return wrapped


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
    # Use multiline_textbbox for accurate height
    try:
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align='center')
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

    text_x = int(x_min + padding + (box_width - text_width) / 2)
    text_y = int(y_min + padding + (box_height - text_height) / 2)
    
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