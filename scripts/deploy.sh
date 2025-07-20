
#!/bin/bash

# Kalki GPT Deployment Script

set -e  # Exit on error

echo "🕉️ Kalki GPT Deployment Script"
echo "================================"

# Configuration
APP_NAME="kalki-gpt"
STREAMLIT_PORT=${PORT:-8501}
PYTHON_VERSION="3.9"

# Check if running in production environment
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🚀 Production deployment detected"
    STREAMLIT_CONFIG="--server.headless=true --server.enableCORSProtection=false"
else
    echo "🔧 Development deployment"
    STREAMLIT_CONFIG=""
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command_exists python3; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

if ! command_exists pip; then
    echo "❌ pip is not installed"
    exit 1
fi

echo "✅ Dependencies check passed"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/raw data/processed data/cache models/embeddings logs

# Download data if not exists
if [ ! -d "data/raw" ] || [ -z "$(ls -A data/raw)" ]; then
    echo "📥 Setting up data..."
    python scripts/setup_data.py
else
    echo "✅ Data already exists"
fi

# Pre-generate embeddings if in production
if [ "$ENVIRONMENT" = "production" ] && [ "$PREGENERATE_EMBEDDINGS" = "true" ]; then
    echo "🧠 Pre-generating embeddings..."
    python scripts/generate_embeddings.py --batch-size 16
fi

# Validate data
echo "🔍 Validating data..."
python scripts/validate_data.py --input-dir data/raw

# Set up environment variables
export STREAMLIT_SERVER_PORT=$STREAMLIT_PORT
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Health check function
health_check() {
    echo "🔍 Performing health check..."
    
    # Check if app is responding
    for i in {1..30}; do
        if curl -f http://localhost:$STREAMLIT_PORT/_stcore/health >/dev/null 2>&1; then
            echo "✅ Health check passed"
            return 0
        fi
        echo "⏳ Waiting for app to start... ($i/30)"
        sleep 2
    done
    
    echo "❌ Health check failed"
    return 1
}

# Start the application
echo "🚀 Starting Kalki GPT..."

if [ "$ENVIRONMENT" = "production" ]; then
    # Production: Start with process management
    echo "🏭 Starting in production mode..."
    
    # Start Streamlit in background
    nohup streamlit run app.py \
        --server.port=$STREAMLIT_PORT \
        --server.address=0.0.0.0 \
        --server.headless=true \
        --server.enableCORSProtection=false \
        --browser.gatherUsageStats=false \
        > logs/app.log 2>&1 &
    
    APP_PID=$!
    echo $APP_PID > app.pid
    echo "📝 App PID: $APP_PID (saved to app.pid)"
    
    # Wait a bit for startup
    sleep 10
    
    # Health check
    if health_check; then
        echo "🎉 Kalki GPT deployed successfully!"
        echo "🌐 Access at: http://localhost:$STREAMLIT_PORT"
    else
        echo "❌ Deployment failed"
        kill $APP_PID 2>/dev/null || true
        exit 1
    fi
    
else
    # Development: Start interactively
    echo "🔧 Starting in development mode..."
    streamlit run app.py \
        --server.port=$STREAMLIT_PORT \
        --server.address=0.0.0.0
fi
