
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
        
    def process_texts(self, texts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process all texts into chunks"""
        processed_chunks = []
        
        for text in texts:
            chunks = self.chunk_text(text)
            processed_chunks.extend(chunks)
        
        logger.info(f"Created {len(processed_chunks)} text chunks")
        return processed_chunks
    
    def chunk_text(self, text_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split text into chunks maintaining context"""
        content = text_data["content"]
        metadata = text_data["metadata"]
        
        # Combine all text for chunking
        full_text = content.get("text", "")
        
        if len(full_text) <= self.chunk_size:
            # Text is small enough, return as single chunk
            return [{
                "content": content,
                "metadata": {**metadata, "chunk_id": 0},
                "chunk_text": full_text
            }]
        
        # Split into chunks
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(full_text):
            end = start + self.chunk_size
            
            if end < len(full_text):
                # Find good breaking point
                end = self._find_break_point(full_text, end)
            else:
                end = len(full_text)
            
            chunk_text = full_text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    "content": content,
                    "metadata": {**metadata, "chunk_id": chunk_id},
                    "chunk_text": chunk_text
                })
                chunk_id += 1
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def _find_break_point(self, text: str, position: int) -> int:
        """Find good breaking point near position"""
        # Look for sentence endings
        sentence_endings = ['।', '॥', '.', '!', '?', '\n']
        
        # Search backwards for sentence ending
        for i in range(position, max(0, position - 100), -1):
            if text[i] in sentence_endings:
                return i + 1
        
        # Search forwards for sentence ending
        for i in range(position, min(len(text), position + 100)):
            if text[i] in sentence_endings:
                return i + 1
        
        # Fallback: look for word boundary
        for i in range(position, max(0, position - 50), -1):
            if text[i] == ' ':
                return i
        
        return position
    
    def detect_language(self, text: str) -> str:
        """Detect text language"""
        try:
            lang = detect(text)
            if lang == 'hi':
                return 'hindi'
            elif lang == 'en':
                return 'english'
            else:
                # Check for Sanskrit/Devanagari
                if re.search(r'[\u0900-\u097F]', text):
                    return 'sanskrit'
                return 'english'
        except:
            return 'english'
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for better search"""
        text = clean_text(text)
        
        # Add concept mappings for better search
        concept_mappings = {
            'dharma': 'dharma धर्म righteous duty',
            'karma': 'karma कर्म action deed',
            'moksha': 'moksha मोक्ष liberation salvation',
            'bhakti': 'bhakti भक्ति devotion love',
            'yoga': 'yoga योग union meditation',
            'gyana': 'gyana ज्ञान knowledge wisdom'
        }
        
        for english, expanded in concept_mappings.items():
            if english.lower() in text.lower():
                text += f" {expanded}"
        
        return text
