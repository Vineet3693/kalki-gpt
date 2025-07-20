
import re
from typing import Dict, List, Any
from src.multilingual import MultilingualProcessor
from src.utils import setup_logging

logger = setup_logging()

class QueryProcessor:
    """Process and expand user queries for better search results"""
    
    def __init__(self):
        self.multilingual = MultilingualProcessor()
        
        # Scripture-specific terms
        self.scripture_keywords = {
            'bhagavad_gita': ['krishna', 'arjuna', 'gita', 'kurukshetra', 'dharma'],
            'ramayana': ['rama', 'sita', 'hanuman', 'ravana', 'lanka'],
            'mahabharata': ['pandava', 'kaurava', 'yudhishthira', 'bhima', 'arjuna'],
            'rigveda': ['indra', 'agni', 'soma', 'mantra', 'hymn'],
            'ramcharitmanas': ['tulsidas', 'awadhi', 'chaupai', 'doha'],
            'vedas': ['mantra', 'sukta', 'rishi', 'yajna', 'sacrifice']
        }
        
        # Thematic keywords
        self.themes = {
            'devotion': ['bhakti', 'love', 'surrender', 'worship', 'prayer'],
            'dharma': ['duty', 'righteousness', 'moral', 'ethics', 'virtue'],
            'karma': ['action', 'deed', 'work', 'consequence', 'result'],
            'moksha': ['liberation', 'salvation', 'freedom', 'enlightenment'],
            'meditation': ['dhyana', 'yoga', 'concentration', 'mindfulness'],
            'knowledge': ['gyana', 'wisdom', 'understanding', 'learning']
        }
    
    def process_query(self, query: str, scripture_filter: str = "All Texts") -> Dict[str, Any]:
        """Process user query with context and expansion"""
        
        # Basic cleaning
        processed_query = self._clean_query(query)
        
        # Detect language
        language = self.multilingual.detect_language(processed_query)
        
        # Expand with multilingual terms
        expanded_query = self.multilingual.expand_query(processed_query)
        
        # Add thematic context
        thematic_query = self._add_thematic_context(expanded_query)
        
        # Add scripture-specific context
        if scripture_filter != "All Texts":
            contextual_query = self._add_scripture_context(thematic_query, scripture_filter)
        else:
            contextual_query = thematic_query
        
        return {
            "original": query,
            "processed": processed_query,
            "expanded": contextual_query,
            "language": language,
            "scripture_filter": scripture_filter,
            "keywords": self._extract_keywords(contextual_query)
        }
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize query"""
        # Remove extra whitespace
        query = " ".join(query.split())
        
        # Convert to lowercase for processing (but preserve original for display)
        query_lower = query.lower()
        
        # Handle common variations
        replacements = {
            'krishna': 'krishna kṛṣṇa कृष्ण',
            'rama': 'rama rāma राम',
            'shiva': 'shiva śiva शिव',
            'vishnu': 'vishnu viṣṇu विष्णु',
            'hanuman': 'hanuman हनुमान',
            'gita': 'gita gītā गीता',
            'veda': 'veda वेद',
            'yoga': 'yoga योग',
            'dharma': 'dharma धर्म',
            'karma': 'karma कर्म'
        }
        
        for key, value in replacements.items():
            if key in query_lower:
                query += f" {value}"
        
        return query
    
    def _add_thematic_context(self, query: str) -> str:
        """Add thematic context to query"""
        query_lower = query.lower()
        
        for theme, keywords in self.themes.items():
            for keyword in keywords:
                if keyword in query_lower:
                    # Add related terms
                    related_terms = [k for k in keywords if k != keyword][:3]
                    query += f" {' '.join(related_terms)}"
                    break
        
        return query
    
    def _add_scripture_context(self, query: str, scripture: str) -> str:
        """Add scripture-specific context"""
        scripture_key = scripture.lower().replace(" ", "_")
        
        # Map UI names to internal keys
        scripture_mapping = {
            "bhagavad_gita": ["bhagavad gita", "gita"],
            "ramayana": ["ramayana", "valmiki ramayana"],
            "mahabharata": ["mahabharata"],
            "rigveda": ["rigveda", "rig veda"],
            "ramcharitmanas": ["ramcharitmanas", "tulsidas"]
        }
        
        for key, names in scripture_mapping.items():
            if any(name in scripture.lower() for name in names):
                if key in self.scripture_keywords:
                    context_terms = self.scripture_keywords[key][:3]
                    query += f" {' '.join(context_terms)}"
                break
        
        return query
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract key terms from query"""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'within',
            'what', 'which', 'who', 'when', 'where', 'why', 'how', 'that', 'this',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'can', 'must', 'shall', 'say', 'says', 'said', 'tell', 'tells', 'told'
        }
        
        # Extract words
        words = re.findall(r'\b\w+\b', query.lower())
        
        # Filter stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Add Devanagari terms
        devanagari_terms = re.findall(r'[\u0900-\u097F]+', query)
        keywords.extend(devanagari_terms)
        
        return list(set(keywords))
    
    def suggest_related_queries(self, original_query: str) -> List[str]:
        """Suggest related queries based on the original"""
        suggestions = []
        
        query_lower = original_query.lower()
        
        # Thematic suggestions
        if any(word in query_lower for word in ['dharma', 'duty', 'righteousness']):
            suggestions.extend([
                "What is dharma according to Krishna?",
                "How is dharma described in Ramayana?",
                "Difference between svadharma and dharma"
            ])
        
        if any(word in query_lower for word in ['karma', 'action', 'deed']):
            suggestions.extend([
                "What is karma yoga in Bhagavad Gita?",
                "How does karma work according to Hindu scriptures?",
                "Types of karma mentioned in texts"
            ])
        
        if any(word in query_lower for word in ['meditation', 'dhyana', 'yoga']):
            suggestions.extend([
                "Meditation techniques in Hindu scriptures",
                "What is dhyana yoga?",
                "How to practice yoga according to Gita?"
            ])
        
        # Character-based suggestions
        if any(word in query_lower for word in ['krishna', 'kṛṣṇa']):
            suggestions.extend([
                "Krishna's teachings on devotion",
                "Krishna's advice to Arjuna",
                "Stories of Krishna from Mahabharata"
            ])
        
        if any(word in query_lower for word in ['rama', 'rāma']):
            suggestions.extend([
                "Rama's qualities as ideal king",
                "Rama's devotion to dharma",
                "Difference between Valmiki and Tulsidas Ramayana"
            ])
        
        return suggestions[:5]  # Return top 5 suggestions
