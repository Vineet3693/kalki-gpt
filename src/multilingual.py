
import re
from typing import Dict, List, Any
from langdetect import detect
from src.utils import setup_logging

logger = setup_logging()

class MultilingualProcessor:
    """Handle multilingual text processing and language detection"""
    
    def __init__(self):
        self.language_patterns = {
            'sanskrit': r'[\u0900-\u097F]',  # Devanagari
            'hindi': r'[\u0900-\u097F]',     # Also Devanagari
            'english': r'[a-zA-Z]'
        }
        
        self.concept_translations = {
            'dharma': {'hindi': 'धर्म', 'sanskrit': 'धर्म', 'english': 'righteousness'},
            'karma': {'hindi': 'कर्म', 'sanskrit': 'कर्म', 'english': 'action'},
            'moksha': {'hindi': 'मोक्ष', 'sanskrit': 'मोक्ष', 'english': 'liberation'},
            'bhakti': {'hindi': 'भक्ति', 'sanskrit': 'भक्ति', 'english': 'devotion'},
            'yoga': {'hindi': 'योग', 'sanskrit': 'योग', 'english': 'union'},
            'gyana': {'hindi': 'ज्ञान', 'sanskrit': 'ज्ञान', 'english': 'knowledge'}
        }
    
    def detect_language(self, text: str) -> str:
        """Detect primary language of text"""
        try:
            # Use langdetect for basic detection
            detected = detect(text)
            
            # Check for Devanagari script
            if re.search(self.language_patterns['sanskrit'], text):
                # Distinguish between Sanskrit and Hindi
                sanskrit_indicators = ['श्लोक', 'मन्त्र', 'ॐ', '॥']
                if any(indicator in text for indicator in sanskrit_indicators):
                    return 'sanskrit'
                return 'hindi'
            
            return 'english' if detected == 'en' else detected
            
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return 'english'
    
    def expand_query(self, query: str) -> str:
        """Expand query with multilingual concepts"""
        expanded_query = query
        
        for concept, translations in self.concept_translations.items():
            if concept.lower() in query.lower():
                # Add all translations
                all_forms = [translations['hindi'], translations['sanskrit'], translations['english']]
                expanded_query += " " + " ".join(all_forms)
        
        return expanded_query
    
    def format_multilingual_text(self, content: Dict[str, str], language_preference: str = "all") -> Dict[str, str]:
        """Format text according to language preference"""
        formatted = {}
        
        if language_preference == "all" or language_preference == "🌍 All Languages":
            formatted = {
                "sanskrit": content.get("sanskrit", ""),
                "hindi": content.get("hindi", ""),
                "english": content.get("english", ""),
                "combined": content.get("text", "")
            }
        elif language_preference == "🇮🇳 Hindi":
            formatted = {
                "primary": content.get("hindi", ""),
                "secondary": content.get("english", ""),
                "original": content.get("sanskrit", "")
            }
        elif language_preference == "🇬🇧 English":
            formatted = {
                "primary": content.get("english", ""),
                "secondary": content.get("hindi", ""),
                "original": content.get("sanskrit", "")
            }
        elif language_preference == "🕉️ Sanskrit":
            formatted = {
                "primary": content.get("sanskrit", ""),
                "secondary": content.get("hindi", ""),
                "translation": content.get("english", "")
            }
        
        return formatted
    
    def transliterate_devanagari(self, text: str) -> str:
        """Basic transliteration from Devanagari to Roman"""
        # Simple character mapping for basic transliteration
        transliteration_map = {
            'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ii', 'उ': 'u', 'ऊ': 'uu',
            'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
            'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha', 'ङ': 'nga',
            'च': 'cha', 'छ': 'chha', 'ज': 'ja', 'झ': 'jha', 'ञ': 'nja',
            'ट': 'ta', 'ठ': 'tha', 'ड': 'da', 'ढ': 'dha', 'ण': 'na',
            'त': 'ta', 'थ': 'tha', 'द': 'da', 'ध': 'dha', 'न': 'na',
            'प': 'pa', 'फ': 'pha', 'ब': 'ba', 'भ': 'bha', 'म': 'ma',
            'य': 'ya', 'र': 'ra', 'ल': 'la', 'व': 'va',
            'श': 'sha', 'ष': 'sha', 'स': 'sa', 'ह': 'ha',
            'ं': 'm', 'ः': 'h', '्': '', '।': '.', '॥': '||'
        }
        
        transliterated = ""
        for char in text:
            transliterated += transliteration_map.get(char, char)
        
        return transliterated
