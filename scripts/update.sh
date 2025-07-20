
#!/bin/bash

# Update Script for Kalki GPT

set -e

echo "🔄 Kalki GPT Update Script"
echo "========================="

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Cannot update from repository."
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository. Cannot update."
    exit 1
fi

# Create backup before update
echo "💾 Creating backup before update..."
./scripts/backup.sh

# Stop running application
if [ -f "app.pid" ]; then
    echo "🛑 Stopping application..."
    ./scripts/stop.sh
fi

# Stash local changes
echo "📦 Stashing local changes..."
git stash push -m "Auto-stash before update $(date)"

# Pull latest changes
echo "⬇️ Pulling latest changes..."
git pull origin main

# Update dependencies
echo "📦 Updating dependencies..."
pip install --upgrade -r requirements.txt

# Update data if needed
echo "📚 Checking for data updates..."
if [ -f "scripts/setup_data.py" ]; then
    python scripts/setup_data.py --update-only 2>/dev/null || echo "⚠️ Data update not available"
fi

# Validate updated data
echo "🔍 Validating data after update..."
python scripts/validate_data.py --input-dir data/raw

# Clear cache to force rebuild
echo "🧹 Clearing cache..."
rm -rf data/cache/* models/embeddings/* 2>/dev/null || true

echo "✅ Update completed!"
echo "🚀 Start the application with: ./scripts/deploy.sh"
echo "📋 Check CHANGELOG.md for details about this update"

# Show recent commits
echo ""
echo "📝 Recent changes:"
git log --oneline -5
