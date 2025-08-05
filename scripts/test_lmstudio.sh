#!/bin/bash

# Test script for LM Studio connection
# This script tests the connection to LM Studio API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# LM Studio endpoint
LM_STUDIO_ENDPOINT="http://192.168.0.34:1234"

echo -e "${BLUE}🧪 Testing LM Studio Connection${NC}"
echo -e "${BLUE}=============================${NC}"

# Function to test API endpoint
test_api_endpoint() {
    echo -e "${BLUE}🔍 Testing API endpoint: $LM_STUDIO_ENDPOINT${NC}"
    
    if command -v curl &> /dev/null; then
        # Test basic connectivity using the correct models endpoint
        if curl -s --connect-timeout 5 "$LM_STUDIO_ENDPOINT/v1/models" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ API endpoint is responding${NC}"
            
            # Get available models
            echo -e "${BLUE}📋 Available models:${NC}"
            curl -s "$LM_STUDIO_ENDPOINT/v1/models" | python3 -m json.tool 2>/dev/null || echo "Raw response: $(curl -s "$LM_STUDIO_ENDPOINT/v1/models")"
            
            return 0
        else
            echo -e "${RED}❌ API endpoint is not responding${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  curl not available, cannot test endpoint${NC}"
        return 1
    fi
}

# Function to test model generation
test_model_generation() {
    echo -e "${BLUE}🤖 Testing model generation...${NC}"
    
    # Test with a simple prompt using chat completions
    TEST_PROMPT="Hello, this is a test. Please respond with 'Test successful' if you can see this message."
    
    if command -v curl &> /dev/null; then
        # Create a test request using OpenAI-compatible format
        TEST_REQUEST=$(cat <<EOF
{
    "model": "deepseek-r1-distill-qwen-7b",
    "messages": [
        {
            "role": "user",
            "content": "$TEST_PROMPT"
        }
    ],
    "stream": false,
    "temperature": 0.7,
    "max_tokens": 50
}
EOF
)
        
        # Send test request to chat completions endpoint
        RESPONSE=$(curl -s -X POST "$LM_STUDIO_ENDPOINT/v1/chat/completions" \
            -H "Content-Type: application/json" \
            -d "$TEST_REQUEST" 2>/dev/null || echo "{}")
        
        if echo "$RESPONSE" | grep -q "choices"; then
            echo -e "${GREEN}✅ Model generation test successful${NC}"
            echo -e "${BLUE}📝 Response preview:${NC}"
            echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('choices', [{}])[0].get('message', {}).get('content', 'No response')[:100] + '...')" 2>/dev/null || echo "Response received"
        else
            echo -e "${YELLOW}⚠️  Model generation test failed or no response${NC}"
            echo -e "${BLUE}📝 Raw response:${NC}"
            echo "$RESPONSE"
        fi
    else
        echo -e "${YELLOW}⚠️  curl not available, cannot test model generation${NC}"
    fi
}

# Function to check network connectivity
check_network() {
    echo -e "${BLUE}🌐 Checking network connectivity...${NC}"
    
    # Extract IP and port
    IP=$(echo "$LM_STUDIO_ENDPOINT" | sed 's|http://||' | cut -d: -f1)
    PORT=$(echo "$LM_STUDIO_ENDPOINT" | sed 's|http://||' | cut -d: -f2)
    
    # Test basic connectivity
    if ping -c 1 "$IP" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Network connectivity to $IP OK${NC}"
    else
        echo -e "${RED}❌ Cannot reach $IP${NC}"
    fi
    
    # Test port connectivity
    if command -v nc &> /dev/null; then
        if nc -z "$IP" "$PORT" 2>/dev/null; then
            echo -e "${GREEN}✅ Port $PORT is open on $IP${NC}"
        else
            echo -e "${RED}❌ Port $PORT is not accessible on $IP${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  netcat not available, cannot test port${NC}"
    fi
}

# Function to display summary
display_summary() {
    echo -e "${BLUE}📊 Test Summary${NC}"
    echo -e "${BLUE}==============${NC}"
    
    # Check if LM Studio is running
    if pgrep -f "LM-Studio" > /dev/null; then
        echo -e "${GREEN}✅ LM Studio process is running${NC}"
    else
        echo -e "${RED}❌ LM Studio process is not running${NC}"
    fi
    
    # Check API connectivity
    if curl -s "$LM_STUDIO_ENDPOINT/v1/models" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ LM Studio API is accessible${NC}"
    else
        echo -e "${RED}❌ LM Studio API is not accessible${NC}"
    fi
}

# Main execution
main() {
    check_network
    echo ""
    test_api_endpoint
    echo ""
    test_model_generation
    echo ""
    display_summary
}

# Run main function
main 