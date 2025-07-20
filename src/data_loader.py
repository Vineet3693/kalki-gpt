
# src/data_loader.py - COMPLETE FILE FOR YOUR SETUP

import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, Any, List

# 🔧 DATA PATH CONFIGURATION
DATA_DIR = "data"  # Your GitHub data folder

@st.cache_data
def load_all_scripture_data():
    """Load scripture data from local GitHub files"""
    try:
        with st.spinner("📥 Loading sacred texts from GitHub..."):
            all_data = {}
            data_path = Path(DATA_DIR)
            
            if not data_path.exists():
                st.error(f"❌ Data directory '{DATA_DIR}' not found in repository")
                return {}
            
            file_count = 0
            total_files = 0
            
            # Count total files first
            for root, dirs, files in os.walk(data_path):
                total_files += len([f for f in files if f.endswith('.json')])
            
            st.info(f"📚 Found {total_files} JSON files to process...")
            
            # Load all JSON files
            for root, dirs, files in os.walk(data_path):
                folder_name = Path(root).name
                
                for file in files:
                    if file.endswith('.json'):
                        file_path = Path(root) / file
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            
                            # Create key: foldername_filename
                            clean_filename = file_path.stem
                            if folder_name != DATA_DIR:
                                key = f"{folder_name}_{clean_filename}"
                            else:
                                key = clean_filename
                            
                            # Handle duplicate keys
                            original_key = key
                            counter = 1
                            while key in all_data:
                                key = f"{original_key}_{counter}"
                                counter += 1
                            
                            all_data[key] = data
                            file_count += 1
                            
                            # Show progress
                            if file_count % 5 == 0 or file_count == total_files:
                                progress = (file_count / total_files) * 100
                                st.info(f"📖 Progress: {file_count}/{total_files} files ({progress:.0f}%)")
                                
                        except json.JSONDecodeError:
                            st.warning(f"⚠️ Skipped invalid JSON: {file_path.name}")
                            continue
                        except Exception as e:
                            st.warning(f"⚠️ Error loading {file_path.name}: {str(e)}")
                            continue
            
            if all_data:
                st.success(f"✅ Successfully loaded {len(all_data)} scripture files!")
                
                # Show detailed collection summary
                collections = {}
                for key in all_data.keys():
                    collection = get_collection_from_filename(key)
                    collections[collection] = collections.get(collection, 0) + 1
                
                # Display collection summary
                st.markdown("### 📖 Loaded Collections:")
                for collection, count in collections.items():
                    st.markdown(f"- **{collection}**: {count} files")
                
                return all_data
            else:
                st.error("❌ No valid JSON files found in data directory")
                return {}
                
    except Exception as e:
        st.error(f"❌ Error loading scripture data: {str(e)}")
        return {}

def get_collection_from_filename(filename):
    """Extract collection name from filename - Optimized for your data"""
    filename_lower = filename.lower()
    
    # Handle your specific folder names
    if any(word in filename_lower for word in ['ramcharitmanas', 'ramcharit']):
        return 'Ramcharitmanas'
    elif any(word in filename_lower for word in ['valmiki', 'valmikiramayana']):
        return 'Valmiki Ramayana'
    elif any(word in filename_lower for word in ['ramayana', 'ramayan']):
        return 'Ramayana'
    elif any(word in filename_lower for word in ['bhagavad', 'gita']):
        return 'Bhagavad Gita'
    elif 'mahabharata' in filename_lower:
        return 'Mahabharata'
    elif any(word in filename_lower for word in ['rigveda', 'rig_veda']):
        return 'Rigveda'
    elif any(word in filename_lower for word in ['yajurveda', 'yajur_veda']):
        return 'Yajurveda'
    elif any(word in filename_lower for word in ['atharvaveda', 'atharva_veda']):
        return 'Atharvaveda'
    else:
        return 'Sacred Texts'

