
import os

class Config:
    # App Configuration
    APP_TITLE = "🕉️ Kalki GPT"
    APP_SUBTITLE = "AI-Powered Hindu Scripture Assistant"
    APP_DESCRIPTION = """
    Ask questions about Hindu sacred texts and receive answers with authentic 
    Sanskrit verses, Hindi explanations, and English translations.
    """
    
    # Model Configuration
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    LLM_MODEL = "microsoft/DialoGPT-medium"
    
    # Data Paths
    DATA_PATH = "data/raw"
    PROCESSED_DATA_PATH = "data/processed"
    EMBEDDINGS_PATH = "models/embeddings"
    CACHE_PATH = "data/cache"
    
    # Text Processing
    CHUNK_SIZE = 512
    CHUNK_OVERLAP = 50
    MAX_CHUNKS = 50000
    
    # Retrieval Settings
    TOP_K_RESULTS = 5
    SIMILARITY_THRESHOLD = 0.3
    
    # LLM Settings
    MAX_LENGTH = 1024
    TEMPERATURE = 0.3
    TOP_P = 0.9
    
    # UI Settings
    LANGUAGES = ["🌍 All Languages", "🇮🇳 Hindi", "🇬🇧 English", "🕉️ Sanskrit"]
    SCRIPTURE_FILTERS = [
        "All Texts", "Bhagavad Gita", "Ramayana", "Mahabharata", 
        "Rigveda", "Yajurveda", "Atharvaveda", "Ramcharitmanas"
    ]
    
    # Sample Questions
    SAMPLE_QUESTIONS = [
        "What does Krishna say about dharma in Bhagavad Gita?",
        "Tell me about Hanuman's devotion in Ramayana",
        "What are the main teachings about karma?",
        "How is meditation described in Hindu scriptures?",
        "What is the concept of moksha according to Vedas?"
    ]
