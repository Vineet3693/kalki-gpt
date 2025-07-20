
# src/rag_chain.py - MINIMAL WORKING VERSION

import streamlit as st
from typing import Dict, List, Any
import logging
from src.data_loader import get_all_scripture_data
from src.utils import setup_logging

logger = setup_logging()

class KalkiRAGChain:
    """Minimal working RAG Chain for immediate responses"""
    
    def __init__(self):
        self.texts = None
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """Simple initialization"""
        try:
            st.info("🚀 Loading scripture data...")
            
            # Load data from GitHub
            raw_data = get_all_scripture_data()
            
            if not raw_data:
                st.error("❌ No data loaded")
                return False
            
            # Convert to simple format
            self.texts = []
            for filename, content in raw_data.items():
                if isinstance(content, list):
                    for i, item in enumerate(content):
                        self.texts.append({
                            'filename': filename,
                            'content': item,
                            'collection': self._get_collection(filename),
                            'id': f"{filename}_{i}"
                        })
                else:
                    self.texts.append({
                        'filename': filename,
                        'content': content,
                        'collection': self._get_collection(filename),
                        'id': filename
                    })
            
            self.is_initialized = True
            st.success(f"✅ Loaded {len(self.texts)} text items!")
            return True
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            return False
    
    def _get_collection(self, filename):
        """Simple collection detection"""
        filename_lower = filename.lower()
        if 'ramcharit' in filename_lower:
            return 'Ramcharitmanas'
        elif 'valmiki' in filename_lower:
            return 'Valmiki Ramayana'
        else:
            return 'Other'
    
    def ask(self, question: str, scripture_filter: str = "All Texts", language_pref: str = "All Languages") -> Dict[str, Any]:
        """Simple question answering"""
        
        if not self.is_initialized:
            return {"error": "Please initialize system first"}
        
        if not question.strip():
            return {"error": "Please enter a question"}
        
        try:
            st.info("🔍 Searching for answers...")
            
            # Simple keyword search
            question_words = question.lower().split()
            matches = []
            
            for text_item in self.texts:
                # Filter by collection
                if scripture_filter != "All Texts" and scripture_filter not in text_item['collection']:
                    continue
                
                # Get text content
                content = text_item['content']
                if isinstance(content, dict):
                    # Try different fields
                    text_to_search = ""
                    for field in ['text', 'english', 'hindi', 'content', 'meaning', 'verse']:
                        if field in content:
                            text_to_search += str(content[field]) + " "
                else:
                    text_to_search = str(content)
                
                text_to_search = text_to_search.lower()
                
                # Count word matches
                word_matches = sum(1 for word in question_words if word in text_to_search)
                
                if word_matches > 0:
                    matches.append({
                        'content': content,
                        'collection': text_item['collection'],
                        'filename': text_item['filename'],
                        'score': word_matches,
                        'text_preview': text_to_search[:200] + "..."
                    })
            
            # Sort by relevance
            matches.sort(key=lambda x: x['score'], reverse=True)
            matches = matches[:3]  # Top 3 results
            
            if not matches:
                return {
                    "response": f"I couldn't find information about '{question}' in the loaded scriptures. Try asking about dharma, devotion, spiritual life, or Ram's teachings.",
                    "sources": [],
                    "query": question
                }
            
            # Create simple response
            response_parts = [
                f"Based on the Hindu scriptures, here's what I found about '{question}':\n"
            ]
            
            for i, match in enumerate(matches, 1):
                collection = match['collection']
                content = match['content']
                
                # Extract best content
                if isinstance(content, dict):
                    text = ""
                    # Try English first, then others
                    for field in ['english', 'text', 'meaning', 'content']:
                        if field in content and content[field]:
                            text = str(content[field])[:300]
                            break
                    
                    if not text and 'hindi' in content:
                        text = str(content['hindi'])[:300]
                else:
                    text = str(content)[:300]
                
                if text:
                    response_parts.append(f"\n**{i}. From {collection}:**\n{text}...")
            
            response_parts.append(f"\n\n*Found {len(matches)} relevant passages from the scriptures.*")
            
            # Prepare sources for display
            sources = []
            for match in matches:
                sources.append({
                    'content': match['content'],
                    'metadata': {
                        'collection_display': match['collection'],
                        'source_file': match['filename']
                    },
                    'similarity_score': match['score'] / 10  # Normalize score
                })
            
            return {
                "response": "".join(response_parts),
                "sources": sources,
                "query": question
            }
            
        except Exception as e:
            st.error(f"❌ Search error: {str(e)}")
            return {
                "error": f"Error processing question: {str(e)}",
                "query": question
            }
    
    def rebuild_index(self):
        """Rebuild - just reinitialize"""
        self.is_initialized = False
        return self.initialize()
    
    def get_system_stats(self):
        """Get basic stats"""
        if not self.is_initialized:
            return {"status": "Not initialized"}
        
        collections = {}
        for text in self.texts:
            collection = text['collection']
            collections[collection] = collections.get(collection, 0) + 1
        
        return {
            "status": "Initialized",
            "total_texts": len(self.texts),
            "search_method": "Simple Keyword Search",
            "collections": collections
        }
    
    def get_sample_questions(self):
        """Sample questions"""
        return [
            "What is dharma?",
            "Tell me about devotion",
            "How to live a spiritual life?",
            "What are Ram's teachings?",
            "What is the importance of guru?",
            "How to overcome difficulties?",
            "What is true bhakti?",
            "What are Hanuman's qualities?"
        ]
