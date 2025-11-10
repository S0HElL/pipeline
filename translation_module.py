import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from typing import Any

# Model name for NLLB 600M distilled model
MODEL_NAME = "facebook/nllb-200-distilled-600M"
SOURCE_LANG = "jpn_Jpan" # Japanese
TARGET_LANG = "eng_Latn" # English

# Global variables to hold the tokenizer and model
tokenizer: Any = None
model: Any = None

def initialize_translation_model():
    """
    Initializes the NLLB model and tokenizer for Japanese to English translation.
    Uses GPU if available, otherwise falls back to CPU.
    """
    global tokenizer, model
    if tokenizer is not None and model is not None:
        return

    print(f"Initializing translation model: {MODEL_NAME}...")
    try:
        # Check for GPU
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, src_lang=SOURCE_LANG)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)
        
        print(f"Translation model initialized successfully on {device}.")
    except Exception as e:
        print(f"Error initializing translation model: {e}")
        # Set to None on failure to allow re-initialization attempt
        tokenizer = None
        model = None
        raise

def translate_japanese_to_english(japanese_text: str) -> str:
    """
    Translates a single string of Japanese text to English using the NLLB model.

    Args:
        japanese_text: The Japanese text to translate.

    Returns:
        The translated English text.
    """
    global tokenizer, model
    if tokenizer is None or model is None:
        try:
            initialize_translation_model()
        except Exception:
            return "[Translation Error: Model initialization failed]"

    # Explicit check after initialization attempt
    if tokenizer is None or model is None:
        return "[Translation Error: Model not initialized]"

    if not japanese_text.strip():
        return ""

    try:
        # Tokenize the input text
        inputs = tokenizer(japanese_text, return_tensors="pt", padding=True, truncation=True)
        
        # Move inputs to the model's device (GPU or CPU)
        device = model.device
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Generate the translation, specifying the target language
        translated_ids = model.generate(
            **inputs, 
            forced_bos_token_id=tokenizer.lang_code_to_id[TARGET_LANG]
        )

        # Decode the translated IDs back to text
        english_text = tokenizer.decode(translated_ids.squeeze(), skip_special_tokens=True)
        
        return english_text
    except Exception as e:
        print(f"Error during translation: {e}")
        return f"[Translation Error: {e}]"

if __name__ == '__main__':
    # Example usage for testing
    sample_japanese = [
        "こんにちは、世界！", # Hello, world!
        "これは漫画の翻訳プロジェクトです。", # This is a manga translation project.
        "私はソフトウェアエンジニアです。", # I am a software engineer.
        "お腹が空いた。", # I'm hungry.
        "" # Empty string test
    ]

    try:
        initialize_translation_model()
    except Exception:
        print("Skipping translation test due to model initialization failure.")
        exit()
    
    print("\n--- Translation Test ---")
    for text in sample_japanese:
        if text:
            english_text = translate_japanese_to_english(text)
            print(f"Japanese: {text}")
            print(f"English:  {english_text}\n")
        else:
            print("Japanese: (empty string)")
            print("English:  (empty string)\n")