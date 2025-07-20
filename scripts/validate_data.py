
#!/usr/bin/env python3
"""
Validate and clean scripture data
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import argparse

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from utils import setup_logging, load_json, save_json
from config import Config

logger = setup_logging()

class DataValidator:
    """Validate scripture data integrity"""
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.errors = []
        self.warnings = []
        self.stats = {}
    
    def validate_all(self) -> Dict[str, Any]:
        """Validate all scripture collections"""
        print("🔍 Starting data validation...")
        
        results = {
            "valid_files": 0,
            "invalid_files": 0,
            "total_verses": 0,
            "collections": {},
            "errors": [],
            "warnings": []
        }
        
        for collection_dir in self.data_path.iterdir():
            if collection_dir.is_dir():
                collection_result = self.validate_collection(collection_dir)
                results["collections"][collection_dir.name] = collection_result
                results["valid_files"] += collection_result["valid_files"]
                results["invalid_files"] += collection_result["invalid_files"]
                results["total_verses"] += collection_result["total_verses"]
        
        results["errors"] = self.errors
        results["warnings"] = self.warnings
        
        return results
    
    def validate_collection(self, collection_path: Path) -> Dict[str, Any]:
        """Validate a single collection"""
        result = {
            "valid_files": 0,
            "invalid_files": 0,
            "total_verses": 0,
            "files": {}
        }
        
        print(f"  📂 Validating {collection_path.name}...")
        
        for json_file in collection_path.glob("*.json"):
            file_result = self.validate_file(json_file)
            result["files"][json_file.name] = file_result
            
            if file_result["is_valid"]:
                result["valid_files"] += 1
            else:
                result["invalid_files"] += 1
            
            result["total_verses"] += file_result["verse_count"]
        
        return result
    
    def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate a single JSON file"""
        result = {
            "is_valid": True,
            "verse_count": 0,
            "errors": [],
            "warnings": []
        }
        
        try:
            data = load_json(str(file_path))
            
            if data is None:
                result["is_valid"] = False
                result["errors"].append("Failed to load JSON")
                return result
            
            # Validate structure
            verse_count = self.count_verses(data)
            result["verse_count"] = verse_count
            
            if verse_count == 0:
                result["warnings"].append("No verses found")
                self.warnings.append(f"{file_path}: No verses found")
            
            # Check for required fields
            if isinstance(data, list):
                for i, item in enumerate(data[:5]):  # Check first 5 items
                    self.validate_verse_structure(item, file_path, i, result)
            elif isinstance(data, dict):
                self.validate_verse_structure(data, file_path, 0, result)
            
        except Exception as e:
            result["is_valid"] = False
            result["errors"].append(f"Validation error: {str(e)}")
            self.errors.append(f"{file_path}: {str(e)}")
        
        return result
    
    def count_verses(self, data: Any) -> int:
        """Count verses in data structure"""
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            if 'verses' in data:
                return len(data['verses'])
            elif 'shlokas' in data:
                return len(data['shlokas'])
            else:
                return 1
        else:
            return 0
    
    def validate_verse_structure(self, verse: Any, file_path: Path, index: int, result: Dict[str, Any]):
        """Validate structure of individual verse"""
        if not isinstance(verse, (dict, str)):
            result["warnings"].append(f"Verse {index}: Unexpected type {type(verse)}")
            return
        
        if isinstance(verse, str):
            if len(verse.strip()) == 0:
                result["warnings"].append(f"Verse {index}: Empty content")
            return
        
        # Check for text content
        text_fields = ['sanskrit', 'hindi', 'english', 'text', 'sloka', 'translation']
        has_text = any(field in verse and verse[field] for field in text_fields)
        
        if not has_text:
            result["warnings"].append(f"Verse {index}: No text content found")
    
    def clean_data(self, input_path: str, output_path: str):
        """Clean and normalize data"""
        print("🧹 Cleaning data...")
        
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
        for collection_dir in Path(input_path).iterdir():
            if collection_dir.is_dir():
                output_collection = Path(output_path) / collection_dir.name
                output_collection.mkdir(exist_ok=True)
                
                for json_file in collection_dir.glob("*.json"):
                    self.clean_file(json_file, output_collection / json_file.name)
        
        print("✅ Data cleaning completed")
    
    def clean_file(self, input_file: Path, output_file: Path):
        """Clean individual file"""
        try:
            data = load_json(str(input_file))
            if data is None:
                return
            
            cleaned_data = self.clean_verses(data)
            save_json(cleaned_data, str(output_file))
            
        except Exception as e:
            logger.error(f"Error cleaning {input_file}: {e}")
    
    def clean_verses(self, data: Any) -> Any:
        """Clean verse data"""
        if isinstance(data, list):
            return [self.clean_verse(verse) for verse in data if verse]
        elif isinstance(data, dict):
            if 'verses' in data:
                data['verses'] = [self.clean_verse(verse) for verse in data['verses'] if verse]
            elif 'shlokas' in data:
                data['shlokas'] = [self.clean_verse(verse) for verse in data['shlokas'] if verse]
            else:
                return self.clean_verse(data)
        return data
    
    def clean_verse(self, verse: Any) -> Any:
        """Clean individual verse"""
        if isinstance(verse, str):
            return verse.strip()
        elif isinstance(verse, dict):
            cleaned = {}
            for key, value in verse.items():
                if isinstance(value, str):
                    cleaned[key] = value.strip()
                else:
                    cleaned[key] = value
            return cleaned
        return verse
    
    def generate_report(self, results: Dict[str, Any], output_file: str):
        """Generate validation report"""
        report = {
            "summary": {
                "total_files": results["valid_files"] + results["invalid_files"],
                "valid_files": results["valid_files"],
                "invalid_files": results["invalid_files"],
                "total_verses": results["total_verses"],
                "success_rate": results["valid_files"] / (results["valid_files"] + results["invalid_files"]) * 100
            },
            "collections": results["collections"],
            "errors": results["errors"][:50],  # Limit errors in report
            "warnings": results["warnings"][:50]  # Limit warnings in report
        }
        
        save_json(report, output_file)
        
        # Print summary
        print("\n📊 Validation Summary:")
        print(f"   Total files: {report['summary']['total_files']}")
        print(f"   Valid files: {report['summary']['valid_files']}")
        print(f"   Invalid files: {report['summary']['invalid_files']}")
        print(f"   Total verses: {report['summary']['total_verses']}")
        print(f"   Success rate: {report['summary']['success_rate']:.1f}%")
        
        if results["errors"]:
            print(f"   ❌ {len(results['errors'])} errors found")
        if results["warnings"]:
            print(f"   ⚠️ {len(results['warnings'])} warnings found")

