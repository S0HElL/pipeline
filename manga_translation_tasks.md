# Manga Translation Project - MVP Task List

## Project Overview
Build a pipeline to: Extract Japanese text from manga/comic images → Remove text (inpainting) → Translate to English → Place translated text back

---

## Phase 1: Environment Setup

### Task 1.1: Install Python and Basic Tools
- [ ] 1.1.1: Verify Python 3.8+ is installed (`python --version`)
- [ ] 1.1.2: Create project folder (e.g., `manga-translator`)
- [ ] 1.1.3: Create virtual environment: `python -m venv venv`
- [ ] 1.1.4: Activate virtual environment:
  - Windows: `venv\Scripts\activate`
  - Mac/Linux: `source venv/bin/activate`

### Task 1.2: Install Core Libraries
- [ ] 1.2.1: Install image processing: `pip install Pillow opencv-python`
- [ ] 1.2.2: Install OCR: `pip install manga-ocr`
- [ ] 1.2.3: Install ML framework: `pip install torch torchvision` (or CPU version if no GPU)
- [ ] 1.2.4: Install utilities: `pip install numpy matplotlib`

### Task 1.3: Test Installation
- [ ] 1.3.1: Create `test_imports.py` and test all imports work
- [ ] 1.3.2: Run test script successfully

---

## Phase 2: OCR (Text Detection & Extraction)

### Task 2.1: Basic OCR Setup
- [ ] 2.1.1: Create `ocr_module.py`
- [ ] 2.1.2: Initialize manga-ocr model
- [ ] 2.1.3: Write function to load test image
- [ ] 2.1.4: Write function to extract text from image

### Task 2.2: Text Location Detection
- [ ] 2.2.1: Install EasyOCR for bounding boxes: `pip install easyocr`
- [ ] 2.2.2: Write function to detect text regions (x, y, width, height)
- [ ] 2.2.3: Save coordinates for each detected text block
- [ ] 2.2.4: Visualize bounding boxes on test image

### Task 2.3: Test OCR Pipeline
- [ ] 2.3.1: Test with 2-3 sample manga images
- [ ] 2.3.2: Verify text extraction accuracy
- [ ] 2.3.3: Debug any issues with text detection

---

## Phase 3: Translation Module

### Task 3.1: Choose Translation Method
- [ ] 3.1.1: Decide: DeepL API / Google Translate API / Local model
- [ ] 3.1.2: Sign up for API key if using DeepL/Google (free tier)
- [ ] 3.1.3: Store API key securely (environment variable or config file)

### Task 3.2: Setup Translation
- [ ] 3.2.1: Install translation library:
  - DeepL: `pip install deepl`
  - Google: `pip install google-cloud-translate`
  - Local: `pip install transformers sentencepiece`
- [ ] 3.2.2: Create `translation_module.py`
- [ ] 3.2.3: Write function to translate Japanese text to English
- [ ] 3.2.4: Test translation with sample Japanese sentences

---

## Phase 4: Inpainting (Text Removal)

### Task 4.1: Setup Inpainting Model
- [ ] 4.1.1: Install inpainting library: `pip install lama-cleaner` or use cv2 inpainting
- [ ] 4.1.2: Create `inpainting_module.py`
- [ ] 4.1.3: Download/initialize inpainting model

### Task 4.2: Implement Text Removal
- [ ] 4.2.1: Write function to create mask from text bounding boxes
- [ ] 4.2.2: Write function to apply inpainting to masked regions
- [ ] 4.2.3: Test on sample image - verify text is cleanly removed

### Task 4.3: Optimize Inpainting
- [ ] 4.3.1: Adjust mask padding/dilation for cleaner results
- [ ] 4.3.2: Test with different text sizes and backgrounds
- [ ] 4.3.3: Handle edge cases (text near image borders)

---

## Phase 5: Text Rendering (Placing English Text)

### Task 5.1: Basic Text Placement
- [ ] 5.1.1: Install text rendering: Already in Pillow
- [ ] 5.1.2: Create `text_renderer.py`
- [ ] 5.1.3: Write function to calculate appropriate font size for text box
- [ ] 5.1.4: Write function to render English text at saved coordinates

### Task 5.2: Text Formatting
- [ ] 5.2.1: Implement word wrapping for long translations
- [ ] 5.2.2: Center text within original bounding box
- [ ] 5.2.3: Choose readable font (include font file or use system font)
- [ ] 5.2.4: Add text background/outline for readability

### Task 5.3: Test Text Rendering
- [ ] 5.3.1: Test with various text lengths
- [ ] 5.3.2: Ensure text fits within speech bubbles
- [ ] 5.3.3: Adjust positioning as needed

---

## Phase 6: Integration (Complete Pipeline)

### Task 6.1: Create Main Pipeline
- [ ] 6.1.1: Create `main.py`
- [ ] 6.1.2: Import all modules
- [ ] 6.1.3: Write pipeline function that chains all steps:
  - Load image → OCR → Inpaint → Translate → Render → Save

### Task 6.2: Add File Handling
- [ ] 6.2.1: Create input/output folders
- [ ] 6.2.2: Add command-line arguments for input image path
- [ ] 6.2.3: Save output image with timestamp/versioning

### Task 6.3: Error Handling
- [ ] 6.3.1: Add try-catch blocks for each pipeline step
- [ ] 6.3.2: Add logging to track progress
- [ ] 6.3.3: Handle cases with no text detected

---

## Phase 7: Testing & Polish

### Task 7.1: End-to-End Testing
- [ ] 7.1.1: Test complete pipeline with 5+ different manga images
- [ ] 7.1.2: Document any failure cases
- [ ] 7.1.3: Measure processing time per image

### Task 7.2: Improvements
- [ ] 7.2.1: Create before/after comparison visualization
- [ ] 7.2.2: Add progress bars for long operations
- [ ] 7.2.3: Optimize slow steps

### Task 7.3: Documentation
- [ ] 7.3.1: Write README.md with setup instructions
- [ ] 7.3.2: Add usage examples
- [ ] 7.3.3: Document known limitations

---

## MVP Complete! 🎉

**Next Steps (Post-MVP):**
- Batch processing for multiple images
- Web interface (Gradio/Streamlit)
- Vertical text handling improvements
- Custom font selection
- Quality comparison metrics

---

## Current Status
**Last Updated:** Not started
**Current Phase:** Phase 1 - Environment Setup
**Next Task:** Task 1.1 - Install Python and Basic Tools