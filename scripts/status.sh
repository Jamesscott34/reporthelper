#!/bin/bash

# Comprehensive status script for AI Report Writer
# This script shows the status of all components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 AI Report Writer Status Dashboard${NC}"
echo -e "${BLUE}===================================${NC}"

# Function to check LM Studio status
check_lm_studio_status() {
    echo -e "${BLUE}🤖 LM Studio Status:${NC}"
    
    # Check if LM Studio process is running
    if pgrep -f "LM-Studio" > /dev/null; then
        echo -e "  ${GREEN}✅ Process: Running${NC}"
    else
        echo -e "  ${RED}❌ Process: Not running${NC}"
    fi
    
    # Check API endpoint
    if curl -s http://192.168.0.34:1234/api/tags > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ API: Responding at http://192.168.0.34:1234${NC}"
    else
        echo -e "  ${RED}❌ API: Not responding${NC}"
    fi
}

# Function to check Django status
check_django_status() {
    echo -e "${BLUE}🌐 Django Status:${NC}"
    
    # Check if Django process is running
    if pgrep -f "manage.py runserver" > /dev/null; then
        echo -e "  ${GREEN}✅ Process: Running${NC}"
        
        # Check if Django is responding
        if curl -s http://127.0.0.1:8000 > /dev/null 2>&1; then
            echo -e "  ${GREEN}✅ Web Interface: Responding at http://127.0.0.1:8000${NC}"
        else
            echo -e "  ${YELLOW}⚠️  Web Interface: Not responding${NC}"
        fi
    else
        echo -e "  ${RED}❌ Process: Not running${NC}"
    fi
}

# Function to check database status
check_database_status() {
    echo -e "${BLUE}🗄️ Database Status:${NC}"
    
    if [ -f "db.sqlite3" ]; then
        echo -e "  ${GREEN}✅ Database file: Exists${NC}"
        
        # Check database connection
        if [ -d "venv" ]; then
            source venv/bin/activate
            if python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('OK')" 2>/dev/null | grep -q "OK"; then
                echo -e "  ${GREEN}✅ Connection: OK${NC}"
            else
                echo -e "  ${RED}❌ Connection: Failed${NC}"
            fi
        else
            echo -e "  ${YELLOW}⚠️  Virtual environment not found${NC}"
        fi
    else
        echo -e "  ${RED}❌ Database file: Not found${NC}"
    fi
}

# Function to check virtual environment
check_venv_status() {
    echo -e "${BLUE}📦 Virtual Environment Status:${NC}"
    
    if [ -d "venv" ]; then
        echo -e "  ${GREEN}✅ Virtual environment: Exists${NC}"
        
        # Check if activated
        if [ -n "$VIRTUAL_ENV" ]; then
            echo -e "  ${GREEN}✅ Status: Activated${NC}"
        else
            echo -e "  ${YELLOW}⚠️  Status: Not activated${NC}"
        fi
    else
        echo -e "  ${RED}❌ Virtual environment: Not found${NC}"
    fi
}

# Function to check file permissions
check_permissions() {
    echo -e "${BLUE}🔐 File Permissions:${NC}"
    
    # Check if scripts are executable
    if [ -x "scripts/start_django.sh" ] && [ -x "scripts/start_llmstudio.sh" ]; then
        echo -e "  ${GREEN}✅ Scripts: Executable${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Scripts: Some not executable${NC}"
    fi
    
    # Check if media directory is writable
    if [ -w "media" ]; then
        echo -e "  ${GREEN}✅ Media directory: Writable${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Media directory: Not writable${NC}"
    fi
}

# Function to display summary
display_summary() {
    echo -e "${BLUE}"
    echo "📊 Summary"
    echo "=========="
    echo -e "${NC}"
    
    # Count running services
    RUNNING_SERVICES=0
    TOTAL_SERVICES=2
    
    if pgrep -f "LM-Studio" > /dev/null; then
        ((RUNNING_SERVICES++))
    fi
    
    if pgrep -f "manage.py runserver" > /dev/null; then
        ((RUNNING_SERVICES++))
    fi
    
    echo -e "Services running: ${GREEN}$RUNNING_SERVICES/$TOTAL_SERVICES${NC}"
    
    if [ $RUNNING_SERVICES -eq $TOTAL_SERVICES ]; then
        echo -e "${GREEN}🎉 All services are running!${NC}"
    elif [ $RUNNING_SERVICES -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Some services are running${NC}"
    else
        echo -e "${RED}❌ No services are running${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}Quick Actions:${NC}"
    echo "• Start all services: ./setup.sh"
    echo "• Test LM Studio: ./scripts/test_lmstudio.sh"
    echo "• Check detailed status: ./scripts/check_status.sh"
    echo -e "${NC}"
}

# Main execution
main() {
    check_venv_status
    echo ""
    check_database_status
    echo ""
    check_lm_studio_status
    echo ""
    check_django_status
    echo ""
    check_permissions
    echo ""
    display_summary
}

# Run main function
main "$@" 