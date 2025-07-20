
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import os
from pathlib import Path
from src.utils import setup_logging, ensure_dir
from config import Config

logger = setup_logging()

class EmbeddingManager:
    """Manage text embeddings using sentence-transformers"""
    
    def __init__(self):
        self.model = None
        self.embeddings_path = Config.EMBEDDINGS_PATH
        self.model_name = Config.EMBEDDING_MODEL
        ensure_dir(self.embeddings_path)
    
    @st.cache_resource
    def load_model(_self):
        """Load sentence transformer model with caching"""
        try:
            logger.info(f"Loading embedding model: {_self.model_name}")
            model = SentenceTransformer(_self.model_name)
            logger.info("Embedding model loaded successfully")
            return model
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            # Fallback to smaller model
            fallback_model = "all-MiniLM-L6-v2"
            logger.info(f"Trying fallback model: {fallback_model}")
            return SentenceTransformer(fallback_model)
    
    def create_embeddings(self, texts: List[Dict[str, Any]]) -> np.ndarray:
        """Create embeddings for all texts"""
        if not self.model:
            self.model = self.load_model()
        
        # Extract text for embedding
        text_list = [text.get("chunk_text", text["content"].get("text", "")) for text in texts]
        
        logger.info(f"Creating embeddings for {len(text_list)} texts")
        
        try:
            with st.spinner("Creating embeddings..."):
                # Create embeddings in batches to manage memory
                batch_size = 32
                embeddings = []
                
                for i in range(0, len(text_list), batch_size):
                    batch = text_list[i:i + batch_size]
                    batch_embeddings = self.model.encode(
                        batch,
                        show_progress_bar=True,
                        convert_to_numpy=True,
                        normalize_embeddings=True
                    )
                    embeddings.extend(batch_embeddings)
            
            embeddings_array = np.array(embeddings)
            logger.info(f"Created embeddings shape: {embeddings_array.shape}")
            
            return embeddings_array
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise
    
    def save_embeddings(self, embeddings: np.ndarray, texts: List[Dict[str, Any]]):
        """Save embeddings and metadata to disk"""
        try:
            # Save embeddings
            embeddings_file = os.path.join(self.embeddings_path, "text_embeddings.npy")
            np.save(embeddings_file, embeddings)
            
            # Save metadata
            metadata_file = os.path.join(self.embeddings_path, "embedding_metadata.json")
            metadata = {
                "texts": texts,
                "model_name": self.model_name,
                "embedding_dim": embeddings.shape[1],
                "num_texts": len(texts)
            }
            
            import json
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved embeddings to {embeddings_file}")
            
        except Exception as e:
            logger.error(f"Error saving embeddings: {e}")
    
    def load_embeddings(self) -> tuple:
        """Load embeddings and metadata from disk"""
        try:
            embeddings_file = os.path.join(self.embeddings_path, "text_embeddings.npy")
            metadata_file = os.path.join(self.embeddings_path, "embedding_metadata.json")
            
            if not (os.path.exists(embeddings_file) and os.path.exists(metadata_file)):
                return None, None
            
            embeddings = np.load(embeddings_file)
            
            import json
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            logger.info(f"Loaded embeddings shape: {embeddings.shape}")
            return embeddings, metadata["texts"]
            
        except Exception as e:
            logger.error(f"Error loading embeddings: {e}")
            return None, None
    
    def search_similar(self, query: str, embeddings: np.ndarray, 
                      texts: List[Dict[str, Any]], k: int = 5) -> List[Dict[str, Any]]:
        """Find similar texts using cosine similarity"""
        if not self.model:
            self.model = self.load_model()
        
        # Create query embedding
        query_embedding = self.model.encode([query], normalize_embeddings=True)
        
        # Calculate similarities
        similarities = np.dot(embeddings, query_embedding.T).flatten()
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:k]
        
        # Return results with similarity scores
        results = []
        for idx in top_indices:
            if similarities[idx] >= Config.SIMILARITY_THRESHOLD:
                result = texts[idx].copy()
                result["similarity_score"] = float(similarities[idx])
                results.append(result)
        
        return results
