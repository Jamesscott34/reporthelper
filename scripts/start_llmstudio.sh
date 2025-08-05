#!/bin/bash

# Script to start LM Studio from AppImage
# This script will start LM Studio if it's not already running

echo "🚀 Starting LM Studio for AI Report Writer..."

# Check if LM Studio is already running
if pgrep -f "LM-Studio" > /dev/null; then
    echo "✅ LM Studio is already running"
else
    echo "🔄 Starting LM Studio..."
    
    # Check if AppImage exists
    STUDIO_DIR="$(dirname "$0")/../Studio"
    APPIMAGE_PATH="$STUDIO_DIR/LM-Studio-0.3.20-4-x64.AppImage"
    
    if [ ! -f "$APPIMAGE_PATH" ]; then
        echo "❌ LM Studio AppImage not found at: $APPIMAGE_PATH"
        echo "Please make sure the AppImage is in the Studio directory"
        exit 1
    fi
    
    # Make AppImage executable if needed
    if [ ! -x "$APPIMAGE_PATH" ]; then
        echo "🔧 Making AppImage executable..."
        chmod +x "$APPIMAGE_PATH"
    fi
    
    # Start LM Studio in the background
    echo "🎯 Launching LM Studio..."
    nohup "$APPIMAGE_PATH" > /dev/null 2>&1 &
    
    # Wait a moment for LM Studio to start
    echo "⏳ Waiting for LM Studio to start..."
    sleep 10
    
    # Check if LM Studio started successfully
    if pgrep -f "LM-Studio" > /dev/null; then
        echo "✅ LM Studio started successfully"
        echo "📍 LM Studio should be available in your desktop environment"
    else
        echo "❌ Failed to start LM Studio"
        echo "Please check if the AppImage is compatible with your system"
        exit 1
    fi
fi

# Check if the API endpoint is available
echo "🔍 Checking LM Studio API endpoint..."
if curl -s http://192.168.0.34:1234/api/tags > /dev/null 2>&1; then
    echo "✅ LM Studio API is responding at http://192.168.0.34:1234"
else
    echo "⚠️  LM Studio API not responding yet. Please:"
    echo "   1. Open LM Studio manually"
    echo "   2. Load one of your models"
    echo "   3. Start the local server in LM Studio"
    echo "   4. Make sure it's running on http://192.168.0.34:1234"
fi

echo ""
echo "🎯 LM Studio is ready for AI Report Writer!"
echo "💡 Make sure to load your models in LM Studio:"
echo "   - deepseek-r1-distill-qwen-7b"
echo "   - whiterabbitneo-2.5-qwen-2.5-coder-7b"
echo "   - llama-3-8b-gpt-40-ru1.0"
echo "   - h2o-danube2-1.8b-chat"
echo ""
echo "🔗 API endpoint: http://192.168.0.34:1234"
