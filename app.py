
# Fixed app.py - Updated for local GitHub files

import streamlit as st
import os
from pathlib import Path
import sys

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

# FIXED IMPORTS - Changed from drive_loader to data_loader
from src.data_loader import get_scripture_data, get_all_scripture_data
from src.rag_chain import KalkiRAGChain
from src.response_formatter import ResponseFormatter
from src.utils import setup_logging
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

# Load scripture data at startup
scripture_data = get_scripture_data()

@st.cache_resource
def initialize_rag_system():
    """Initialize RAG system with caching"""
    return KalkiRAGChain()

def ensure_dir(path):
    """Ensure directory exists - simplified for Streamlit Cloud"""
    try:
        os.makedirs(path, exist_ok=True)
    except:
        pass  # Ignore errors on Streamlit Cloud

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
        <h1>🕉️ {getattr(Config, 'APP_TITLE', 'Kalki GPT')}</h1>
        <p style="font-size: 1.2em; margin: 0;">{getattr(Config, 'APP_SUBTITLE', 'Hindu Scripture AI Assistant')}</p>
        <p style="font-size: 1em; margin: 0.5rem 0 0 0;">{getattr(Config, 'APP_DESCRIPTION', 'Discover wisdom from sacred texts')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show scripture loading status
    if scripture_data:
        st.success(f"📚 Loaded {len(scripture_data)} scripture files successfully!")
        
        # Show collections summary
        collections = {}
        for filename in scripture_data.keys():
            if 'ramcharitmanas' in filename.lower():
                collections['Ramcharitmanas'] = collections.get('Ramcharitmanas', 0) + 1
            elif 'valmiki' in filename.lower():
                collections['Valmiki Ramayana'] = collections.get('Valmiki Ramayana', 0) + 1
            else:
                collections['Other Texts'] = collections.get('Other Texts', 0) + 1
        
        cols = st.columns(len(collections))
        for i, (collection, count) in enumerate(collections.items()):
            with cols[i]:
                st.metric(collection, count, "files")
    else:
        st.error("❌ Failed to load scripture data from GitHub")
        st.stop()
    
    # Initialize RAG system
    rag_chain = initialize_rag_system()
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        st.header("🌐 Language / भाषा")
        language_options = [
            "🌍 All Languages", "🇮🇳 Hindi", "🇺🇸 English", 
            "संस्कृत Sanskrit", "📖 Original Text"
        ]
        language_pref = st.selectbox(
            "Choose response language:",
            language_options,
            index=0
        )
        
        st.header("📚 Scripture Selection")
        scripture_options = [
            "All Texts", "Ramcharitmanas", "Valmiki Ramayana", 
            "Bhagavad Gita", "Ramayana", "Mahabharata"
        ]
        scripture_filter = st.selectbox(
            "Filter by text:",
            scripture_options,
            index=0
        )
        
        st.header("⚙️ System Settings")
        
        # Initialize system
        if st.button("🔄 Initialize System", type="primary"):
            with st.spinner("Initializing Kalki GPT..."):
                if rag_chain.initialize():
                    st.success("✅ System initialized successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to initialize system")
        
        # Rebuild index
        if st.button("🔨 Rebuild Index"):
            with st.spinner("Rebuilding search index..."):
                if rag_chain.rebuild_index():
                    st.success("✅ Index rebuilt successfully!")
                    st.rerun()
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
                <strong>Collections:</strong> {len(stats.get('collections', {}))}<br>
                <strong>Status:</strong> ✅ Initialized
            </div>
            """, unsafe_allow_html=True)
            
            # Collection stats
            collections = stats.get('collections', {})
            if collections:
                st.write("**Text Collections:**")
                for collection, count in collections.items():
                    st.write(f"- {collection.replace('_', ' ').title()}: {count}")
        else:
            st.info("🔄 System not initialized yet. Click 'Initialize System' above.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Sample questions
        st.header("💡 Sample Questions")
        sample_questions = [
            "What does Ramcharitmanas say about devotion?",
            "Tell me about Hanuman's qualities",
            "What is dharma according to scriptures?",
            "Explain the concept of bhakti",
            "What are the qualities of a good devotee?",
            "How to overcome difficulties in life?",
            "What is the importance of guru?",
            "Tell me about Ram's ideals"
        ]
        
        for i, question in enumerate(sample_questions):
            if st.button(
                question, 
                key=f"sample_q_{i}",
                help="Click to ask this question"
            ):
                st.session_state.query = question
                st.rerun()
    
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
            placeholder="Example: What does Ramcharitmanas say about devotion to Lord Ram?",
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
                st.rerun()
        
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
                    if hasattr(rag_chain, 'response_formatter'):
                        formatter = rag_chain.response_formatter
                    else:
                        formatter = ResponseFormatter()
                    
                    # Display response
                    st.markdown("### 📖 Answer from Scriptures")
                    
                    # Main response
                    if "response" in response:
                        st.markdown(response["response"])
                    
                    # Sources
                    if "sources" in response and response["sources"]:
                        with st.expander("📚 Sources", expanded=True):
                            for i, source in enumerate(response["sources"], 1):
                                st.markdown(f"""
                                **Source {i}:** {source.get('collection_display', 'Unknown')}  
                                **File:** {source.get('source_file', 'Unknown')}  
                                **Relevance:** {source.get('similarity_score', 0):.2%}  
                                **Content:** {source.get('content', {}).get('text', 'No content')[:200]}...
                                """)
                                st.markdown("---")
                    
                    # Query processing info
                    if "processed_query" in response:
                        with st.expander("🔧 Query Processing Details"):
                            pq = response["processed_query"]
                            st.write("**Original Query:**", pq.get("original", ""))
                            st.write("**Processed Query:**", pq.get("processed", ""))
                            st.write("**Expanded Query:**", pq.get("expanded", ""))
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
            random_q = random.choice(sample_questions)
            st.session_state.query = random_q
            st.rerun()
        
        # Popular topics
        st.subheader("🔥 Popular Topics")
        topics = [
            "Dharma", "Bhakti", "Ram", "Hanuman", 
            "Devotion", "Spiritual Path", "Guru", "Prayer"
        ]
        
        for topic in topics:
            if st.button(f"#{topic}", key=f"topic_{topic}", use_container_width=True):
                st.session_state.query = f"Tell me about {topic} according to Hindu scriptures"
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        🕉️ <strong>Kalki GPT</strong> - Built with ❤️ for preserving and sharing dharmic wisdom<br>
        <small>Powered by AI • Sourced from authentic Hindu scriptures • Data: Ramcharitmanas & Valmiki Ramayana</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