def main():
    parser = argparse.ArgumentParser(description="Validate scripture data for Kalki GPT")
    parser.add_argument("--input-dir", type=str, default=Config.DATA_PATH, help="Input data directory")
    parser.add_argument("--output-dir", type=str, help="Output directory for cleaned data")
    parser.add_argument("--report", type=str, default="data_validation_report.json", help="Validation report file")
    parser.add_argument("--clean", action="store_true", help="Clean data after validation")
    
    args = parser.parse_args()
    
    print("🕉️ Kalki GPT Data Validator")
    print("=" * 40)
    
    if not Path(args.input_dir).exists():
        print(f"❌ Input directory does not exist: {args.input_dir}")
        sys.exit(1)
    
    validator = DataValidator(args.input_dir)
    
    # Validate data
    results = validator.validate_all()
    
    # Generate report
    validator.generate_report(results, args.report)
    print(f"📄 Report saved to: {args.report}")
    
    # Clean data if requested
    if args.clean and args.output_dir:
        validator.clean_data(args.input_dir, args.output_dir)
        print(f"🧹 Cleaned data saved to: {args.output_dir}")
    
    # Exit with appropriate code
    if results["invalid_files"] > 0:
        print(f"\n⚠️ {results['invalid_files']} files have validation issues")
        sys.exit(1)
    else:
        print("\n✅ All files passed validation!")
        sys.exit(0)

if __name__ == "__main__":
    main()
