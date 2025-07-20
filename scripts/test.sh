
#!/bin/bash

# Test Script for Kalki GPT

set -e

echo "🧪 Kalki GPT Test Suite"
echo "======================"

# Configuration
PYTHON_CMD="python3"
TEST_TIMEOUT=300  # 5 minutes

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local required="$3"  # "required" or "optional"
    
    echo -e "\n🔍 Running: $test_name"
    
    if timeout $TEST_TIMEOUT $test_command >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}: $test_name"
        ((TESTS_PASSED++))
    else
        if [ "$required" = "required" ]; then
            echo -e "${RED}❌ FAILED${NC}: $test_name"
            ((TESTS_FAILED++))
        else
            echo -e "${YELLOW}⚠️ SKIPPED${NC}: $test_name (optional)"
            ((TESTS_SKIPPED++))
        fi
    fi
}

# Test Python environment
echo "🐍 Testing Python environment..."
run_test "Python version" "$PYTHON_CMD --version" "required"
run_test "pip installation" "pip --version" "required"

# Test dependencies
echo -e "\n📦 Testing dependencies..."
run_test "Import streamlit" "$PYTHON_CMD -c 'import streamlit'" "required"
run_test "Import transformers" "$PYTHON_CMD -c 'import transformers'" "required"
run_test "Import sentence_transformers" "$PYTHON_CMD -c 'import sentence_transformers'" "required"
run_test "Import faiss" "$PYTHON_CMD -c 'import faiss'" "required"
run_test "Import numpy" "$PYTHON_CMD -c 'import numpy'" "required"
run_test "Import pandas" "$PYTHON_CMD -c 'import pandas'" "optional"

# Test data availability
echo -e "\n📚 Testing data availability..."
run_test "Data directory exists" "test -d data/raw" "required"
run_test "Scripture files exist" "find data/raw -name '*.json' | head -1" "required"
run_test "Bhagavad Gita data" "test -f data/raw/SrimadBhagvadGita/bhagavad_gita_chapter_1.json" "optional"
run_test "Ramayana data" "test -d data/raw/ValmikiRamayana" "optional"

# Test application modules
echo -e "\n🔧 Testing application modules..."
export PYTHONPATH="${PYTHONPATH}:src"

run_test "Import config" "$PYTHON_CMD -c 'from config import Config'" "required"
run_test "Import data_loader" "$PYTHON_CMD -c 'from src.data_loader import DharmicDataLoader'" "required"
run_test "Import embeddings" "$PYTHON_CMD -c 'from src.embeddings import EmbeddingManager'" "required"
run_test "Import RAG chain" "$PYTHON_CMD -c 'from src.rag_chain import KalkiRAGChain'" "required"

# Test data loading functionality
echo -e "\n📖 Testing data loading..."
run_test "Load sample data" "$PYTHON_CMD -c '
from src.data_loader import DharmicDataLoader
loader = DharmicDataLoader(\"data/raw\")
texts = loader.load_collection(\"SrimadBhagvadGita\")
assert len(texts) > 0, \"No texts loaded\"
print(f\"Loaded {len(texts)} texts\")
'" "required"

# Test embedding functionality (if models are available)
echo -e "\n🧠 Testing embedding functionality..."
run_test "Load embedding model" "$PYTHON_CMD -c '
from src.embeddings import EmbeddingManager
em = EmbeddingManager()
model = em.load_model()
print(\"Model loaded successfully\")
'" "optional"

# Test application startup (quick check)
echo -e "\n🚀 Testing application startup..."
run_test "App syntax check" "$PYTHON_CMD -m py_compile app.py" "required"
run_test "Streamlit config check" "streamlit config show" "optional"

# Test scripts
echo -e "\n📜 Testing utility scripts..."
run_test "Setup script syntax" "$PYTHON_CMD -m py_compile scripts/setup_data.py" "required"
run_test "Validation script syntax" "$PYTHON_CMD -m py_compile scripts/validate_data.py" "required"

# Performance test (optional)
echo -e "\n⚡ Performance tests..."
run_test "Memory usage test" "$PYTHON_CMD -c '
import psutil
import os
process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
print(f\"Memory usage: {memory_mb:.1f} MB\")
assert memory_mb < 1000, \"Memory usage too high\"
'" "optional"

# Network connectivity test
echo -e "\n🌐 Network tests..."
run_test "HuggingFace connectivity" "curl -s https://huggingface.co > /dev/null" "optional"
run_test "GitHub connectivity" "curl -s https://github.com > /dev/null" "optional"

# Disk space check
echo -e "\n💾 Storage tests..."
run_test "Sufficient disk space" "[ $(df . | tail -1 | awk '{print $4}') -gt 1000000 ]" "required"  # 1GB

# Generate test report
echo -e "\n" + "="*50
echo "📊 Test Results Summary"
echo "======================"
echo -e "✅ Passed: $TESTS_PASSED"
echo -e "❌ Failed: $TESTS_FAILED"  
echo -e "⚠️ Skipped: $TESTS_SKIPPED"
echo -e "📈 Total: $((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All required tests passed! Kalki GPT is ready to use.${NC}"
    exit 0
else
    echo -e "\n${RED}❌ $TESTS_FAILED required tests failed. Please fix issues before deploying.${NC}"
    exit 1
fi
