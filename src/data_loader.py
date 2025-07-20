
# src/data_loader.py - COMPLETE FIXED VERSION

import streamlit as st
import requests
import json
import zipfile
import tempfile
import os
from pathlib import Path

# 🔧 CORRECT FILE ID (ONLY THE ID, NOT FULL URL!)
GDRIVE_ZIP_ID = "1AKXBWVM2ooeZ8MJ5ZeRHS1Ph1JObcDP0"

@st.cache_data
def load_all_scripture_data():
    """Load scripture data from Google Drive ZIP"""
    try:
        # Build correct download URL
        url = f"https://drive.google.com/uc?export=download&id={GDRIVE_ZIP_ID}"
        
        with st.spinner("📥 Loading sacred texts from Drive..."):
            # Download with proper headers and timeout
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, stream=True, timeout=300, headers=headers)
            
            # Handle large file download confirmation
            if 'download_warning' in response.cookies:
                params = {'id': GDRIVE_ZIP_ID, 'confirm': response.cookies['download_warning']}
                response = requests.get(url, params=params, stream=True, timeout=300, headers=headers)
            
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                total_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                        total_size += len(chunk)
                temp_zip_path = temp_file.name
            
            st.info(f"📦 Downloaded {total_size / (1024*1024):.1f} MB, extracting files...")
            
            # Extract and load JSON files
            all_data = {}
            file_count = 0
            
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                json_files = [f for f in zip_ref.namelist() if f.endswith('.json') and not f.startswith('__MACOSX')]
                
                for file_path in json_files:
                    try:
                        with zip_ref.open(file_path) as json_file:
                            content = json_file.read().decode('utf-8')
                            data = json.loads(content)
                            
                            # Use clean filename as key
                            clean_name = Path(file_path).stem
                            
                            # Handle duplicate filenames by adding folder name
                            if clean_name in all_data:
                                folder_name = Path(file_path).parent.name
                                clean_name = f"{folder_name}_{clean_name}" if folder_name != '.' else f"file_{file_count}_{clean_name}"
                            
                            all_data[clean_name] = data
                            file_count += 1
                            
                            # Show progress for large datasets
                            if file_count % 10 == 0:
                                st.info(f"📚 Processed {file_count} scripture files...")
                                
                    except json.JSONDecodeError as e:
                        st.warning(f"⚠️ Skipped invalid JSON file: {file_path}")
                        continue
                    except Exception as e:
                        st.warning(f"⚠️ Error processing {file_path}: {str(e)}")
                        continue
            
            # Cleanup temporary file
            try:
                os.unlink(temp_zip_path)
            except:
                pass  # Ignore cleanup errors
            
            if all_data:
                st.success(f"✅ Successfully loaded {len(all_data)} scripture files!")
                
                # Show summary of loaded collections
                collections = {}
                for filename in all_data.keys():
                    collection = get_collection_from_filename(filename)
                    collections[collection] = collections.get(collection, 0) + 1
                
                summary_text = " | ".join([f"{col}: {count}" for col, count in collections.items()])
                st.info(f"📖 Collections loaded: {summary_text}")
                
                return all_data
            else:
                st.error("❌ No valid JSON files found in the ZIP archive")
                return {}
            
    except requests.exceptions.RequestException as e:
        st.error(f"🌐 Network error downloading from Google Drive: {str(e)}")
        return {}
    except zipfile.BadZipFile:
        st.error("📦 Downloaded file is not a valid ZIP archive")
        return {}
    except Exception as e:
        st.error(f"❌ Unexpected error loading scripture data: {str(e)}")
        return {}

def get_collection_from_filename(filename):
    """Extract collection name from filename"""
    filename_lower = filename.lower()
    
    if any(word in filename_lower for word in ['bhagavad', 'gita']):
        return 'Bhagavad Gita'
    elif any(word in filename_lower for word in ['ramayana', 'valmiki']):
        return 'Ramayana'
    elif 'mahabharata' in filename_lower:
        return 'Mahabharata'
    elif any(word in filename_lower for word in ['rigveda', 'rig_veda']):
        return 'Rigveda'
    elif any(word in filename_lower for word in ['yajurveda', 'yajur_veda']):
        return 'Yajurveda'
    elif any(word in filename_lower for word in ['atharvaveda', 'atharva_veda']):
        return 'Atharvaveda'
    elif 'ramcharitmanas' in filename_lower:
        return 'Ramcharitmanas'
    else:
        return 'Other Texts'

# Compatibility class for existing code
class DharmicDataLoader:
    """Data loader class for backward compatibility"""
    
    def __init__(self, data_path=None):
        """Initialize data loader (data_path ignored for Google Drive loading)"""
        self._data = None
        self._raw_data = None
    
    def load_data(self):
        """Load data using Google Drive method"""
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
                'text', 'content', 'verse', 'shloka', 'mantra',
                'sanskrit', 'devanagari', 'hindi', 'english',
                'translation', 'meaning', 'commentary'
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

# Simple access functions for direct use
def get_scripture_data():
    """Simple function to get raw scripture data"""
    return load_all_scripture_data()

def get_all_scripture_data():
    """Alternative function name for getting raw scripture data"""
    return load_all_scripture_data()

def get_formatted_scripture_data():
    """Get scripture data formatted for RAG processing"""
    loader = DharmicDataLoader()
    return loader.load_all_texts()

# Test function for development
def test_data_loading():
    """Test the data loading functionality"""
    st.write("🧪 Testing Google Drive data loading...")
    
    try:
        data = load_all_scripture_data()
        
        if data:
            st.success(f"✅ Test successful! Loaded {len(data)} files")
            
            # Show sample data structure
            sample_key = list(data.keys())[0]
            sample_data = data[sample_key]
            
            st.write(f"📋 Sample data from '{sample_key}':")
            if isinstance(sample_data, list):
                st.write(f"   - Type: List with {len(sample_data)} items")
                if sample_data:
                    st.write(f"   - First item keys: {list(sample_data[0].keys()) if isinstance(sample_data[0], dict) else 'Not a dictionary'}")
            elif isinstance(sample_data, dict):
                st.write(f"   - Type: Dictionary with keys: {list(sample_data.keys())}")
            else:
                st.write(f"   - Type: {type(sample_data)}")
                
        else:
            st.error("❌ Test failed - no data loaded")
            
    except Exception as e:
        st.error(f"❌ Test failed with error: {str(e)}")

# Allow running as standalone for testing
if __name__ == "__main__":
    test_data_loading()
