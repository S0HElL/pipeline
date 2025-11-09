# Testing the OCR Pipeline
import cv2
import pytesseract

def test_ocr_pipeline(image_path):
    # Load the image
    image = cv2.imread(image_path)
    
    # Convert the image to gray scale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Use pytesseract to do OCR on the image
    text = pytesseract.image_to_string(gray_image)
    
    print("Detected Text:", text)

# Example usage
if __name__ == "__main__":
    test_ocr_pipeline('path/to/your/image.png')  # Update with the actual image path