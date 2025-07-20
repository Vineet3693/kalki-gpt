
import streamlit as st
from transformers import pipeline, AutoTokenizer
from typing import Dict, List, Any
import torch
from src.utils import setup_logging
from config import Config

logger = setup_logging()

class LLMHandler:
    """Handle Language Model operations for response generation"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_name = Config.LLM_MODEL
        self.max_length = Config.MAX_LENGTH
        self.temperature = Config.TEMPERATURE
    
    @st.cache_resource
    def load_model(_self):
        """Load LLM model with caching"""
        try:
            logger.info(f"Loading LLM model: {_self.model_name}")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(_self.model_name, padding_side='left')
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Load model pipeline
            model = pipeline(
                "text-generation",
                model=_self.model_name,
                tokenizer=tokenizer,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            logger.info("LLM model loaded successfully")
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"Error loading LLM model: {e}")
            # Fallback to simpler model
            try:
                logger.info("Trying fallback model: facebook/blenderbot_small-90M")
                fallback_model = pipeline("text-generation", model="facebook/blenderbot_small-90M")
                return fallback_model, None
            except:
                raise Exception("Failed to load any suitable LLM model")
    
    def generate_response(self, query: str, context_docs: List[Dict[str, Any]], 
                         language_preference: str = "all") -> Dict[str, Any]:
        """Generate response using LLM with context"""
        
        if not self.model:
            self.model, self.tokenizer = self.load_model()
        
        # Create context from retrieved documents
        context = self._format_context(context_docs)
        
        # Create prompt based on language preference
        prompt = self._create_prompt(query, context, language_preference)
        
        try:
            # Generate response
            with st.spinner("Generating response..."):
                response = self.model(
                    prompt,
                    max_length=self.max_length,
                    temperature=self.temperature,
                    num_return_sequences=1,
                    do_sample=True,
                    top_p=Config.TOP_P,
                    pad_token_id=self.tokenizer.pad_token_id if self.tokenizer else None,
                    eos_token_id=self.tokenizer.eos_token_id if self.tokenizer else None,
                    truncation=True
                )
            
            # Extract generated text
            generated_text = response[0]['generated_text']
            
            # Clean and format response
            clean_response = self._clean_response(generated_text, prompt)
            
            return {
                "response": clean_response,
                "sources": context_docs,
                "query": query,
                "language_preference": language_preference
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._fallback_response(query, context_docs)
    
    def _format_context(self, context_docs: List[Dict[str, Any]]) -> str:
        """Format retrieved documents as context"""
        context_parts = []
        
        for doc in context_docs[:Config.TOP_K_RESULTS]:
            content = doc["content"]
            metadata = doc["metadata"]
            
            # Format each document
            doc_text = f"""
Source: {metadata.get('collection', 'Unknown')} - {metadata.get('file', '')}
Verse: {metadata.get('verse_number', 'N/A')}

Sanskrit: {content.get('sanskrit', 'N/A')}
Hindi: {content.get('hindi', 'N/A')}
English: {content.get('english', 'N/A')}
"""
            context_parts.append(doc_text.strip())
        
        return "\n\n---\n\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str, language_preference: str) -> str:
        """Create appropriate prompt based on language preference"""
        
        if language_preference == "🌍 All Languages":
            return self._create_trilingual_prompt(query, context)
        elif language_preference == "🇮🇳 Hindi":
            return self._create_hindi_prompt(query, context)
        elif language_preference == "🇬🇧 English":
            return self._create_english_prompt(query, context)
        elif language_preference == "🕉️ Sanskrit":
            return self._create_sanskrit_prompt(query, context)
        else:
            return self._create_trilingual_prompt(query, context)
    
    def _create_trilingual_prompt(self, query: str, context: str) -> str:
        """Create prompt for trilingual response"""
        return f"""You are an expert on Hindu scriptures. Answer questions based on authentic texts only.

Context from Hindu Scriptures:
{context}

Question: {query}

Please provide a comprehensive answer in the following format:

🕉️ **Main Answer:**
[Provide answer in Hindi and English]

📿 **Sanskrit Verses:**
[Quote relevant Sanskrit verses if available]

🔍 **Explanation:**
[Detailed explanation in Hindi and English]

📚 **Sources:**
[List the specific texts and verses referenced]

Answer:"""

    def _create_hindi_prompt(self, query: str, context: str) -> str:
        """Create prompt for Hindi response"""
        return f"""आप हिंदू धर्मग्रंथों के विशेषज्ञ हैं। केवल प्रामाणिक ग्रंथों के आधार पर उत्तर दें।

हिंदू शास्त्रों से संदर्भ:
{context}

प्रश्न: {query}

कृपया हिंदी में विस्तृत उत्तर दें और संस्कृत श्लोकों को भी शामिल करें।

उत्तर:"""

    def _create_english_prompt(self, query: str, context: str) -> str:
        """Create prompt for English response"""
        return f"""You are an expert on Hindu scriptures. Answer based only on authentic texts.

Context from Hindu Scriptures:
{context}

Question: {query}

Please provide a detailed answer in English, including relevant Sanskrit verses with translations.

Answer:"""

    def _create_sanskrit_prompt(self, query: str, context: str) -> str:
        """Create prompt emphasizing Sanskrit content"""
        return f"""You are a Sanskrit and Hindu scripture expert. Focus on original Sanskrit texts.

Context from Hindu Scriptures:
{context}

Question: {query}

Please provide answer with emphasis on Sanskrit verses, their transliteration, and accurate translations.

Answer:"""

    def _clean_response(self, generated_text: str, original_prompt: str) -> str:
        """Clean and format the generated response"""
        # Remove the original prompt from response
        if original_prompt in generated_text:
            response = generated_text.replace(original_prompt, "").strip()
        else:
            # Fallback: try to extract after "Answer:"
            if "Answer:" in generated_text:
                response = generated_text.split("Answer:", 1)[-1].strip()
            else:
                response = generated_text.strip()
        
        # Basic cleaning
        response = response.replace("</s>", "").replace("<s>", "").strip()
        
        # Limit response length
        max_response_length = 2000
        if len(response) > max_response_length:
            response = response[:max_response_length] + "..."
        
        return response
    
    def _fallback_response(self, query: str, context_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Provide fallback response when LLM fails"""
        
        fallback_text = "I found relevant information from the scriptures, but couldn't generate a complete response. Here are the relevant verses:"
        
        if context_docs:
            verses = []
            for doc in context_docs[:3]:
                content = doc["content"]
                metadata = doc["metadata"]
                
                verse_text = f"""
**{metadata.get('collection', 'Scripture')}** - {metadata.get('file', '')}

Sanskrit: {content.get('sanskrit', 'N/A')}
English: {content.get('english', 'N/A')}
Hindi: {content.get('hindi', 'N/A')}
"""
                verses.append(verse_text)
            
            fallback_text += "\n\n" + "\n---\n".join(verses)
        
        return {
            "response": fallback_text,
            "sources": context_docs,
            "query": query,
            "is_fallback": True
        }
