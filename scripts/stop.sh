
#!/bin/bash

# Stop Kalki GPT Script

echo "🛑 Stopping Kalki GPT..."

# Check if PID file exists
if [ -f "app.pid" ]; then
    PID=$(cat app.pid)
    
    if kill -0 $PID 2>/dev/null; then
        echo "🔄 Stopping process $PID..."
        kill $PID
        
        # Wait for graceful shutdown
        for i in {1..10}; do
            if ! kill -0 $PID 2>/dev/null; then
                echo "✅ Process stopped gracefully"
                rm -f app.pid
                exit 0
            fi
            sleep 1
        done
        
        # Force kill if necessary
        echo "⚠️ Forcing process termination..."
        kill -9 $PID 2>/dev/null || true
        rm -f app.pid
        echo "🛑 Process terminated"
    else
        echo "⚠️ Process not running, cleaning up PID file"
        rm -f app.pid
    fi
else
    # Try to find and kill streamlit processes
    PIDS=$(pgrep -f "streamlit run app.py")
    if [ -n "$PIDS" ]; then
        echo "🔍 Found Streamlit processes: $PIDS"
        kill $PIDS
        echo "🛑 Streamlit processes stopped"
    else
        echo "ℹ️ No running Kalki GPT processes found"
    fi
fi

echo "✅ Kalki GPT stopped"
