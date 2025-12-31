"""
Text processing utilities for direct text input.
"""
import logging

def process_text_input(text: str) -> dict:
    """
    Process direct text input.
    Returns dict with 'text' and metadata.
    """
    logging.info(f'=== Processing direct text input ===')
    
    if not text or not text.strip():
        logging.error("Empty text provided")
        return None
    
    text = text.strip()
    
    if len(text) < 50:
        logging.error(f"Text too short: {len(text)} characters (minimum 50)")
        return None
    
    word_count = len(text.split())
    char_count = len(text)
    
    logging.info(f"Processed text: {char_count} characters, {word_count} words")
    
    return {
        'text': text,
        'word_count': word_count,
        'char_count': char_count,
        'source': 'direct_text'
    }
