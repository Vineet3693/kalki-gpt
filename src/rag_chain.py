
# src/rag_chain.py - FAST VERSION WITHOUT EMBEDDINGS

import streamlit as st
from typing import Dict, List, Any, Optional
import os
from src.data_loader import DharmicDataLoader, get_all_scripture_data
from src.text_processor import TextProcessor
from src.query_processor import QueryProcessor
from src.llm_handler import LLMHandler
from src.response_formatter import ResponseFormatter
from src.utils import setup_logging
from config import Config

logger = setup_logging()

class KalkiRAGChain:
    """Fast RAG Chain without slow embeddings"""
    
    def __init__(self):
        self.data_loader = DharmicDataLoader()
        self.text_processor = TextProcessor()
        self.query_processor = QueryProcessor()
        self.llm_handler = LLMHandler()
        self.response_formatter = ResponseFormatter()
        
        self.texts = None
        self.is_initialized = False
    
    def initialize(self, force_rebuild: bool = False) -> bool:
        """Fast initialization without embeddings"""
        try:
            logger.info("🚀 Starting fast initialization...")
            
            with st.spinner("📥 Loading sacred texts from GitHub..."):
                # Use local GitHub files instead of Google Drive
                raw_data = get_all_scripture_data()
                if not raw_data:
                    st.error("❌ Failed to load scripture data from GitHub")
                    return False
                
                # Convert to the format expected by text processor
                self.texts = self._convert_data_format(raw_data)
                logger.info(f"✅ Loaded {len(self.texts)} texts")
                st.success(f"📚 Loaded {len(self.texts)} text items from scriptures!")
            
            with st.spinner("🔄 Processing texts for search..."):
                # Simple text processing without heavy operations
                processed_texts = self._simple_process_texts(self.texts)
                self.texts = processed_texts
                logger.info(f"✅ Processed {len(processed_texts)} text chunks")
            
            self.is_initialized = True
            st.success("✅ Fast initialization complete! Ready to answer questions.")
            logger.info("🎉 RAG Chain initialization complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing RAG Chain: {e}")
            st.error(f"❌ Failed to initialize system: {e}")
            return False
    
    def _simple_process_texts(self, texts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simple text processing without heavy operations"""
        processed_texts = []
        
        for text in texts:
            try:
                content = text.get('content', {})
                
                # Extract text content for search
                search_text = ""
                if isinstance(content, dict):
                    for field in ['text', 'english', 'hindi', 'content', 'verse', 'meaning']:
                        if field in content and content[field]:
                            search_text += str(content[field]) + " "
                else:
                    search_text = str(content)
                
                # Add search text to the item
                text['search_text'] = search_text.strip().lower()
                processed_texts.append(text)
                
            except Exception as e:
                logger.error(f"Error processing text item: {e}")
                continue
        
        return processed_texts
    
    def _convert_data_format(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert raw GitHub data to expected format"""
        converted_texts = []
        
        for filename, file_content in raw_data.items():
            try:
                # Handle different data structures
                if isinstance(file_content, list):
                    # If file content is a list of items
                    for idx, item in enumerate(file_content):
                        converted_item = {
                            "id": f"{filename}_{idx}",
                            "content": item if isinstance(item, dict) else {"text": str(item)},
                            "metadata": {
                                "collection": self._get_collection_name(filename),
                                "collection_display": self._get_collection_display_name(filename),
                                "source_file": filename,
                                "item_index": idx,
                                "total_items": len(file_content)
                            }
                        }
                        converted_texts.append(converted_item)
                
                elif isinstance(file_content, dict):
                    # If file content is a single dictionary
                    converted_item = {
                        "id": filename,
                        "content": file_content,
                        "metadata": {
                            "collection": self._get_collection_name(filename),
                            "collection_display": self._get_collection_display_name(filename),
                            "source_file": filename,
                            "item_index": 0,
                            "total_items": 1
                        }
                    }
                    converted_texts.append(converted_item)
                
                else:
                    # Handle other data types as text
                    converted_item = {
                        "id": filename,
                        "content": {"text": str(file_content)},
                        "metadata": {
                            "collection": self._get_collection_name(filename),
                            "collection_display": self._get_collection_display_name(filename),
                            "source_file": filename,
                            "item_index": 0,
                            "total_items": 1
                        }
                    }
                    converted_texts.append(converted_item)
                    
            except Exception as e:
                logger.error(f"Error processing file {filename}: {e}")
                continue
        
        return converted_texts
    
    def _get_collection_name(self, filename: str) -> str:
        """Extract collection name from filename for internal use"""
        filename_lower = filename.lower()
        
        if any(word in filename_lower for word in ['ramcharitmanas', 'ramcharit']):
            return 'ramcharitmanas'
        elif any(word in filename_lower for word in ['valmiki', 'valmikiramayana']):
            return 'valmiki_ramayana'
        elif "bhagavad" in filename_lower or "gita" in filename_lower:
            return "bhagavad_gita"
        elif "ramayana" in filename_lower:
            return "ramayana"
        elif "mahabharata" in filename_lower:
            return "mahabharata"
        else:
            return "other_texts"
    
    def _get_collection_display_name(self, filename: str) -> str:
        """Extract collection display name from filename"""
        filename_lower = filename.lower()
        
        if any(word in filename_lower for word in ['ramcharitmanas', 'ramcharit']):
            return 'Ramcharitmanas'
        elif any(word in filename_lower for word in ['valmiki', 'valmikiramayana']):
            return 'Valmiki Ramayana'
        elif "bhagavad" in filename_lower or "gita" in filename_lower:
            return "Bhagavad Gita"
        elif "ramayana" in filename_lower:
            return "Ramayana"
        elif "mahabharata" in filename_lower:
            return "Mahabharata"
        else:
            return "Other Texts"
    
    def fast_search(self, question: str, scripture_filter: str = "All Texts", max_results: int = 5):
        """Fast keyword-based search instead of embedding search"""
        
        # Process question into keywords
        question_lower = question.lower()
        question_words = set(question_lower.split())
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'what', 'how', 'why',
            'where', 'when', 'who', 'which', 'does', 'do', 'did', 'can', 'could',
            'should', 'would', 'will', 'about', 'tell', 'me', 'according', 'says',
            'का', 'की', 'के', 'में', 'से', 'को', 'और', 'है', 'हैं'
        }
        
        keywords = question_words - stop_words
        
        results = []
        
        for text_item in self.texts:
            # Apply scripture filter
            if scripture_filter != "All Texts":
                collection_display = text_item.get('metadata', {}).get('collection_display', '')
                if scripture_filter.lower() not in collection_display.lower():
                    continue
            
            # Get search text
            search_text = text_item.get('search_text', '')
            
            if not search_text.strip():
                continue
            
            # Calculate relevance score
            text_words = set(search_text.split())
            
            # Count keyword matches
            matches = 0
            bonus_matches = 0
            
            for keyword in keywords:
                if keyword in search_text:
                    matches += 1
                    # Bonus for exact word match
                    if keyword in text_words:
                        bonus_matches += 0.5
            
            total_matches = matches + bonus_matches
            
            if total_matches > 0:
                relevance_score = total_matches / len(keywords) if keywords else 0
                
                results.append({
                    'content': text_item.get('content', {}),
                    'metadata': text_item.get('metadata', {}),
                    'similarity_score': relevance_score,
                    'match_count': matches
                })
        
        # Sort by relevance (higher is better)
        results.sort(key=lambda x: (x['similarity_score'], x['match_count']), reverse=True)
        
        return results[:max_results]
    
    def ask(self, question: str, scripture_filter: str = "All Texts", 
            language_preference: str = "🌍 All Languages") -> Dict[str, Any]:
        """Ask a question using fast keyword search"""
        
        if not self.is_initialized:
            return {"error": "System not initialized. Please click 'Initialize System' first."}
        
        try:
            # Process query
            with st.spinner("🔍 Processing your question..."):
                processed_query = self.query_processor.process_query(
                    question, scripture_filter
                )
            
            # Fast search instead of embedding search
            with st.spinner("🔍 Searching scriptures..."):
                relevant_sources = self.fast_search(question, scripture_filter, max_results=5)
            
            if not relevant_sources:
                return {
                    "response": "I couldn't find relevant information about your question in the loaded scriptures. Please try rephrasing your question or asking about topics like dharma, devotion, life principles, or spiritual guidance.",
                    "sources": [],
                    "query": question,
                    "processed_query": processed_query
                }
            
            # Generate response using LLM or simple method
            with st.spinner("📝 Generating response..."):
                response_text = self._generate_response(question, relevant_sources, language_preference)
            
            return {
                "response": response_text,
                "sources": relevant_sources,
                "query": question,
                "processed_query": processed_query,
                "scripture_filter": scripture_filter,
                "search_method": "keyword_based"
            }
            
        except Exception as e:
            logger.error(f"Error in ask method: {e}")
            return {
                "error": f"An error occurred while processing your question: {str(e)}",
                "query": question
            }
    
    def _generate_response(self, question: str, sources: List[Dict], language_preference: str) -> str:
        """Generate response using LLM or simple fallback"""
        
        try:
            # Try to use LLM handler if available
            if hasattr(self.llm_handler, 'generate_response'):
                context_parts = []
                for source in sources:
                    content = source['content']
                    if isinstance(content, dict):
                        for field in ['text', 'english', 'hindi', 'content']:
                            if field in content and content[field]:
                                context_parts.append(str(content[field]))
                                break
                
                context = "\n\n".join(context_parts[:3])
                return self.llm_handler.generate_response(question, context, language_preference)
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
        
        # Fallback to simple response
        return self._create_simple_response(question, sources)
    
    def _create_simple_response(self, question: str, sources: List[Dict]) -> str:
        """Create simple response when LLM is not available"""
        
        if not sources:
            return "No relevant information found for your question."
        
        response_parts = [
            f"Based on the Hindu scriptures, here's what I found regarding '{question}':\n"
        ]
        
        for i, source in enumerate(sources[:2], 1):
            content = source.get('content', {})
            collection = source.get('metadata', {}).get('collection_display', 'Scripture')
            
            text = ""
            if isinstance(content, dict):
                # Prefer English, then other fields
                for field in ['english', 'text', 'content', 'meaning', 'hindi']:
                    if field in content and content[field]:
                        text = str(content[field])
                        # Truncate long text
                        if len(text) > 400:
                            text = text[:400] + "..."
                        break
            
            if text:
                response_parts.append(f"\n**From {collection}:**\n{text}")
        
        response_parts.append(f"\n\n*This response is based on {len(sources)} relevant passages from the Hindu scriptures.*")
        
        return "".join(response_parts)
    
    def rebuild_index(self):
        """Rebuild search index - simplified for keyword search"""
        logger.info("🔄 Rebuilding search index...")
        self.is_initialized = False
        
        # Clear Streamlit cache
        if hasattr(st, 'cache_data'):
            st.cache_data.clear()
        if hasattr(st, 'cache_resource'):
            st.cache_resource.clear()
        
        # Reinitialize
        return self.initialize(force_rebuild=True)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        if not self.is_initialized:
            return {"status": "Not initialized"}
        
        collections = {}
        if self.texts:
            for text in self.texts:
                collection = text.get('metadata', {}).get('collection_display', 'Unknown')
                collections[collection] = collections.get(collection, 0) + 1
        
        return {
            "status": "Initialized",
            "total_texts": len(self.texts) if self.texts else 0,
            "search_method": "Keyword-based (Fast)",
            "collections": collections,
            "embedding_dimension": "N/A (Not using embeddings)",
            "index_type": "Keyword Search"
        }
    
    def get_sample_questions(self) -> List[str]:
        """Get sample questions based on loaded collections"""
        base_questions = [
            "What is dharma according to Hindu scriptures?",
            "How to live a spiritual life?",
            "What is the importance of devotion?",
            "How to overcome difficulties in life?",
            "What are the qualities of a good person?"
        ]
        
        # Add collection-specific questions based on your actual data
        if self.texts:
            collections = set()
            for text in self.texts:
                collection = text.get('metadata', {}).get('collection', '')
                collections.add(collection.lower())
            
            if 'ramcharitmanas' in collections:
                base_questions.extend([
                    "What does Ramcharitmanas say about devotion?",
                    "Tell me about Hanuman's qualities",
                    "What is the importance of guru according to Tulsidas?",
                    "How does Tulsidas describe true bhakti?"
                ])
            
            if 'valmiki_ramayana' in collections:
                base_questions.extend([
                    "What are Ram's ideals in Valmiki Ramayana?",
                    "How does Ram demonstrate dharma?",
                    "What can we learn from Sita's character?",
                    "What are the lessons from Ramayana?"
                ])
        
        return base_questions[:8]  # Limit to 8 questions
    
    def search_by_keywords(self, keywords: List[str], max_results: int = 10) -> List[Dict[str, Any]]:
        """Search texts by specific keywords"""
        if not self.is_initialized or not self.texts:
            return []
        
        matching_texts = []
        
        for text in self.texts:
            search_text = text.get("search_text", "")
            content = text.get("content", {})
            
            if not search_text:
                continue
            
            # Calculate keyword match score
            matches = 0
            for keyword in keywords:
                if keyword.lower() in search_text:
                    matches += 1
            
            if matches > 0:
                text_copy = text.copy()
                text_copy["keyword_matches"] = matches
                text_copy["match_score"] = matches / len(keywords)
                matching_texts.append(text_copy)
        
        # Sort by match score
        matching_texts.sort(key=lambda x: x["match_score"], reverse=True)
        return matching_texts[:max_results]
    
    def get_collections(self) -> Dict[str, int]:
        """Get available collections and their counts"""
        collections = {}
        
        if self.texts:
            for text in self.texts:
                collection = text.get('metadata', {}).get('collection_display', 'Unknown')
                collections[collection] = collections.get(collection, 0) + 1
        
        return collections
    
    def filter_by_collection(self, collection_name: str) -> List[Dict[str, Any]]:
        """Filter texts by collection"""
        if not self.texts:
            return []
        
        filtered_texts = []
        for text in self.texts:
            text_collection = text.get('metadata', {}).get('collection_display', '')
            if collection_name.lower() in text_collection.lower() or collection_name == "All Texts":
                filtered_texts.append(text)
        
        return filtered_texts
