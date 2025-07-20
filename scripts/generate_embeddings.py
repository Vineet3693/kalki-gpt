
#!/usr/bin/env python3
"""
Pre-generate embeddings for faster initialization
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
import argparse
from tqdm import tqdm

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from data_loader import DharmicDataLoader
from text_processor import TextProcessor
from embeddings import EmbeddingManager
from vector_store import VectorStore
from utils import setup_logging, ensure_dir
from config import Config

logger = setup_logging()

def main():
    parser = argparse.ArgumentParser(description="Generate embeddings for Kalki GPT")
    parser.add_argument("--force", action="store_true", help="Force regenerate even if embeddings exist")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for embedding generation")
    parser.add_argument("--output-dir", type=str, default=Config.EMBEDDINGS_PATH, help="Output directory for embeddings")
    
    args = parser.parse_args()
    
    print("🕉️ Kalki GPT Embedding Generator")
    print("=" * 40)
    
    # Ensure output directory exists
    ensure_dir(args.output_dir)
    
    # Check if embeddings already exist
    embeddings_file = os.path.join(args.output_dir, "text_embeddings.npy")
    if os.path.exists(embeddings_file) and not args.force:
        print("✅ Embeddings already exist. Use --force to regenerate.")
        return
    
    try:
        # Load data
        print("📚 Loading scripture texts...")
        data_loader = DharmicDataLoader(Config.DATA_PATH)
        texts = data_loader.load_all_texts()
        print(f"✅ Loaded {len(texts)} texts")
        
        # Process texts
        print("🔄 Processing texts...")
        text_processor = TextProcessor()
        processed_texts = text_processor.process_texts(texts)
        print(f"✅ Created {len(processed_texts)} text chunks")
        
        # Generate embeddings
        print("🧠 Generating embeddings...")
        embedding_manager = EmbeddingManager()
        
        # Create embeddings in batches with progress bar
        text_list = [text.get("chunk_text", text["content"].get("text", "")) for text in processed_texts]
        
        model = embedding_manager.load_model()
        embeddings = []
        
        for i in tqdm(range(0, len(text_list), args.batch_size), desc="Creating embeddings"):
            batch = text_list[i:i + args.batch_size]
            batch_embeddings = model.encode(
                batch,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            embeddings.extend(batch_embeddings)
        
        embeddings_array = np.array(embeddings)
        print(f"✅ Generated embeddings shape: {embeddings_array.shape}")
        
        # Save embeddings
        print("💾 Saving embeddings...")
        embedding_manager.save_embeddings(embeddings_array, processed_texts)
        
        # Create FAISS index
        print("🔍 Creating search index...")
        vector_store = VectorStore()
        vector_store.create_index(embeddings_array)
        vector_store.save_index()
        
        # Generate statistics
        print("📊 Generating statistics...")
        stats = {
            "total_texts": len(processed_texts),
            "embedding_dimension": embeddings_array.shape[1],
            "model_name": Config.EMBEDDING_MODEL,
            "batch_size": args.batch_size,
            "collections": {}
        }
        
        # Collection statistics
        for text in processed_texts:
            collection = text["metadata"].get("collection", "unknown")
            stats["collections"][collection] = stats["collections"].get(collection, 0) + 1
        
        with open(os.path.join(args.output_dir, "generation_stats.json"), "w") as f:
            json.dump(stats, f, indent=2)
        
        print("\n" + "=" * 40)
        print("🎉 Embedding generation completed successfully!")
        print(f"📁 Saved to: {args.output_dir}")
        print(f"📊 Statistics:")
        print(f"   Total texts: {stats['total_texts']}")
        print(f"   Embedding dimension: {stats['embedding_dimension']}")
        print(f"   Collections: {len(stats['collections'])}")
        
        for collection, count in stats["collections"].items():
            print(f"     {collection}: {count}")
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
