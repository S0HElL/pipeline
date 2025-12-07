import os
import cv2
import numpy as np
import easyocr
from PIL import Image, ImageDraw

# Initialize EasyOCR reader globally
# This model is used for text detection and bounding box generation
# 'ja' for Japanese, 'en' for English (to detect any English text in the image)
# The 'gpu=False' is a safe default for systems without a dedicated GPU or for smaller tasks.
# If a GPU is available and performance is critical, this should be set to True.
try:
    reader = easyocr.Reader(['ja', 'en'], gpu=True)
except Exception as e:
    print(f"Error initializing EasyOCR: {e}")
    reader = None

def detect_text_regions(image_path: str) -> tuple[list[tuple], Image.Image | None]:
    """
    Detects text regions in an image and returns bounding box coordinates.
    
    Args:
        image_path: The file path to the image.
        
    Returns:
        A tuple containing:
        1. A list of bounding box tuples: [(x_min, y_min, x_max, y_max), ...]
        2. The original PIL Image object, or None if loading fails.
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return [], None

    try:
        # Load image with PIL for visualization later
        pil_img = Image.open(image_path).convert("RGB")
        
        # Convert PIL Image to a format EasyOCR can use (numpy array)
        img_np = np.array(pil_img)
        
        if reader is None:
            print("Error: EasyOCR reader is not initialized.")
            return [], pil_img

        # Perform text detection
        # detail=0 returns only the text, detail=1 returns bounding boxes, text, and confidence
        results = reader.readtext(img_np, detail=1)
        
        # Extract bounding boxes in the format (x_min, y_min, x_max, y_max)
        # EasyOCR returns: [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], text, confidence]
        # We need to convert the 4-point polygon to a simple bounding box (min/max x/y)
        bounding_boxes = []
        for (bbox_poly, text, conf) in results:
            # bbox_poly is a list of 4 (x, y) points
            x_coords = [p[0] for p in bbox_poly]
            y_coords = [p[1] for p in bbox_poly]
            
            x_min = int(min(x_coords))
            y_min = int(min(y_coords))
            x_max = int(max(x_coords))
            y_max = int(max(y_coords))
            
            bounding_boxes.append((x_min, y_min, x_max, y_max))
            
        return bounding_boxes, pil_img
        
    except Exception as e:
        print(f"Error during text detection for {image_path}: {e}")
        return [], None


def visualize_bounding_boxes(pil_img: Image.Image, bounding_boxes: list[tuple], output_path: str):
    """
    Draws bounding boxes on the image and saves the result.
    
    Args:
        pil_img: The PIL Image object.
        bounding_boxes: A list of bounding box tuples: [(x_min, y_min, x_max, y_max), ...]
        output_path: The file path to save the visualized image.
    """
    if not pil_img:
        print("Cannot visualize: Image is None.")
        return

    draw = ImageDraw.Draw(pil_img)
    
    for (x_min, y_min, x_max, y_max) in bounding_boxes:
        # Draw a red rectangle with a thickness of 2
        # PIL's ImageDraw.rectangle takes (x_min, y_min, x_max, y_max)
        draw.rectangle([(x_min, y_min), (x_max, y_max)], outline="red", width=2)
        
    try:
        pil_img.save(output_path)
        print(f"Visualization saved to: {output_path}")
    except Exception as e:
        print(f"Error saving visualized image to {output_path}: {e}")


if __name__ == '__main__':
    # --- Simple Test Case ---
    # NOTE: You will need a sample Japanese manga image named 'sample_manga.jpg' 
    # in the 'data/' directory for this test to work.
    
    data_dir = "data"
    sample_image_path = os.path.join(data_dir, 'sample_manga.jpg')
    output_image_path = os.path.join(data_dir, 'sample_manga_boxes.jpg')
    
    print(f"--- Testing Text Location Detection with {sample_image_path} ---")
    
    if not os.path.exists(sample_image_path):
        print(f"Please place a sample Japanese manga image at: {sample_image_path}")
        print("Skipping text location detection test.")
    else:
        boxes, image = detect_text_regions(sample_image_path)
        
        if image and boxes:
            print(f"Detected {len(boxes)} text regions.")
            print("Sample Bounding Boxes (x_min, y_min, x_max, y_max):")
            for i, box in enumerate(boxes[:5]): # Print first 5 boxes
                print(f"  Box {i+1}: {box}")
                
            visualize_bounding_boxes(image, boxes, output_image_path)
        elif image:
            print("Image loaded, but no text regions were detected.")
        else:
            print("Image loading or detection failed.")
