
import streamlit as st
import os
from pathlib import Path
import sys

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.rag_chain import KalkiRAGChain
from src.response_formatter import ResponseFormatter
from src.utils import setup_logging, ensure_dir
from config import Config

# Configure page
st.set_page_config(
    page_title="Kalki GPT - Hindu Scripture AI",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup logging
logger = setup_logging()

# Ensure required directories exist
for path in [Config.DATA_PATH, Config.PROCESSED_DATA_PATH, Config.EMBEDDINGS_PATH, Config.CACHE_PATH, "logs"]:
    ensure_dir(path)

@st.cache_resource
def initialize_rag_system():
    """Initialize RAG system with caching"""
    return KalkiRAGChain()

def main():
    """Main application function"""
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #FF6B35, #F7931E);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .question-input {
        font-size: 1.1em !important;
        border-radius: 8px !important;
        border: 2px solid #FF6B35 !important;
    }
    
    .sidebar-content {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .stats-card {
        background: #E3F2FD;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .sample-question {
        background: #FFF3E0;
        border: 1px solid #FFB74D;
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .sample-question:hover {
        background: #FFF8E1;
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>🕉️ {Config.APP_TITLE}</h1>
        <p style="font-size: 1.2em; margin: 0;">{Config.APP_SUBTITLE}</p>
        <p style="font-size: 1em; margin: 0.5rem 0 0 0;">{Config.APP_DESCRIPTION}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize RAG system
    rag_chain = initialize_rag_system()
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        st.header("🌐 Language / भाषा")
        language_pref = st.selectbox(
            "Choose response language:",
            Config.LANGUAGES,
            index=0
        )
        
        st.header("📚 Scripture Selection")
        scripture_filter = st.selectbox(
            "Filter by text:",
            Config.SCRIPTURE_FILTERS,
            index=0
        )
        
        st.header("⚙️ System Settings")
        
        # Initialize system
        if st.button("🔄 Initialize System", type="primary"):
            with st.spinner("Initializing Kalki GPT..."):
                if rag_chain.initialize():
                    st.success("✅ System initialized successfully!")
                    st.experimental_rerun()
                else:
                    st.error("❌ Failed to initialize system")
        
        # Rebuild index
        if st.button("🔨 Rebuild Index"):
            with st.spinner("Rebuilding search index..."):
                if rag_chain.rebuild_index():
                    st.success("✅ Index rebuilt successfully!")
                    st.experimental_rerun()
                else:
                    st.error("❌ Failed to rebuild index")
        
        # System stats
        st.header("📊 System Statistics")
        stats = rag_chain.get_system_stats()
        
        if stats.get("status") != "Not initialized":
            st.markdown(f"""
            <div class="stats-card">
                <strong>Total Texts:</strong> {stats.get('total_texts', 0)}<br>
                <strong>Vector Dimension:</strong> {stats.get('embedding_dimension', 0)}<br>
                <strong>Index Type:</strong> {stats.get('index_type', 'N/A')}
            </div>
            """, unsafe_allow_html=True)
            
            # Collection stats
            collections = stats.get('collections', {})
            if collections:
                st.write("**Text Collections:**")
                for collection, count in collections.items():
                    st.write(f"- {collection.title()}: {count}")
        else:
            st.info("System not initialized yet")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Sample questions
        st.header("💡 Sample Questions")
        sample_questions = rag_chain.get_sample_questions()
        
        for i, question in enumerate(sample_questions):
            if st.button(
                question, 
                key=f"sample_q_{i}",
                help="Click to ask this question"
            ):
                st.session_state.query = question
                st.experimental_rerun()
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Question input
        st.subheader("🔍 Ask Your Question")
        
        # Get query from session state or user input
        default_query = st.session_state.get('query', '')
        
        question = st.text_area(
            "Enter your question about Hindu scriptures:",
            value=default_query,
            height=100,
            placeholder="Example: What does Krishna say about dharma in Bhagavad Gita?",
            help="Ask questions about dharma, karma, devotion, meditation, or any spiritual concept"
        )
        
        # Clear the session state query after using it
        if 'query' in st.session_state:
            del st.session_state.query
        
        col_search, col_clear = st.columns([2, 1])
        
        with col_search:
            search_clicked = st.button("🚀 Search Scriptures", type="primary", use_container_width=True)
        
        with col_clear:
            if st.button("🗑️ Clear", use_container_width=True):
                st.experimental_rerun()
        
        # Process question
        if search_clicked and question.strip():
            
            if not rag_chain.is_initialized:
                st.warning("⚠️ Please initialize the system first using the sidebar button.")
                st.stop()
            
            try:
                # Get response
                with st.spinner("🔍 Searching sacred texts..."):
                    response = rag_chain.ask(
                        question, 
                        scripture_filter, 
                        language_pref
                    )
                
                if "error" in response:
                    st.error(f"❌ {response['error']}")
                else:
                    # Display formatted response
                    formatter = ResponseFormatter()
                    formatter.display_multilingual_response(response)
                    
                    # Show query processing info in expander
                    if "processed_query" in response:
                        with st.expander("🔧 Query Processing Details"):
                            pq = response["processed_query"]
                            st.write("**Original Query:**", pq.get("original", ""))
                            st.write("**Processed Query:**", pq.get("processed", ""))
                            st.write("**Expanded Query:**", pq.get("expanded", ""))
                            st.write("**Detected Language:**", pq.get("language", ""))
                            st.write("**Keywords:**", ", ".join(pq.get("keywords", [])))
                            
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                logger.error(f"Error in main app: {e}")
        
        elif search_clicked and not question.strip():
            st.warning("⚠️ Please enter a question first.")
    
    with col2:
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("🎲 Random Question", use_container_width=True):
            import random
            random_q = random.choice(rag_chain.get_sample_questions())
            st.session_state.query = random_q
            st.experimental_rerun()
        
        # Popular topics
        st.subheader("🔥 Popular Topics")
        topics = [
            "Dharma", "Karma", "Bhakti", "Yoga", 
            "Meditation", "Moksha", "Krishna", "Rama"
        ]
        
        for topic in topics:
            if st.button(f"#{topic}", key=f"topic_{topic}", use_container_width=True):
                st.session_state.query = f"Tell me about {topic} in Hindu scriptures"
                st.experimental_rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        🕉️ <strong>Kalki GPT</strong> - Built with ❤️ for preserving and sharing dharmic wisdom<br>
        <small>Powered by AI • Sourced from authentic Hindu scriptures</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
