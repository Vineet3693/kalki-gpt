
import streamlit as st
from typing import Dict, List, Any, Optional
import os
from src.data_loader import DharmicDataLoader, get_all_scripture_data
from src.text_processor import TextProcessor
from src.embeddings import EmbeddingManager
from src.vector_store import VectorStore
from src.query_processor import QueryProcessor
from src.llm_handler import LLMHandler
from src.response_formatter import ResponseFormatter
from src.utils import setup_logging, save_json, load_json
from config import Config

logger = setup_logging()

class KalkiRAGChain:
    """Complete RAG pipeline for Kalki GPT"""
    
    def __init__(self):
        # Updated to use new Google Drive loader without path requirement
        self.data_loader = DharmicDataLoader()  # No path needed now
        self.text_processor = TextProcessor()
        self.embedding_manager = EmbeddingManager()
        self.vector_store = VectorStore()
        self.query_processor = QueryProcessor()
        self.llm_handler = LLMHandler()
        self.response_formatter = ResponseFormatter()
        
        self.texts = None
        self.embeddings = None
        self.is_initialized = False
    
    @st.cache_data
    def initialize(_self, force_rebuild: bool = False) -> bool:
        """Initialize the RAG system with caching"""
        try:
            logger.info("Initializing Kalki RAG Chain...")
            
            with st.spinner("Loading sacred texts from Google Drive..."):
                # Use the new Google Drive loading method
                raw_data = get_all_scripture_data()
                if not raw_data:
                    st.error("Failed to load scripture data from Google Drive")
                    return False
                
                # Convert to the format expected by text processor
                _self.texts = _self._convert_data_format(raw_data)
                logger.info(f"Loaded {len(_self.texts)} texts")
            
            with st.spinner("Processing texts..."):
                # Process texts into chunks
                processed_texts = _self.text_processor.process_texts(_self.texts)
                _self.texts = processed_texts
                logger.info(f"Created {len(processed_texts)} text chunks")
            
            # Try to load existing embeddings
            if not force_rebuild:
                embeddings, cached_texts = _self.embedding_manager.load_embeddings()
                if embeddings is not None and cached_texts is not None:
                    logger.info("Loaded cached embeddings")
                    _self.embeddings = embeddings
                    _self.texts = cached_texts
                    
                    # Load FAISS index
                    if _self.vector_store.load_index():
                        logger.info("Loaded cached FAISS index")
                        _self.is_initialized = True
                        return True
            
            # Create new embeddings if not cached or force rebuild
            with st.spinner("Creating embeddings... This may take a few minutes."):
                _self.embeddings = _self.embedding_manager.create_embeddings(_self.texts)
            
            with st.spinner("Creating search index..."):
                # Create and save FAISS index
                _self.vector_store.create_index(_self.embeddings)
                _self.vector_store.save_index()
            
            with st.spinner("Saving embeddings..."):
                # Save embeddings for future use
                _self.embedding_manager.save_embeddings(_self.embeddings, _self.texts)
            
            _self.is_initialized = True
            logger.info("RAG Chain initialization complete!")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing RAG Chain: {e}")
            st.error(f"Failed to initialize system: {e}")
            return False
    
    def _convert_data_format(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert raw Google Drive data to expected format"""
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
        """Extract collection name from filename"""
        filename_lower = filename.lower()
        
        if "bhagavad" in filename_lower or "gita" in filename_lower:
            return "bhagavad_gita"
        elif "ramayana" in filename_lower:
            return "ramayana"
        elif "mahabharata" in filename_lower:
            return "mahabharata"
        elif "rigveda" in filename_lower or "rig_veda" in filename_lower:
            return "rigveda"
        elif "yajurveda" in filename_lower or "yajur_veda" in filename_lower:
            return "yajurveda"
        elif "atharvaveda" in filename_lower or "atharva_veda" in filename_lower:
            return "atharvaveda"
        elif "ramcharitmanas" in filename_lower:
            return "ramcharitmanas"
        else:
            return "unknown"
    
    def ask(self, question: str, scripture_filter: str = "All Texts", 
            language_preference: str = "🌍 All Languages") -> Dict[str, Any]:
        """Ask a question and get comprehensive answer"""
        
        if not self.is_initialized:
            if not self.initialize():
                return {"error": "System not initialized"}
        
        try:
            # Process query
            processed_query = self.query_processor.process_query(
                question, scripture_filter
            )
            
            # Search for relevant texts
            with st.spinner("Searching scriptures..."):
                relevant_texts = self._search_relevant_texts(
                    processed_query["expanded"], 
                    scripture_filter
                )
            
            if not relevant_texts:
                return {
                    "response": "I couldn't find relevant information in the scriptures for your question. Please try rephrasing or asking about different topics.",
                    "sources": [],
                    "query": question
                }
            
            # Generate response using LLM
            with st.spinner("Generating response..."):
                llm_response = self.llm_handler.generate_response(
                    question, relevant_texts, language_preference
                )
            
            # Format response for display
            formatted_response = self.response_formatter.format_response(llm_response)
            
            # Add processed query info
            formatted_response["processed_query"] = processed_query
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error in ask method: {e}")
            return {
                "error": f"Error processing question: {str(e)}",
                "query": question
            }
    
    def _search_relevant_texts(self, query: str, scripture_filter: str) -> List[Dict[str, Any]]:
        """Search for relevant texts using vector similarity"""
        
        # Create query embedding
        if not self.embedding_manager.model:
            self.embedding_manager.model = self.embedding_manager.load_model()
        
        query_embedding = self.embedding_manager.model.encode(
            [query], normalize_embeddings=True
        )
        
        # Search using FAISS
        scores, indices = self.vector_store.search(
            query_embedding, k=Config.TOP_K_RESULTS * 2  # Get more results for filtering
        )
        
        # Filter results
        relevant_texts = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.texts) and score >= Config.SIMILARITY_THRESHOLD:
                text = self.texts[idx].copy()
                text["similarity_score"] = float(score)
                
                # Apply scripture filter
                if self._matches_scripture_filter(text, scripture_filter):
                    relevant_texts.append(text)
        
        # Sort by relevance and limit results
        relevant_texts.sort(key=lambda x: x["similarity_score"], reverse=True)
        return relevant_texts[:Config.TOP_K_RESULTS]
    
    def _matches_scripture_filter(self, text: Dict[str, Any], filter_name: str) -> bool:
        """Check if text matches scripture filter"""
        if filter_name == "All Texts":
            return True
        
        collection = text["metadata"].get("collection", "").lower()
        
        filter_mapping = {
            "Bhagavad Gita": ["bhagavad_gita", "srimadbhagvadgita"],
            "Ramayana": ["valmiki_ramayana", "ramayana"],
            "Mahabharata": ["mahabharata"],
            "Rigveda": ["rigveda"],
            "Yajurveda": ["yajurveda"],
            "Atharvaveda": ["atharvaveda", "atharva"],
            "Ramcharitmanas": ["ramcharitmanas"]
        }
        
        for filter_key, collections in filter_mapping.items():
            if filter_key == filter_name:
                return any(coll in collection for coll in collections)
        
        return True
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        if not self.is_initialized:
            return {"status": "Not initialized"}
        
        stats = {
            "total_texts": len(self.texts) if self.texts else 0,
            "embedding_dimension": self.embeddings.shape[1] if self.embeddings is not None else 0,
            "collections": {}
        }
        
        # Get collection statistics
        if self.texts:
            for text in self.texts:
                collection = text["metadata"].get("collection", "unknown")
                stats["collections"][collection] = stats["collections"].get(collection, 0) + 1
        
        # Get vector store stats
        vector_stats = self.vector_store.get_stats()
        stats.update(vector_stats)
        
        return stats
    
    def rebuild_index(self):
        """Rebuild embeddings and index from scratch"""
        logger.info("Rebuilding RAG index...")
        self.is_initialized = False
        
        # Clear cached data
        st.cache_data.clear()
        st.cache_resource.clear()
        
        # Reinitialize with force rebuild
        return self.initialize(force_rebuild=True)
    
    def get_sample_questions(self) -> List[str]:
        """Get sample questions based on available data"""
        base_questions = Config.SAMPLE_QUESTIONS.copy()
        
        # Add collection-specific questions if data is available
        if self.texts:
            collections = set()
            for text in self.texts:
                collections.add(text["metadata"].get("collection", ""))
            
            if "bhagavad_gita" in collections:
                base_questions.append("What does Bhagavad Gita say about yoga?")
            if "ramayana" in collections:
                base_questions.append("Describe Hanuman's qualities from Ramayana")
            if "rigveda" in collections:
                base_questions.append("What are the main themes in Rigveda?")
        
        return base_questions[:8]  # Limit to 8 questions
    
    def search_by_keywords(self, keywords: List[str], max_results: int = 10) -> List[Dict[str, Any]]:
        """Search texts by specific keywords"""
        if not self.is_initialized or not self.texts:
            return []
        
        matching_texts = []
        
        for text in self.texts:
            content_text = text.get("chunk_text", "").lower()
            content_fields = text.get("content", {})
            
            # Check all text fields
            all_text = " ".join([
                content_fields.get("sanskrit", ""),
                content_fields.get("hindi", ""),
                content_fields.get("english", ""),
                content_text
            ]).lower()
            
            # Calculate keyword match score
            matches = sum(1 for keyword in keywords if keyword.lower() in all_text)
            
            if matches > 0:
                text_copy = text.copy()
                text_copy["keyword_matches"] = matches
                text_copy["match_score"] = matches / len(keywords)
                matching_texts.append(text_copy)
        
        # Sort by match score
        matching_texts.sort(key=lambda x: x["match_score"], reverse=True)
        return matching_texts[:max_results]
