
#!/bin/bash

# Restore Script for Kalki GPT Data

set -e

echo "🔄 Kalki GPT Restore Script"
echo "=========================="

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    echo ""
    echo "Available backups:"
    ls -la backups/kalki_gpt_backup_*.tar.gz 2>/dev/null || echo "No backups found in backups/ directory"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "📦 Restoring from: $BACKUP_FILE"

# Create temporary directory for extraction
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Extract backup
echo "📂 Extracting backup..."
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Find the backup directory (should be the only directory in temp)
BACKUP_DIR=$(find "$TEMP_DIR" -maxdepth 1 -type d -not -path "$TEMP_DIR")

if [ -z "$BACKUP_DIR" ]; then
    echo "❌ Invalid backup structure"
    exit 1
fi

# Confirm restore
echo "⚠️ This will overwrite existing data. Continue? (y/N)"
read -r CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "❌ Restore cancelled"
    exit 0
fi

# Stop running application
if [ -f "app.pid" ]; then
    echo "🛑 Stopping running application..."
    ./scripts/stop.sh
fi

# Backup current data (just in case)
if [ -d "data" ]; then
    CURRENT_BACKUP="data_before_restore_$(date +%Y%m%d_%H%M%S)"
    echo "💾 Backing up current data to $CURRENT_BACKUP..."
    mv data "$CURRENT_BACKUP"
fi

# Restore data
if [ -d "$BACKUP_DIR/data" ]; then
    echo "📚 Restoring scripture data..."
    cp -r "$BACKUP_DIR/data" .
else
    echo "⚠️ No data directory in backup"
fi

# Restore models
if [ -d "$BACKUP_DIR/models" ]; then
    echo "🧠 Restoring models..."
    cp -r "$BACKUP_DIR/models" .
else
    echo "⚠️ No models directory in backup"
fi

# Restore configuration
if [ -d "$BACKUP_DIR/.streamlit" ]; then
    echo "⚙️ Restoring Streamlit configuration..."
    cp -r "$BACKUP_DIR/.streamlit" .
fi

if [ -f "$BACKUP_DIR/config.py" ]; then
    echo "⚙️ Restoring application configuration..."
    cp "$BACKUP_DIR/config.py" .
fi

# Restore logs
if [ -d "$BACKUP_DIR/logs" ]; then
    echo "📝 Restoring logs..."
    mkdir -p logs
    cp -r "$BACKUP_DIR/logs/"* logs/
fi

echo "✅ Restore completed successfully!"
echo "🚀 You can now start Kalki GPT with: ./scripts/deploy.sh"
