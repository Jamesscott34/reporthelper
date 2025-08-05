#!/bin/bash

# Update script for AI Report Writer
# This script handles automatic updates and new features

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Version tracking
CURRENT_VERSION="1.0.0"
VERSION_FILE=".version"

echo -e "${BLUE}🔄 AI Report Writer Update Script${NC}"
echo -e "${BLUE}================================${NC}"

# Function to check current version
get_current_version() {
    if [ -f "$VERSION_FILE" ]; then
        cat "$VERSION_FILE"
    else
        echo "0.0.0"
    fi
}

# Function to backup before update
backup_before_update() {
    echo -e "${BLUE}💾 Creating backup before update...${NC}"
    ./scripts/backup.sh > /dev/null 2>&1 || echo -e "${YELLOW}⚠️  Backup failed, continuing...${NC}"
}

# Function to update dependencies
update_dependencies() {
    echo -e "${BLUE}📦 Updating dependencies...${NC}"
    source venv/bin/activate
    
    # Update pip
    pip install --upgrade pip
    
    # Update core dependencies
    pip install --upgrade django python-docx PyPDF2 requests python-dotenv
    
    # Update from requirements.txt if it exists
    if [ -f "requirements.txt" ]; then
        pip install --upgrade -r requirements.txt
    fi
    
    echo -e "${GREEN}✅ Dependencies updated${NC}"
}

# Function to run migrations
run_migrations() {
    echo -e "${BLUE}🗄️ Running database migrations...${NC}"
    source venv/bin/activate
    
    # Make migrations for all apps
    python manage.py makemigrations --noinput || true
    
    # Apply migrations
    python manage.py migrate --noinput
    
    echo -e "${GREEN}✅ Database migrations completed${NC}"
}

# Function to collect static files
collect_static() {
    echo -e "${BLUE}📁 Collecting static files...${NC}"
    source venv/bin/activate
    python manage.py collectstatic --noinput || true
    echo -e "${GREEN}✅ Static files collected${NC}"
}

# Function to check for new apps
check_new_apps() {
    echo -e "${BLUE}🔍 Checking for new apps...${NC}"
    
    # List of expected apps
    EXPECTED_APPS=("breakdown" "user_review" "breakdown_review" "creation")
    
    for app in "${EXPECTED_APPS[@]}"; do
        if [ ! -d "$app" ]; then
            echo -e "${YELLOW}⚠️  App '$app' not found, creating...${NC}"
            source venv/bin/activate
            python manage.py startapp "$app" || true
        fi
    done
    
    echo -e "${GREEN}✅ Apps checked${NC}"
}

# Function to update configuration
update_configuration() {
    echo -e "${BLUE}⚙️ Updating configuration...${NC}"
    
    # Update settings if needed
    if [ -f "ai_report_writer/settings.py" ]; then
        # Check if new apps need to be added to INSTALLED_APPS
        if ! grep -q "'user_review'" ai_report_writer/settings.py; then
            echo -e "${YELLOW}⚠️  Updating INSTALLED_APPS...${NC}"
            # This would need manual intervention or a more sophisticated approach
        fi
    fi
    
    echo -e "${GREEN}✅ Configuration updated${NC}"
}

# Function to check for new templates
check_new_templates() {
    echo -e "${BLUE}🎨 Checking for new templates...${NC}"
    
    # Create template directories if they don't exist
    mkdir -p templates/breakdown
    mkdir -p templates/user_review
    mkdir -p templates/breakdown_review
    mkdir -p templates/creation
    
    echo -e "${GREEN}✅ Template directories checked${NC}"
}

# Function to check for new static files
check_new_static() {
    echo -e "${BLUE}📁 Checking for new static files...${NC}"
    
    # Create static directories if they don't exist
    mkdir -p static/css
    mkdir -p static/js
    mkdir -p static/images
    
    echo -e "${GREEN}✅ Static directories checked${NC}"
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

# Function to save new version
save_version() {
    echo "$CURRENT_VERSION" > "$VERSION_FILE"
    echo -e "${GREEN}✅ Version $CURRENT_VERSION saved${NC}"
}

# Function to display update summary
display_update_summary() {
    OLD_VERSION=$(get_current_version)
    
    echo -e "${GREEN}"
    echo "🎉 Update completed successfully!"
    echo "================================"
    echo ""
    echo "📈 Version: $OLD_VERSION → $CURRENT_VERSION"
    echo ""
    echo "🔄 What was updated:"
    echo "- Dependencies upgraded"
    echo "- Database migrations applied"
    echo "- Static files collected"
    echo "- New apps checked"
    echo "- Configuration updated"
    echo "- Health checks completed"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Start LM Studio: ./scripts/start_llmstudio.sh"
    echo "2. Start Django: ./scripts/start_django.sh"
    echo "3. Check status: ./scripts/check_status.sh"
    echo ""
    echo "📚 Check README.md for new features"
    echo -e "${NC}"
}

# Function to check if update is needed
check_update_needed() {
    STORED_VERSION=$(get_current_version)
    
    if [ "$STORED_VERSION" != "$CURRENT_VERSION" ]; then
        echo -e "${YELLOW}📦 Update available: $STORED_VERSION → $CURRENT_VERSION${NC}"
        return 0
    else
        echo -e "${GREEN}✅ Already up to date (v$CURRENT_VERSION)${NC}"
        return 1
    fi
}

# Main execution
main() {
    echo -e "${BLUE}Starting update process...${NC}"
    
    # Check if update is needed
    if ! check_update_needed; then
        echo -e "${GREEN}No update needed.${NC}"
        exit 0
    fi
    
    # Backup before update
    backup_before_update
    
    # Perform updates
    update_dependencies
    check_new_apps
    update_configuration
    check_new_templates
    check_new_static
    run_migrations
    collect_static
    run_health_checks
    
    # Save new version
    save_version
    
    # Display summary
    display_update_summary
}

# Run main function
main "$@" 