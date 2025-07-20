
# src/rag_chain.py - ULTRA SIMPLE TEST VERSION

import streamlit as st
from typing import Dict, List, Any

class KalkiRAGChain:
    """Ultra simple version for testing"""
    
    def __init__(self):
        self.is_initialized = False
        self.sample_data = {
            "ramcharitmanas_1": {
                "hindi": "धर्म की रक्षा करना हमारा कर्तव्य है।",
                "english": "It is our duty to protect dharma.",
                "collection": "Ramcharitmanas"
            },
            "valmiki_1": {
                "hindi": "सत्य और धर्म का पालन करो।",
                "english": "Follow truth and righteousness.",
                "collection": "Valmiki Ramayana"
            }
        }
    
    def initialize(self) -> bool:
        """Instant initialization with sample data"""
        try:
            st.info("🚀 Quick test initialization...")
            
            # Skip JSON loading completely - use sample data
            self.is_initialized = True
            st.success("✅ Test data loaded instantly!")
            return True
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            return False
    
    def ask(self, question: str, scripture_filter: str = "All Texts", language_pref: str = "All Languages") -> Dict[str, Any]:
        """Instant response with sample data"""
        
        if not self.is_initialized:
            return {"error": "Please initialize system first"}
        
        # INSTANT RESPONSE - NO PROCESSING
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['dharma', 'duty', 'life']):
            response = """Based on Hindu scriptures:

**About Dharma and Life:**
Dharma means righteous duty. According to Ramcharitmanas: "धर्म की रक्षा करना हमारा कर्तव्य है" (It is our duty to protect dharma).

The Valmiki Ramayana teaches: "सत्य और धर्म का पालन करो" (Follow truth and righteousness).

Living according to dharma brings peace and spiritual progress."""

            sources = [
                {
                    'content': self.sample_data['ramcharitmanas_1'],
                    'metadata': {
                        'collection_display': 'Ramcharitmanas',
                        'source_file': 'sample_data'
                    },
                    'similarity_score': 0.9
                }
            ]
        
        else:
            response = f"""I understand your question about "{question}".

Based on Hindu scriptures, the key principles are:
- Follow dharma (righteous duty)
- Practice devotion and surrender to God
- Live with compassion and truth
- Serve others selflessly

These teachings come from sacred texts like Ramcharitmanas and Valmiki Ramayana."""

            sources = [
                {
                    'content': self.sample_data['valmiki_1'],
                    'metadata': {
                        'collection_display': 'Valmiki Ramayana',
                        'source_file': 'sample_data'
                    },
                    'similarity_score': 0.8
                }
            ]
        
        return {
            "response": response,
            "sources": sources,
            "query": question
        }
    
    def get_system_stats(self):
        """Test stats"""
        return {
            "status": "Test Mode",
            "total_texts": 2,
            "search_method": "Sample Data Test",
            "collections": {"Ramcharitmanas": 1, "Valmiki Ramayana": 1}
        }
    
    def rebuild_index(self):
        """Test rebuild"""
        return True
    
    def get_sample_questions(self):
        """Sample questions"""
        return [
            "What is dharma?",
            "What is the meaning of life?",
            "How to live spiritually?",
            "What are Ram's teachings?"
        ]
