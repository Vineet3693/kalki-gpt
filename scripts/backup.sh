
#!/bin/bash

# Backup Script for Kalki GPT Data

set -e

echo "💾 Kalki GPT Backup Script"
echo "=========================="

# Configuration
BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="kalki_gpt_backup_$TIMESTAMP"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "📂 Creating backup: $BACKUP_NAME"

# Create backup structure
mkdir -p "$BACKUP_PATH"

# Backup data
if [ -d "data" ]; then
    echo "📚 Backing up scripture data..."
    cp -r data "$BACKUP_PATH/"
else
    echo "⚠️ No data directory found"
fi

# Backup models (if they exist)
if [ -d "models" ]; then
    echo "🧠 Backing up models..."
    cp -r models "$BACKUP_PATH/"
fi

# Backup configuration
echo "⚙️ Backing up configuration..."
cp -r .streamlit "$BACKUP_PATH/" 2>/dev/null || echo "No .streamlit config found"
cp config.py "$BACKUP_PATH/" 2>/dev/null || echo "No config.py found"
cp requirements.txt "$BACKUP_PATH/" 2>/dev/null || echo "No requirements.txt found"

# Backup logs (recent only)
if [ -d "logs" ]; then
    echo "📝 Backing up recent logs..."
    mkdir -p "$BACKUP_PATH/logs"
    find logs -name "*.log" -mtime -7 -exec cp {} "$BACKUP_PATH/logs/" \; 2>/dev/null || true
fi

# Create archive
echo "🗜️ Creating compressed archive..."
tar -czf "$BACKUP_PATH.tar.gz" -C "$BACKUP_DIR" "$BACKUP_NAME"

# Remove uncompressed backup
rm -rf "$BACKUP_PATH"

# Get backup size
BACKUP_SIZE=$(du -h "$BACKUP_PATH.tar.gz" | cut -f1)

echo "✅ Backup completed!"
echo "📁 Location: $BACKUP_PATH.tar.gz"
echo "📏 Size: $BACKUP_SIZE"

# Cleanup old backups (keep last 5)
echo "🧹 Cleaning up old backups..."
ls -t "$BACKUP_DIR"/kalki_gpt_backup_*.tar.gz | tail -n +6 | xargs -r rm --
echo "✅ Cleanup completed"

# Optional: Upload to cloud storage
if [ -n "$BACKUP_UPLOAD_URL" ]; then
    echo "☁️ Uploading to cloud storage..."
    curl -X POST -F "file=@$BACKUP_PATH.tar.gz" "$BACKUP_UPLOAD_URL" || echo "⚠️ Cloud upload failed"
fi

echo "🎉 Backup process finished!"
