# Manga Translator

An automated pipeline for translating Japanese manga and comics into English. This tool detects Japanese text in images, removes it cleanly, translates it to English, and renders the translation back onto the image.

## Overview

This project implements a multi-modal processing pipeline that combines:
- Optical Character Recognition (OCR) for Japanese text
- Image inpainting for text removal
- Machine translation (Japanese to English)
- Text rendering and placement

## Features

- Automatic Japanese text detection and extraction
- Clean text removal using inpainting
- Translation to natural English
- Smart text placement that fits within original speech bubbles
- Support for both horizontal and vertical text layouts
- Batch processing capabilities

## Requirements

### System Requirements
- Python 3.8 or higher
- 4GB+ RAM
- GPU recommended but not required (CPU processing is slower)

### Dependencies
- Python 3.8+
- PyTorch
- manga-ocr
- EasyOCR
- Pillow (PIL)
- OpenCV
- Translation API or local translation model

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/manga-translator.git
cd manga-translator
```

### 2. Create virtual environment
```bash
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure translation (choose one)

#### Option A: DeepL API (Recommended - Free tier available)
1. Sign up at https://www.deepl.com/pro-api
2. Get your API key
3. Create `.env` file:
```
DEEPL_API_KEY=your_api_key_here
```

#### Option B: Google Cloud Translation
1. Set up Google Cloud project
2. Enable Translation API
3. Download credentials JSON
4. Set environment variable to credentials path

#### Option C: Local Translation Model
No setup required - uses offline Hugging Face models (slower, less natural translations)

## Usage

### Basic Usage
```bash
python main.py --input path/to/manga_page.jpg --output translated_output.jpg
```

### Advanced Options
```bash
python main.py \
  --input input_image.jpg \
  --output output_image.jpg \
  --translation-method deepl \
  --visualize-boxes
```

### Command Line Arguments
- `--input`: Path to input manga image
- `--output`: Path to save translated image
- `--translation-method`: Translation method (deepl/google/local)
- `--visualize-boxes`: Show detected text bounding boxes
- `--font-size`: Base font size for rendered text
- `--language`: Source language (default: Japanese)

## Project Structure

```
manga-translator/
├── main.py                 # Main pipeline script
├── ocr_module.py          # Text detection and extraction
├── inpainting_module.py   # Text removal
├── translation_module.py  # Text translation
├── text_renderer.py       # English text placement
├── requirements.txt       # Python dependencies
├── .env                   # API keys (not in repo)
├── input/                 # Input images folder
├── output/                # Translated images folder
└── fonts/                 # Font files for text rendering
```

## How It Works

### Pipeline Steps

1. **Text Detection (OCR)**
   - Detects Japanese text regions using EasyOCR
   - Extracts text content using manga-ocr
   - Saves bounding box coordinates for each text block

2. **Text Removal (Inpainting)**
   - Creates masks for detected text regions
   - Uses inpainting to fill in removed text areas
   - Preserves background artwork and details

3. **Translation**
   - Translates extracted Japanese text to English
   - Uses DeepL/Google API or local models
   - Preserves context and natural phrasing

4. **Text Rendering**
   - Calculates appropriate font size for each text block
   - Wraps text to fit within original boundaries
   - Renders English text with readable formatting

## Limitations

- Best results with clear, printed text
- May struggle with highly stylized or handwritten fonts
- Vertical text handling is basic in current version
- Translation quality depends on chosen method
- Inpainting may produce artifacts on complex backgrounds

## Known Issues

- Text overlapping image borders may be cut off
- Very long translations might not fit in small speech bubbles
- Background patterns may not perfectly match after inpainting

## Troubleshooting

### "No text detected" error
- Ensure image has sufficient resolution
- Check if text contrast is high enough
- Try adjusting detection confidence threshold

### Poor inpainting quality
- Increase mask padding in settings
- Try different inpainting models
- Manual touch-up may be needed for complex areas

### Translation seems unnatural
- Switch from local model to DeepL/Google API
- Check source language detection accuracy
- Verify API key is configured correctly

## Performance

Approximate processing times (on mid-range hardware):
- Single manga page: 10-30 seconds (with GPU)
- Single manga page: 30-90 seconds (CPU only)

Factors affecting speed:
- Image resolution
- Amount of text
- Translation method (API vs local)
- Hardware specifications

## Future Improvements

- Web interface for easier usage
- Batch processing with progress tracking
- Better vertical text support
- Custom font selection per text block
- Manual correction interface
- Support for more languages
- OCR model fine-tuning on specific manga styles

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Acknowledgments

- manga-ocr for Japanese OCR capabilities
- EasyOCR for text detection
- DeepL/Google for translation APIs
- LaMa for inpainting model
- The open-source community

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.

---

**Note:** This is an educational project. Please respect copyright laws when using this tool with commercial manga content.
