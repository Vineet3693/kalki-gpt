
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def ensure_dir(path: str):
    """Ensure directory exists"""
    Path(path).mkdir(parents=True, exist_ok=True)

def load_json(file_path: str) -> Optional[Dict]:
    """Load JSON file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON file {file_path}: {e}")
        return None

def save_json(data: Dict, file_path: str):
    """Save data to JSON file"""
    try:
        ensure_dir(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Error saving JSON file {file_path}: {e}")

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove special characters but keep Devanagari
    import re
    text = re.sub(r'[^\w\s\u0900-\u097F।॥]', '', text)
    
    return text.strip()

def get_file_size(file_path: str) -> str:
    """Get human readable file size"""
    try:
        size = os.path.getsize(file_path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except:
        return "Unknown"
