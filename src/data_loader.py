
# src/data_loader.py - REPLACE ENTIRE FILE WITH THIS:

import streamlit as st
import requests
import json
import zipfile
import tempfile
import os
from pathlib import Path

# 🔧 CORRECT FILE ID (NO FULL URL!)
GDRIVE_ZIP_ID = "1AKXBWVM2ooeZ8MJ5ZeRHS1Ph1JObcDP0"  # ← ONLY FILE ID

@st.cache_data
def load_all_scripture_data():
    """Load scripture data from Google Drive ZIP"""
    try:
        url = f"https://drive.google.com/uc?export=download&id={GDRIVE_ZIP_ID}"
        
        with st.spinner("📥 Loading sacred texts from Drive..."):
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                temp_zip_path = temp_file.name
            
            all_data = {}
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                for file_path in zip_ref.namelist():
                    if file_path.endswith('.json'):
                        try:
                            with zip_ref.open(file_path) as json_file:
                                content = json_file.read().decode('utf-8')
                                data = json.loads(content)
                                clean_name = Path(file_path).stem
                                all_data[clean_name] = data
                        except:
                            continue
            
            os.unlink(temp_zip_path)
            st.success(f"✅ Loaded {len(all_data)} scripture files")
            return all_data
            
    except Exception as e:
        st.error(f"❌ Failed to load scripture data: {e}")
        return {}

# Keep your existing class name for compatibility
class DharmicDataLoader:
    def __init__(self):
        self.data = None
    
    def load_data(self):
        """Load data using the new Google Drive method"""
        if self.data is None:
            self.data = load_all_scripture_data()
        return self.data
    
    def get_all_texts(self):
        """Get all loaded texts"""
        if self.data is None:
            self.data = load_all_scripture_data()
        return self.data

# Additional functions for compatibility
def get_scripture_data():
    """Simple function to get all scripture data"""
    return load_all_scripture_data()

def get_all_scripture_data():
    """Alternative function name"""
    return load_all_scripture_data()