# Compatibility class for existing RAG code
class DharmicDataLoader:
    """Data loader class for backward compatibility"""
    
    def __init__(self, data_path=None):
        """Initialize data loader"""
        self._data = None
        self._raw_data = None
        self.data_path = data_path or DATA_DIR
    
    def load_data(self):
        """Load raw data"""
        if self._raw_data is None:
            self._raw_data = load_all_scripture_data()
        return self._raw_data
    
    def load_all_texts(self):
        """Load and format all texts for RAG processing"""
        if self._data is None:
            raw_data = self.load_data()
            self._data = self._convert_to_rag_format(raw_data)
        return self._data
    
    def get_all_texts(self):
        """Get all loaded texts (alias for load_all_texts)"""
        return self.load_all_texts()
    
    def _convert_to_rag_format(self, raw_data):
        """Convert raw JSON data to RAG-compatible format"""
        formatted_texts = []
        
        for filename, file_content in raw_data.items():
            collection = get_collection_from_filename(filename)
            
            try:
                if isinstance(file_content, list):
                    # Handle list of items (verses, chapters, etc.)
                    for idx, item in enumerate(file_content):
                        formatted_item = {
                            "id": f"{filename}_{idx}",
                            "content": self._extract_content_fields(item),
                            "metadata": {
                                "collection": collection.lower().replace(' ', '_'),
                                "source_file": filename,
                                "item_index": idx,
                                "total_items": len(file_content),
                                "collection_display": collection
                            }
                        }
                        formatted_texts.append(formatted_item)
                
                elif isinstance(file_content, dict):
                    # Handle single dictionary
                    formatted_item = {
                        "id": filename,
                        "content": self._extract_content_fields(file_content),
                        "metadata": {
                            "collection": collection.lower().replace(' ', '_'),
                            "source_file": filename,
                            "item_index": 0,
                            "total_items": 1,
                            "collection_display": collection
                        }
                    }
                    formatted_texts.append(formatted_item)
                
                else:
                    # Handle other data types
                    formatted_item = {
                        "id": filename,
                        "content": {"text": str(file_content)},
                        "metadata": {
                            "collection": collection.lower().replace(' ', '_'),
                            "source_file": filename,
                            "item_index": 0,
                            "total_items": 1,
                            "collection_display": collection
                        }
                    }
                    formatted_texts.append(formatted_item)
                    
            except Exception as e:
                st.warning(f"⚠️ Error processing {filename}: {str(e)}")
                continue
        
        return formatted_texts
    
    def _extract_content_fields(self, item):
        """Extract text content from various field structures"""
        content = {}
        
        if isinstance(item, dict):
            # Common field names for different languages/formats
            text_fields = [
                'text', 'content', 'verse', 'shloka', 'mantra', 'doha', 'chaupai',
                'sanskrit', 'devanagari', 'hindi', 'english', 'translation', 
                'meaning', 'commentary', 'explanation'
            ]
            
            for field in text_fields:
                if field in item and item[field]:
                    content[field] = str(item[field]).strip()
            
            # If no text fields found, convert entire dict to text
            if not content:
                content['text'] = str(item)
        else:
            content['text'] = str(item)
        
        return content

# Simple access functions
def get_scripture_data():
    """Get raw scripture data"""
    return load_all_scripture_data()

def get_all_scripture_data():
    """Alternative function name"""
    return load_all_scripture_data()

def get_formatted_scripture_data():
    """Get formatted scripture data for RAG"""
    loader = DharmicDataLoader()
    return loader.load_all_texts()

# Test function
def test_data_loading():
    """Test the data loading functionality"""
    st.write("🧪 Testing GitHub data loading...")
    
    try:
        data = load_all_scripture_data()
        
        if data:
            st.success(f"✅ Test successful! Loaded {len(data)} files")
            
            # Show data structure for first few files
            for i, (key, content) in enumerate(list(data.items())[:3]):
                st.write(f"📄 **File {i+1}: {key}**")
                if isinstance(content, list):
                    st.write(f"   - Type: List with {len(content)} items")
                    if content:
                        first_item = content[0]
                        if isinstance(first_item, dict):
                            st.write(f"   - Sample keys: {list(first_item.keys())[:5]}...")
                elif isinstance(content, dict):
                    st.write(f"   - Type: Dictionary with keys: {list(content.keys())[:5]}...")
                else:
                    st.write(f"   - Type: {type(content)}")
                st.write("---")
        else:
            st.error("❌ Test failed - no data loaded")
            
    except Exception as e:
        st.error(f"❌ Test failed with error: {str(e)}")

# Allow running as standalone for testing
if __name__ == "__main__":
    test_data_loading()
