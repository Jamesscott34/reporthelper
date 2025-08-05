#!/bin/bash

# Status check script for AI Report Writer
# This script checks the health of all components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 AI Report Writer Status Check${NC}"
echo -e "${BLUE}==============================${NC}"

# Function to check if virtual environment exists
check_venv() {
    echo -e "${BLUE}📦 Checking virtual environment...${NC}"
    if [ -d "venv" ]; then
        echo -e "${GREEN}✅ Virtual environment exists${NC}"
        return 0
    else
        echo -e "${RED}❌ Virtual environment not found${NC}"
        return 1
    fi
}

# Function to check Django installation
check_django() {
    echo -e "${BLUE}🐍 Checking Django installation...${NC}"
    if [ -d "venv" ]; then
        source venv/bin/activate
        if python -c "import django; print('✅ Django', django.get_version())" 2>/dev/null; then
            return 0
        else
            echo -e "${RED}❌ Django not installed${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  Cannot check Django (no venv)${NC}"
        return 1
    fi
}

# Function to check database
check_database() {
    echo -e "${BLUE}🗄️ Checking database...${NC}"
    if [ -d "venv" ]; then
        source venv/bin/activate
        if python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('✅ Database connection OK')" 2>/dev/null; then
            return 0
        else
            echo -e "${RED}❌ Database connection failed${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  Cannot check database (no venv)${NC}"
        return 1
    fi
}

# Function to check LM Studio
check_lm_studio() {
    echo -e "${BLUE}🤖 Checking LM Studio...${NC}"
    
    # Check if AppImage exists
    if [ -f "Studio/LM-Studio-0.3.20-4-x64.AppImage" ]; then
        echo -e "${GREEN}✅ LM Studio AppImage found${NC}"
    else
        echo -e "${YELLOW}⚠️  LM Studio AppImage not found${NC}"
    fi
    
    # Check if LM Studio is running
    if pgrep -f "LM-Studio" > /dev/null; then
        echo -e "${GREEN}✅ LM Studio is running${NC}"
    else
        echo -e "${YELLOW}⚠️  LM Studio is not running${NC}"
    fi
    
    # Check LM Studio API
    if curl -s http://192.168.0.34:1234/v1/models > /dev/null 2>&1; then
        echo -e "${GREEN}✅ LM Studio API: Responding${NC}"
    else
        echo -e "${RED}❌ LM Studio API: Not responding${NC}"
    fi
}

# Function to check Django server
check_django_server() {
    echo -e "${BLUE}🌐 Checking Django server...${NC}"
    if pgrep -f "manage.py runserver" > /dev/null; then
        echo -e "${GREEN}✅ Django server is running${NC}"
        if curl -s http://127.0.0.1:8000 > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Django server responding${NC}"
        else
            echo -e "${YELLOW}⚠️  Django server not responding on port 8000${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Django server is not running${NC}"
    fi
}

# Function to check file permissions
check_permissions() {
    echo -e "${BLUE}🔐 Checking file permissions...${NC}"
    
    # Check if scripts are executable
    if [ -x "scripts/start_django.sh" ] && [ -x "scripts/start_llmstudio.sh" ]; then
        echo -e "${GREEN}✅ Scripts are executable${NC}"
    else
        echo -e "${YELLOW}⚠️  Some scripts are not executable${NC}"
    fi
    
    # Check if media directory is writable
    if [ -w "media" ]; then
        echo -e "${GREEN}✅ Media directory is writable${NC}"
    else
        echo -e "${YELLOW}⚠️  Media directory is not writable${NC}"
    fi
}

# Function to check dependencies
check_dependencies() {
    echo -e "${BLUE}📦 Checking dependencies...${NC}"
    if [ -d "venv" ]; then
        source venv/bin/activate
        
        # Check core dependencies
        for dep in django python-docx PyPDF2 requests python-dotenv; do
            if python -c "import $dep" 2>/dev/null; then
                echo -e "${GREEN}✅ $dep installed${NC}"
            else
                echo -e "${RED}❌ $dep not installed${NC}"
            fi
        done
    else
        echo -e "${YELLOW}⚠️  Cannot check dependencies (no venv)${NC}"
    fi
}

# Function to display summary
display_summary() {
    echo -e "${BLUE}"
    echo "📊 Status Summary"
    echo "================="
    echo -e "${NC}"
    
    # Count checks
    TOTAL_CHECKS=0
    PASSED_CHECKS=0
    
    # Run all checks and count results
    check_venv && ((PASSED_CHECKS++)) || true; ((TOTAL_CHECKS++))
    check_django && ((PASSED_CHECKS++)) || true; ((TOTAL_CHECKS++))
    check_database && ((PASSED_CHECKS++)) || true; ((TOTAL_CHECKS++))
    check_lm_studio
    check_django_server
    check_permissions
    check_dependencies
    
    echo -e "${BLUE}"
    echo "📈 Results: $PASSED_CHECKS/$TOTAL_CHECKS core checks passed"
    
    if [ $PASSED_CHECKS -eq $TOTAL_CHECKS ]; then
        echo -e "${GREEN}🎉 All core systems are healthy!${NC}"
    else
        echo -e "${YELLOW}⚠️  Some issues detected. Run ./setup.sh to fix.${NC}"
    fi
    
    echo -e "${NC}"
}

# Main execution
main() {
    display_summary
}

# Run main function
main "$@" 