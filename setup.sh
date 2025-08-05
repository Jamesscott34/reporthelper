#!/bin/bash

# Enhanced Setup script for AI Report Writer
# This script automatically handles initial setup and updates

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Version tracking
CURRENT_VERSION="1.0.0"
VERSION_FILE=".version"

echo -e "${BLUE}🚀 AI Report Writer Setup & Update Script${NC}"
echo -e "${BLUE}==========================================${NC}"

# Function to check if this is an update
check_for_updates() {
    if [ -f "$VERSION_FILE" ]; then
        STORED_VERSION=$(cat "$VERSION_FILE")
        if [ "$STORED_VERSION" != "$CURRENT_VERSION" ]; then
            echo -e "${YELLOW}📦 Update detected: $STORED_VERSION → $CURRENT_VERSION${NC}"
            return 0
        else
            echo -e "${GREEN}✅ Already up to date (v$CURRENT_VERSION)${NC}"
            return 1
        fi
    else
        echo -e "${BLUE}🆕 First time setup${NC}"
        return 0
    fi
}

# Function to create virtual environment
setup_venv() {
    echo -e "${BLUE}📦 Setting up virtual environment...${NC}"
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}✅ Virtual environment created${NC}"
    else
        echo -e "${GREEN}✅ Virtual environment already exists${NC}"
    fi
}

# Function to install/update dependencies
install_dependencies() {
    echo -e "${BLUE}📦 Installing/updating dependencies...${NC}"
    source venv/bin/activate
    
    # Install core dependencies
    pip install --upgrade pip
    pip install django python-docx PyPDF2 requests python-dotenv
    
    # Install additional dependencies if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    echo -e "${GREEN}✅ Dependencies installed/updated${NC}"
}

# Function to run database migrations
run_migrations() {
    echo -e "${BLUE}🗄️ Running database migrations...${NC}"
    source venv/bin/activate
    
    # Make migrations for all apps
    python manage.py makemigrations --noinput || true
    
    # Apply migrations
    python manage.py migrate --noinput
    
    echo -e "${GREEN}✅ Database migrations completed${NC}"
}

# Function to create superuser
create_superuser() {
    echo -e "${BLUE}👤 Setting up superuser...${NC}"
    source venv/bin/activate
    
    # Create superuser if it doesn't exist
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell
    
    echo -e "${GREEN}✅ Superuser created: admin/admin123${NC}"
}

# Function to collect static files
collect_static() {
    echo -e "${BLUE}📁 Collecting static files...${NC}"
    source venv/bin/activate
    python manage.py collectstatic --noinput || true
    echo -e "${GREEN}✅ Static files collected${NC}"
}

# Function to check LM Studio setup
check_lm_studio() {
    echo -e "${BLUE}🤖 Checking LM Studio setup...${NC}"
    
    # Check if LM Studio AppImage exists
    if [ -f "Studio/LM-Studio-0.3.20-4-x64.AppImage" ]; then
        echo -e "${GREEN}✅ LM Studio AppImage found${NC}"
        chmod +x Studio/LM-Studio-0.3.20-4-x64.AppImage
    else
        echo -e "${YELLOW}⚠️  LM Studio AppImage not found in Studio/ directory${NC}"
        echo -e "${YELLOW}   Please download LM Studio and place it in the Studio/ directory${NC}"
    fi
}

