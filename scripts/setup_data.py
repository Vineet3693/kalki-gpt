#!/usr/bin/env python3
"""
Setup script to download and prepare DharmicData for Kalki GPT
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any
import requests
import zipfile
import shutil

def setup_directories():
    """Create necessary directory structure"""
    directories = [
        "data/raw",
        "data/processed", 
        "data/cache",
        "models/embeddings",
        "models/cache",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def download_dharmic_data():
    """Download DharmicData repository"""
    print("📥 Downloading DharmicData repository...")
    
    repo_url = "https://github.com/bhavykhatri/DharmicData/archive/refs/heads/main.zip"
    
    try:
        response = requests.get(repo_url, stream=True)
        response.raise_for_status()
        
        with open("dharmic_data.zip", "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("✅ Downloaded DharmicData successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error downloading DharmicData: {e}")
        return False

def extract_and_organize_data():
    """Extract and organize the downloaded data"""
    print("📂 Extracting and organizing data...")
    
    try:
        with zipfile.ZipFile("dharmic_data.zip", "r") as zip_ref:
            zip_ref.extractall("temp_data")
        
        # Move data to correct locations
        source_dir = Path("temp_data/DharmicData-main")
        target_dir = Path("data/raw")
        
        # Copy all scripture directories
        scripture_dirs = [
            "AtharvaVeda", "Mahabharata", "Ramcharitmanas", 
            "Rigveda", "SrimadBhagvadGita", "ValmikiRamayana", "Yajurveda"
        ]
        
        for dir_name in scripture_dirs:
            source_path = source_dir / dir_name
            target_path = target_dir / dir_name
            
            if source_path.exists():
                shutil.copytree(source_path, target_path, dirs_exist_ok=True)
                print(f"✅ Copied {dir_name}")
            else:
                print(f"⚠️ Directory not found: {dir_name}")
        
        # Cleanup
        shutil.rmtree("temp_data")
        os.remove("dharmic_data.zip")
        
        print("✅ Data extraction completed")
        return True
        
    except Exception as e:
        print(f"❌ Error extracting data: {e}")
        return False

def validate_data():
    """Validate the downloaded data"""
    print("🔍 Validating data...")
    
    data_dir = Path("data/raw")
    stats = {}
    total_files = 0
    
    for scripture_dir in data_dir.iterdir():
        if scripture_dir.is_dir():
            json_files = list(scripture_dir.glob("*.json"))
            stats[scripture_dir.name] = len(json_files)
            total_files += len(json_files)
            
            # Validate each JSON file
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        json.load(f)
                except Exception as e:
                    print(f"⚠️ Invalid JSON file: {json_file} - {e}")
    
    print(f"✅ Validation complete:")
    for scripture, count in stats.items():
        print(f"   {scripture}: {count} files")
    print(f"   Total: {total_files} JSON files")
    
    # Save stats
    with open("data/processed/data_stats.json", "w", encoding="utf-8") as f:
        json.dump({
            "scripture_counts": stats,
            "total_files": total_files,
            "validation_date": str(Path(__file__).stat().st_mtime)
        }, f, indent=2)
    
    return total_files > 0

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_sample_config():
    """Create sample configuration files"""
    print("⚙️ Creating configuration files...")
    
    # Create .streamlit directory and config
    streamlit_dir = Path(".streamlit")
    streamlit_dir.mkdir(exist_ok=True)
    
    config_content = """[theme]
primaryColor = "#FF6B35"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "serif"

[server]
headless = true
port = 8501
enableCORSProtection = false
maxUploadSize = 1024

[browser]
gatherUsageStats = false
showErrorDetails = false
"""
    
    with open(streamlit_dir / "config.toml", "w") as f:
        f.write(config_content)
    
    print("✅ Configuration files created")

def test_setup():
    """Test the setup by loading a sample text"""
    print("🧪 Testing setup...")
    
    try:
        # Test import of main modules
        sys.path.append("src")
        from data_loader import DharmicDataLoader
        
        # Test loading data
        loader = DharmicDataLoader("data/raw")
        texts = loader.load_all_texts()
        
        if len(texts) > 0:
            print(f"✅ Setup test passed: Loaded {len(texts)} texts")
            return True
        else:
            print("❌ Setup test failed: No texts loaded")
            return False
            
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🕉️ Kalki GPT Setup Script")
    print("=" * 40)
    
    steps = [
        ("Setting up directories", setup_directories),
        ("Downloading DharmicData", download_dharmic_data),
        ("Extracting and organizing data", extract_and_organize_data),
        ("Validating data", validate_data),
        ("Installing dependencies", install_dependencies),
        ("Creating configuration", create_sample_config),
        ("Testing setup", test_setup)
    ]
    
    success_count = 0
    
    for step_name, step_function in steps:
        print(f"\n🔄 {step_name}...")
        try:
            if step_function():
                success_count += 1
            else:
                print(f"⚠️ {step_name} completed with warnings")
        except Exception as e:
            print(f"❌ {step_name} failed: {e}")
    
    print("\n" + "=" * 40)
    print(f"Setup completed: {success_count}/{len(steps)} steps successful")
    
    if success_count == len(steps):
        print("🎉 Kalki GPT is ready to use!")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Open browser to http://localhost:8501")
        print("3. Click 'Initialize System' in the sidebar")
        print("4. Start asking questions about Hindu scriptures!")
    else:
        print("⚠️ Some steps failed. Please check the errors above.")
        print("You may need to manually complete some setup steps.")

if __name__ == "__main__":
    main()
