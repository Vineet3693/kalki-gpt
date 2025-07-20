
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import streamlit as st
from src.utils import setup_logging, clean_text, load_json

logger = setup_logging()

class DharmicDataLoader:
    """Load and process Hindu scripture JSON files"""
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.scripture_collections = {
            "AtharvaVeda": "atharvaveda",
            "Mahabharata": "mahabharata",
            "Ramcharitmanas": "ramcharitmanas",
            "Rigveda": "rigveda",
            "SrimadBhagvadGita": "bhagavad_gita",
            "ValmikiRamayana": "valmiki_ramayana",
            "Yajurveda": "yajurveda"
        }
    
    @st.cache_data
    def load_all_texts(_self) -> List[Dict[str, Any]]:
        """Load all scripture texts with caching"""
        all_texts = []
        
        for folder_name, collection_id in _self.scripture_collections.items():
            folder_path = _self.data_path / folder_name
            
            if not folder_path.exists():
                logger.warning(f"Folder not found: {folder_path}")
                continue
                
            texts = _self._load_collection(folder_path, collection_id)
            all_texts.extend(texts)
            logger.info(f"Loaded {len(texts)} texts from {folder_name}")
        
        logger.info(f"Total texts loaded: {len(all_texts)}")
        return all_texts
    
    def _load_collection(self, folder_path: Path, collection_id: str) -> List[Dict[str, Any]]:
        """Load texts from a specific collection folder"""
        texts = []
        
        for json_file in folder_path.glob("*.json"):
            try:
                data = load_json(str(json_file))
                if data:
                    processed_texts = self._process_json_data(
                        data, collection_id, json_file.stem
                    )
                    texts.extend(processed_texts)
            except Exception as e:
                logger.error(f"Error loading {json_file}: {e}")
        
        return texts
    
    def _process_json_data(self, data: Any, collection: str, file_name: str) -> List[Dict[str, Any]]:
        """Process JSON data into structured format"""
        texts = []
        
        if isinstance(data, list):
            for i, item in enumerate(data):
                processed_item = self._extract_text_content(item, collection, file_name, i)
                if processed_item:
                    texts.append(processed_item)
        
        elif isinstance(data, dict):
            # Handle different JSON structures
            if 'verses' in data or 'shlokas' in data:
                verses_key = 'verses' if 'verses' in data else 'shlokas'
                for i, verse in enumerate(data[verses_key]):
                    processed_item = self._extract_text_content(verse, collection, file_name, i)
                    if processed_item:
                        texts.append(processed_item)
            else:
                processed_item = self._extract_text_content(data, collection, file_name, 0)
                if processed_item:
                    texts.append(processed_item)
        
        return texts
    
    def _extract_text_content(self, item: Any, collection: str, file_name: str, index: int) -> Dict[str, Any]:
        """Extract and structure text content from JSON item"""
        if isinstance(item, str):
            return {
                "content": {
                    "text": clean_text(item),
                    "sanskrit": "",
                    "hindi": "",
                    "english": clean_text(item)
                },
                "metadata": {
                    "collection": collection,
                    "file": file_name,
                    "verse_id": f"{collection}_{file_name}_{index}",
                    "index": index
                }
            }
        
        elif isinstance(item, dict):
            # Extract multilingual content
            content = self._extract_multilingual_content(item)
            
            return {
                "content": content,
                "metadata": {
                    "collection": collection,
                    "file": file_name,
                    "verse_id": f"{collection}_{file_name}_{index}",
                    "index": index,
                    "chapter": item.get("chapter", ""),
                    "verse_number": item.get("verse", item.get("verse_number", "")),
                    "speaker": item.get("speaker", "")
                }
            }
        
        return None
    
    def _extract_multilingual_content(self, item: Dict[str, Any]) -> Dict[str, str]:
        """Extract multilingual content from item"""
        # Common field mappings
        sanskrit_fields = ["sanskrit", "sloka", "original", "devanagari"]
        hindi_fields = ["hindi", "hindi_translation", "meaning_hindi"]
        english_fields = ["english", "translation", "meaning", "text"]
        
        content = {
            "sanskrit": "",
            "hindi": "",
            "english": "",
            "text": ""
        }
        
        # Extract Sanskrit
        for field in sanskrit_fields:
            if field in item and item[field]:
                content["sanskrit"] = clean_text(str(item[field]))
                break
        
        # Extract Hindi
        for field in hindi_fields:
            if field in item and item[field]:
                content["hindi"] = clean_text(str(item[field]))
                break
        
        # Extract English
        for field in english_fields:
            if field in item and item[field]:
                content["english"] = clean_text(str(item[field]))
                break
        
        # Create combined text for search
        combined_parts = []
        if content["sanskrit"]:
            combined_parts.append(content["sanskrit"])
        if content["hindi"]:
            combined_parts.append(content["hindi"])
        if content["english"]:
            combined_parts.append(content["english"])
        
        content["text"] = " ".join(combined_parts) if combined_parts else str(item)
        
        return content
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics for each collection"""
        stats = {}
        texts = self.load_all_texts()
        
        for text in texts:
            collection = text["metadata"]["collection"]
            stats[collection] = stats.get(collection, 0) + 1
        
        return stats
