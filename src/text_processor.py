
from typing import List, Dict, Any
import re
from langdetect import detect
from src.utils import clean_text, setup_logging
from config import Config

logger = setup_logging()

class TextProcessor:
    """Process and chunk text for embeddings"""
    
    def __init__(self):
        self.chunk_size = Config.CHUNK_SIZE
        self.chunk_overlap = Config.CHUNK_OVERLAP
        
    def process_texts(self, texts: List[Dict[str, Any]])
