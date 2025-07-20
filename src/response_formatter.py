
import streamlit as st
import re
from typing import Dict, List, Any
from src.multilingual import MultilingualProcessor
from src.utils import setup_logging

logger = setup_logging()

class ResponseFormatter:
    """Format LLM responses for beautiful display"""
    
    def __init__(self):
        self.multilingual = MultilingualProcessor()
        self.css_styles = self._load_css_styles()
    
    def format_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format complete response for display"""
        
        response_text = response_data.get("response", "")
        sources = response_data.get("sources", [])
        query = response_data.get("query", "")
        language_preference = response_data.get("language_preference", "all")
        
        # Parse response sections
        parsed_response = self._parse_response_sections(response_text)
        
        # Format sources
        formatted_sources = self._format_sources(sources)
        
        # Create display components
        display_components = {
            "main_answer": parsed_response.get("main_answer", response_text),
            "sanskrit_verses": parsed_response.get("sanskrit_verses", []),
            "explanation": parsed_response.get("explanation", ""),
            "sources": formatted_sources,
            "related_questions": self._generate_related_questions(query),
            "css_styles": self.css_styles
        }
        
        return display_components
    
    def _parse_response_sections(self, response: str) -> Dict[str, Any]:
        """Parse response into structured sections"""
        sections = {
            "main_answer": "",
            "sanskrit_verses": [],
            "explanation": "",
            "sources_mentioned": []
        }
        
        # Try to parse structured response
        if "🕉️" in response or "📿" in response:
            return self._parse_structured_response(response)
        
        # Fallback: treat entire response as main answer
        sections["main_answer"] = response
        
        # Extract Sanskrit verses if present
        sanskrit_pattern = r'[\u0900-\u097F।॥\s]+'
        sanskrit_matches = re.findall(sanskrit_pattern, response)
        
        for match in sanskrit_matches:
            if len(match.strip()) > 10:  # Filter out small matches
                sections["sanskrit_verses"].append({
                    "sanskrit": match.strip(),
                    "transliteration": self.multilingual.transliterate_devanagari(match.strip()),
                    "source": "From response"
                })
        
        return sections
    
    def _parse_structured_response(self, response: str) -> Dict[str, Any]:
        """Parse structured response with emojis"""
        sections = {
            "main_answer": "",
            "sanskrit_verses": [],
            "explanation": "",
            "sources_mentioned": []
        }
        
        # Split by sections
        lines = response.split('\n')
        current_section = "main_answer"
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("🕉️") or "Main Answer" in line:
                current_section = "main_answer"
                continue
            elif line.startswith("📿") or "Sanskrit Verses" in line:
                current_section = "sanskrit_verses"
                continue
            elif line.startswith("🔍") or "Explanation" in line:
                current_section = "explanation"
                continue
            elif line.startswith("📚") or "Sources" in line:
                current_section = "sources"
                continue
            
            # Add content to appropriate section
            if current_section == "main_answer" and line:
                sections["main_answer"] += line + "\n"
            elif current_section == "explanation" and line:
                sections["explanation"] += line + "\n"
            elif current_section == "sources" and line:
                sections["sources_mentioned"].append(line)
            elif current_section == "sanskrit_verses" and line:
                if re.search(r'[\u0900-\u097F]', line):
                    sections["sanskrit_verses"].append({
                        "sanskrit": line,
                        "transliteration": self.multilingual.transliterate_devanagari(line),
                        "source": "From response"
                    })
        
        return sections
    
    def _format_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format source information for display"""
        formatted_sources = []
        
        for source in sources:
            content = source.get("content", {})
            metadata = source.get("metadata", {})
            
            formatted_source = {
                "title": f"{metadata.get('collection', 'Unknown').title()} - {metadata.get('file', 'Unknown')}",
                "verse_reference": metadata.get('verse_number', 'N/A'),
                "chapter": metadata.get('chapter', 'N/A'),
                "sanskrit": content.get('sanskrit', ''),
                "hindi": content.get('hindi', ''),
                "english": content.get('english', ''),
                "similarity_score": source.get('similarity_score', 0),
                "collection": metadata.get('collection', 'unknown')
            }
            
            formatted_sources.append(formatted_source)
        
        return formatted_sources
    
    def _generate_related_questions(self, query: str) -> List[str]:
        """Generate related questions based on current query"""
        related_questions = []
        
        # Basic keyword-based suggestions
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['krishna', 'kṛṣṇa']):
            related_questions.extend([
                "What are Krishna's teachings on dharma?",
                "How does Krishna explain karma yoga?",
                "What is Krishna's advice on meditation?"
            ])
        
        if any(word in query_lower for word in ['dharma', 'duty']):
            related_questions.extend([
                "What is the difference between dharma and karma?",
                "How is dharma described in Ramayana?",
                "What are the types of dharma mentioned in scriptures?"
            ])
        
        if any(word in query_lower for word in ['dharma', 'duty']):
            related_questions.extend([
                "What is the difference between dharma and karma?",
                "How is dharma described in Ramayana?",
                "What are the types of dharma mentioned in scriptures?"
            ])
        
        if any(word in query_lower for word in ['karma', 'action']):
            related_questions.extend([
                "What is nishkama karma?",
                "How does karma affect rebirth?",
                "Different types of karma in Hindu philosophy"
            ])
        
        if any(word in query_lower for word in ['meditation', 'dhyana']):
            related_questions.extend([
                "What are the stages of meditation?",
                "How to practice dhyana according to Patanjali?",
                "Benefits of meditation in scriptures"
            ])
        
        # Remove duplicates and limit to 5
        return list(set(related_questions))[:5]
    
    def _load_css_styles(self) -> str:
        """Load CSS styles for formatting"""
        return """
        <style>
        .sanskrit-text {
            font-family: 'Noto Sans Devanagari', serif;
            font-size: 1.3em;
            color: #8B4513;
            background: linear-gradient(135deg, #FFF8DC, #F0E68C);
            padding: 1.5rem;
            border-left: 4px solid #FF6B35;
            border-radius: 8px;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .hindi-text {
            font-family: 'Noto Sans Devanagari', serif;
            font-size: 1.1em;
            color: #2E4053;
            background: #F8F9FA;
            padding: 1rem;
            border-radius: 6px;
            margin: 0.5rem 0;
        }
        
        .english-text {
            font-family: 'Georgia', serif;
            color: #1B4F72;
            line-height: 1.6;
            padding: 1rem;
            background: #FFFFFF;
            border-radius: 6px;
            margin: 0.5rem 0;
        }
        
        .source-card {
            background: #F7F9FC;
            border: 1px solid #E1E8ED;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            transition: box-shadow 0.3s ease;
        }
        
        .source-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .source-title {
            font-weight: bold;
            color: #FF6B35;
            margin-bottom: 0.5rem;
        }
        
        .verse-reference {
            font-size: 0.9em;
            color: #666;
            font-style: italic;
        }
        
        .similarity-score {
            background: #E8F5E8;
            color: #2E7D32;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .related-questions {
            background: #FFF3E0;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .question-item {
            background: #FFFFFF;
            border: 1px solid #FFB74D;
            border-radius: 6px;
            padding: 0.8rem;
            margin: 0.5rem 0;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .question-item:hover {
            background: #FFF8E1;
            transform: translateY(-2px);
        }
        </style>
        """
    
    def display_multilingual_response(self, components: Dict[str, Any]):
        """Display formatted multilingual response in Streamlit"""
        
        # Apply CSS styles
        st.markdown(components["css_styles"], unsafe_allow_html=True)
        
        # Main Answer Section
        st.markdown("## 🕉️ उत्तर / Answer")
        
        if components["main_answer"]:
            st.markdown(f'<div class="english-text">{components["main_answer"]}</div>', 
                       unsafe_allow_html=True)
        
        # Sanskrit Verses Section
        if components["sanskrit_verses"]:
            st.markdown("## 📿 संस्कृत श्लोक / Sanskrit Verses")
            
            for i, verse in enumerate(components["sanskrit_verses"]):
                st.markdown(f'''
                <div class="sanskrit-text">
                <strong>श्लोक {i+1}:</strong><br>
                {verse["sanskrit"]}<br><br>
                <strong>Transliteration:</strong><br>
                <em>{verse.get("transliteration", "")}</em><br><br>
                <strong>Source:</strong> {verse.get("source", "Unknown")}
                </div>
                ''', unsafe_allow_html=True)
        
        # Explanation Section
        if components["explanation"]:
            st.markdown("## 🔍 विस्तृत व्याख्या / Detailed Explanation")
            st.markdown(f'<div class="english-text">{components["explanation"]}</div>', 
                       unsafe_allow_html=True)
        
        # Sources Section
        if components["sources"]:
            st.markdown("## 📚 स्रोत / Sources")
            
            for source in components["sources"]:
                similarity_score = f"{source['similarity_score']:.2f}" if source['similarity_score'] > 0 else "N/A"
                
                st.markdown(f'''
                <div class="source-card">
                    <div class="source-title">{source["title"]}</div>
                    <div class="verse-reference">
                        Chapter: {source["chapter"]} | Verse: {source["verse_reference"]}
                        <span class="similarity-score">Relevance: {similarity_score}</span>
                    </div>
                    <br>
                    <strong>Sanskrit:</strong> {source["sanskrit"]}<br>
                    <strong>Hindi:</strong> {source["hindi"]}<br>
                    <strong>English:</strong> {source["english"]}
                </div>
                ''', unsafe_allow_html=True)
        
        # Related Questions Section
        if components["related_questions"]:
            st.markdown("## 💡 संबंधित प्रश्न / Related Questions")
            
            st.markdown('<div class="related-questions">', unsafe_allow_html=True)
            
            for question in components["related_questions"]:
                if st.button(question, key=f"related_q_{hash(question)}"):
                    st.experimental_rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

----
