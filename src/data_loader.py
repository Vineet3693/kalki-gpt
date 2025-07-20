
# ADD THIS TO YOUR EXISTING src/data_loader.py file

import streamlit as st
import requests
import json
import zipfile
import tempfile
import os
from pathlib import Path

# 🔧 YOUR ACTUAL GOOGLE DRIVE FILE ID
GDRIVE_ZIP_ID = "1AKXBWVM2ooeZ8MJ5ZeRHS1Ph1JObcDP0"

@st.cache_data
def load_scripture_data_from_drive():
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

def get_all_scripture_data():
    """Get all scripture data - use this in your app"""
    return load_scripture_data_from_drive()
