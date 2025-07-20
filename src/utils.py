
# src/utils.py - COMPLETE VERSION WITH ALL REQUIRED FUNCTIONS

import logging
import os
import json
import re
from pathlib import Path
from typing import Dict, Any, List

def setup_logging():
    """Setup logging for Streamlit Cloud compatibility"""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging with fallback for Streamlit Cloud
    try:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/app.log'),
                logging.StreamHandler()  # Also log to console
            ]
        )
    except (PermissionError, FileNotFoundError):
        # Fallback for Streamlit Cloud - only console logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()  # Console only
            ]
        )
    
    return logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Clean and normalize text for processing - REQUIRED BY text_processor.py"""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep basic punctuation and Devanagari
    # Keep: letters, numbers, spaces, basic punctuation, Devanagari script (U+0900-U+097F)
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\'\"।॥ॐ\u0900-\u097F]', ' ', text)
    
    # Remove multiple punctuation marks
    text = re.sub(r'[\.]{2,}', '.', text)
    text = re.sub(r'[\,]{2,}', ',', text)
    text = re.sub(r'[\।]{2,}', '।', text)  # Devanagari danda
    
    # Final cleanup
    text = text.strip()
    
    return text

def normalize_text(text: str) -> str:
    """Normalize text for better processing"""
    if not text:
        return ""
    
    # Clean first
    text = clean_text(text)
    
    # Convert to lowercase (but preserve Devanagari characters)
    normalized = ""
    for char in text:
        if char.isascii() and char.isalpha():
            normalized += char.lower()
        else:
            normalized += char
    
    return normalized

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text"""
    if not text:
        return []
    
    # Clean text first
    text = clean_text(text)
    
    # Split into words
    words = text.split()
    
    # Remove common stop words (English and Hindi)
    stop_words = {
        # English stop words
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
        # Hindi stop words
        'का', 'की', 'के', 'में', 'से', 'को', 'पर', 'और', 'या', 'है', 'हैं', 'था', 'थे',
        'एक', 'यह', 'वह', 'जो', 'कि', 'ने', 'तो', 'भी', 'नहीं', 'कर', 'कार्य'
    }
    
    # Filter words
    keywords = []
    for word in words:
        # Keep words longer than 2 characters and not in stop words
        if len(word) > 2 and word.lower() not in stop_words:
            keywords.append(word)
    
    # Get unique keywords and limit count
    unique_keywords = list(set(keywords))
    
    return unique_keywords[:max_keywords]

def save_json(data: Dict[str, Any], filepath: str) -> bool:
    """Save data as JSON with error handling"""
    try:
        # Create directory if it doesn't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logging.error(f"Failed to save JSON to {filepath}: {e}")
        return False

def load_json(filepath: str) -> Dict[str, Any]:
    """Load data from JSON with error handling"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"JSON file not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in {filepath}: {e}")
        return {}
    except Exception as e:
        logging.error(f"Failed to load JSON from {filepath}: {e}")
        return {}

def ensure_dir(directory: str) -> bool:
    """Ensure directory exists - Streamlit Cloud compatible"""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except (PermissionError, OSError):
        # On Streamlit Cloud, some directories can't be created
        logging.warning(f"Cannot create directory {directory} - using fallback")
        return False

def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks for better processing"""
    if not text or len(text) <= chunk_size:
        return [text] if text else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # If this isn't the last chunk, try to end at a sentence boundary
        if end < len(text):
            # Look for sentence endings near the chunk boundary
            for i in range(end - 50, end + 50):
                if i < len(text) and text[i] in '.।॥\n':
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start forward with overlap
        start = end - overlap
        
        # Avoid infinite loop
        if start <= 0:
            start = end
    
    return chunks

def clean_devanagari_text(text: str) -> str:
    """Specific cleaning for Devanagari/Hindi text"""
    if not text:
        return ""
    
    # Remove extra spaces around Devanagari punctuation
    text = re.sub(r'\s+([।॥])\s+', r'\1 ', text)
    
    # Normalize Devanagari numerals if needed
    # text = re.sub(r'[०-९]', lambda m: str(ord(m.group()) - ord('०')), text)
    
    # Remove unwanted characters but keep Devanagari
    text = re.sub(r'[^\u0900-\u097F\w\s\.\,\;\:\!\?\-\'\"।॥]', ' ', text)
    
    return clean_text(text)
