
# src/utils.py - REPLACE THE setup_logging FUNCTION:

import logging
import os
import json
from pathlib import Path
from typing import Dict, Any

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