# Function to make scripts executable
make_scripts_executable() {
    echo -e "${BLUE}🔧 Making scripts executable...${NC}"
    chmod +x scripts/*.sh 2>/dev/null || true
    chmod +x setup.sh
    echo -e "${GREEN}✅ Scripts made executable${NC}"
}

# Function to create necessary directories
create_directories() {
    echo -e "${BLUE}📁 Creating necessary directories...${NC}"
    mkdir -p media/documents
    mkdir -p staticfiles
    mkdir -p assets
    mkdir -p java_assets
    mkdir -p prompts
    echo -e "${GREEN}✅ Directories created${NC}"
}

# Function to check system requirements
check_system_requirements() {
    echo -e "${BLUE}🔍 Checking system requirements...${NC}"
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"
    
    # Check if curl is available (for API testing)
    if command -v curl &> /dev/null; then
        echo -e "${GREEN}✅ curl available${NC}"
    else
        echo -e "${YELLOW}⚠️  curl not found (needed for API testing)${NC}"
    fi
    
    # Check if git is available
    if command -v git &> /dev/null; then
        echo -e "${GREEN}✅ git available${NC}"
    else
        echo -e "${YELLOW}⚠️  git not found${NC}"
    fi
}

# Function to run health checks
run_health_checks() {
    echo -e "${BLUE}🏥 Running health checks...${NC}"
    source venv/bin/activate
    
    # Test Django configuration
    python manage.py check --deploy || echo -e "${YELLOW}⚠️  Django check warnings (normal for development)${NC}"
    
    # Test database connection
    python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('✅ Database connection OK')" 2>/dev/null || echo -e "${RED}❌ Database connection failed${NC}"
    
    echo -e "${GREEN}✅ Health checks completed${NC}"
}

# Function to display setup completion
display_completion() {
    echo -e "${GREEN}"
    echo "🎉 Setup completed successfully!"
    echo "================================"
    echo ""
    echo "🚀 Automatic Startup:"
    echo "✅ LM Studio: Started automatically (if available)"
    echo "✅ Django Server: Started automatically"
    echo "✅ Updates: Applied automatically"
    echo ""
    echo "🌐 Access Points:"
    echo "• Web Interface: http://127.0.0.1:8000"
    echo "• Admin Panel: http://127.0.0.1:8000/admin (admin/admin123)"
    echo "• LM Studio API: http://192.168.0.34:1234"
    echo ""
    echo "🔧 Useful Commands:"
    echo "- Check status: ./scripts/check_status.sh"
    echo "- Backup data: ./scripts/backup.sh"
    echo "- Test LM Studio: ./scripts/test_lmstudio.sh"
    echo "- Manual restart: ./setup.sh"
    echo ""
    echo "📚 Documentation: README.md"
    echo "🐛 Troubleshooting: Check README.md#troubleshooting"
    echo -e "${NC}"
}

# Function to save version
save_version() {
    echo "$CURRENT_VERSION" > "$VERSION_FILE"
    echo -e "${GREEN}✅ Version $CURRENT_VERSION saved${NC}"
}

# Function to start LM Studio if not running
start_lm_studio() {
    echo -e "${BLUE}🤖 Starting LM Studio...${NC}"
    
    # Check if LM Studio is already running
    if pgrep -f "LM-Studio" > /dev/null; then
        echo -e "${GREEN}✅ LM Studio is already running${NC}"
    else
        echo -e "${BLUE}🔄 Starting LM Studio...${NC}"
        
        # Check if AppImage exists
        STUDIO_DIR="$(dirname "$0")/Studio"
        APPIMAGE_PATH="$STUDIO_DIR/LM-Studio-0.3.20-4-x64.AppImage"
        
        if [ -f "$APPIMAGE_PATH" ]; then
            # Make AppImage executable if needed
            if [ ! -x "$APPIMAGE_PATH" ]; then
                chmod +x "$APPIMAGE_PATH"
            fi
            
            # Start LM Studio in the background
            echo -e "${BLUE}🎯 Launching LM Studio...${NC}"
            nohup "$APPIMAGE_PATH" > /dev/null 2>&1 &
            
            # Wait for LM Studio to start
            echo -e "${BLUE}⏳ Waiting for LM Studio to start...${NC}"
            sleep 15
            
            # Check if LM Studio started successfully
            if pgrep -f "LM-Studio" > /dev/null; then
                echo -e "${GREEN}✅ LM Studio started successfully${NC}"
            else
                echo -e "${YELLOW}⚠️  LM Studio may not have started automatically${NC}"
                echo -e "${YELLOW}   Please start it manually: ./scripts/start_llmstudio.sh${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  LM Studio AppImage not found at: $APPIMAGE_PATH${NC}"
            echo -e "${YELLOW}   Please download LM Studio and place it in the Studio/ directory${NC}"
        fi
    fi
    
    # Check API endpoint
    echo -e "${BLUE}🔍 Checking LM Studio API endpoint...${NC}"
    if curl -s http://192.168.0.34:1234/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✅ LM Studio API is responding at http://192.168.0.34:1234${NC}"
    else
        echo -e "${YELLOW}⚠️  LM Studio API not responding yet${NC}"
        echo -e "${YELLOW}   Please ensure LM Studio is running and local server is started${NC}"
    fi
}

# Function to start Django server
start_django() {
    echo -e "${BLUE}🌐 Starting Django server...${NC}"
    
    # Check if Django is already running
    if pgrep -f "manage.py runserver" > /dev/null; then
        echo -e "${GREEN}✅ Django server is already running${NC}"
    else
        echo -e "${BLUE}🔄 Starting Django server...${NC}"
        
        # Activate virtual environment and start Django
        source venv/bin/activate
        
        # Start Django in the background
        nohup python manage.py runserver 127.0.0.1:8000 > /dev/null 2>&1 &
        
        # Wait for Django to start
        echo -e "${BLUE}⏳ Waiting for Django to start...${NC}"
        sleep 5
        
        # Check if Django started successfully
        if pgrep -f "manage.py runserver" > /dev/null; then
            echo -e "${GREEN}✅ Django server started successfully${NC}"
            echo -e "${GREEN}🌐 Django is running at: http://127.0.0.1:8000${NC}"
        else
            echo -e "${YELLOW}⚠️  Django server may not have started automatically${NC}"
            echo -e "${YELLOW}   Please start it manually: ./scripts/start_django.sh${NC}"
        fi
    fi
}

# Function to apply updates
apply_updates() {
    echo -e "${BLUE}🔄 Applying updates...${NC}"
    
    # Check if this is an update
    if [ -f "$VERSION_FILE" ]; then
        STORED_VERSION=$(cat "$VERSION_FILE")
        if [ "$STORED_VERSION" != "$CURRENT_VERSION" ]; then
            echo -e "${YELLOW}📦 Applying updates from v$STORED_VERSION to v$CURRENT_VERSION${NC}"
            
            # Run update-specific tasks
            echo -e "${BLUE}📦 Updating dependencies...${NC}"
            source venv/bin/activate
            pip install --upgrade -r requirements.txt
            
            echo -e "${BLUE}🗄️ Running migrations...${NC}"
            python manage.py makemigrations --noinput || true
            python manage.py migrate --noinput
            
            echo -e "${BLUE}📁 Collecting static files...${NC}"
            python manage.py collectstatic --noinput || true
            
            echo -e "${GREEN}✅ Updates applied successfully${NC}"
        else
            echo -e "${GREEN}✅ No updates needed${NC}"
        fi
    else
        echo -e "${BLUE}🆕 First time setup - no updates to apply${NC}"
    fi
}

# Main execution
main() {
    echo -e "${BLUE}Starting AI Report Writer setup...${NC}"
    
    # Check for updates
    NEEDS_UPDATE=$(check_for_updates)
    
    # System requirements
    check_system_requirements
    
    # Create directories
    create_directories
    
    # Setup virtual environment
    setup_venv
    
    # Install dependencies
    install_dependencies
    
    # Make scripts executable
    make_scripts_executable
    
    # Run migrations
    run_migrations
    
    # Create superuser
    create_superuser
    
    # Collect static files
    collect_static
    
    # Check LM Studio setup
    check_lm_studio
    
    # Apply updates if needed
    apply_updates
    
    # Run health checks
    run_health_checks
    
    # Save version
    save_version
    
    # Start LM Studio if not running
    start_lm_studio
    
    # Start Django server
    start_django
    
    # Display completion
    display_completion
}

# Run main function
main "$@" 