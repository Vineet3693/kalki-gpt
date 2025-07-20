
import faiss
import numpy as np
import os
import pickle
from typing import List, Dict, Any, Tuple
from src.utils import setup_logging, ensure_dir
from config import Config

logger = setup_logging()

class VectorStore:
    """FAISS-based vector store for similarity search"""
    
    def __init__(self):
        self.index = None
        self.dimension = None
        self.embeddings_path = Config.EMBEDDINGS_PATH
        ensure_dir(self.embeddings_path)
    
    def create_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Create FAISS index from embeddings"""
        self.dimension = embeddings.shape[1]
        
        logger.info(f"Creating FAISS index with dimension: {self.dimension}")
        
        # Use IndexFlatIP for cosine similarity (with normalized embeddings)
        self.index = faiss.IndexFlatIP(self.dimension)
        
        # Ensure embeddings are normalized for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add embeddings to index
        self.index.add(embeddings.astype('float32'))
        
        logger.info(f"Added {self.index.ntotal} vectors to FAISS index")
        return self.index
    
    def save_index(self):
        """Save FAISS index to disk"""
        if self.index is None:
            logger.error("No index to save")
            return
        
        try:
            index_path = os.path.join(self.embeddings_path, "faiss_index.bin")
            faiss.write_index(self.index, index_path)
            logger.info(f"Saved FAISS index to {index_path}")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    def load_index(self) -> bool:
        """Load FAISS index from disk"""
        try:
            index_path = os.path.join(self.embeddings_path, "faiss_index.bin")
            
            if not os.path.exists(index_path):
                return False
            
            self.index = faiss.read_index(index_path)
            self.dimension = self.index.d
            
            logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            return False
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """Search for similar vectors"""
        if self.index is None:
            raise ValueError("Index not initialized. Call create_index() first.")
        
        # Normalize query embedding
        query_embedding = query_embedding.astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, k)
        
        return scores, indices
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        if self.index is None:
            return {"status": "No index loaded"}
        
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": type(self.index).__name__,
            "is_trained": self.index.is_trained
        }
