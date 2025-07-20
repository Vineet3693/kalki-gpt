
import streamlit as st
import requests
import json
import zipfile
import tempfile
import os
from pathlib import Path

# 🔧 CONFIGURATION - ONLY CHANGE THIS LINE
GDRIVE_ZIP_ID = "https://drive.google.com/file/d/1AKXBWVM2ooeZ8MJ5ZeRHS1Ph1JObcDP0/view?usp=drive_link"  # ← PUT YOUR DRIVE FILE ID HERE

@st.cache_data
def load_all_scripture_data():
    """
    Universal scripture data loader from Google Drive ZIP
    NO CHANGES NEEDED - Just replace the GDRIVE_ZIP_ID above
    """
    try:
        # Download ZIP from Google Drive
        url = f"https://drive.google.com/uc?export=download&id={GDRIVE_ZIP_ID}"
        
        with st.spinner("📥 Loading sacred texts from Drive..."):
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                temp_zip_path = temp_file.name
            
            # Extract all JSON files
            all_data = {}
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                for file_path in zip_ref.namelist():
                    if file_path.endswith('.json'):
                        try:
                            with zip_ref.open(file_path) as json_file:
                                content = json_file.read().decode('utf-8')
                                data = json.loads(content)
                                
                                # Use clean file name as key
                                clean_name = Path(file_path).stem
                                all_data[clean_name] = data
                                
                        except Exception as e:
                            continue  # Skip problematic files
            
            # Cleanup
            os.unlink(temp_zip_path)
            
            st.success(f"✅ Loaded {len(all_data)} scripture files")
            return all_data
            
    except Exception as e:
        st.error(f"❌ Failed to load scripture data: {e}")
        return {}

# Export function for easy import
def get_scripture_data():
    """Simple function to get all scripture data"""
    return load_all_scripture_data()
