#!/bin/bash

# Backup script for AI Report Writer
# This script creates backups of important data and configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Backup directory
BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="ai_report_writer_backup_$TIMESTAMP"

echo -e "${BLUE}💾 AI Report Writer Backup Script${NC}"
echo -e "${BLUE}===============================${NC}"

# Function to create backup directory
create_backup_dir() {
    echo -e "${BLUE}📁 Creating backup directory...${NC}"
    mkdir -p "$BACKUP_DIR"
    echo -e "${GREEN}✅ Backup directory created${NC}"
}

# Function to backup database
backup_database() {
    echo -e "${BLUE}🗄️ Backing up database...${NC}"
    if [ -f "db.sqlite3" ]; then
        cp db.sqlite3 "$BACKUP_DIR/db_backup_$TIMESTAMP.sqlite3"
        echo -e "${GREEN}✅ Database backed up${NC}"
    else
        echo -e "${YELLOW}⚠️  No database file found${NC}"
    fi
}

# Function to backup uploaded documents
backup_documents() {
    echo -e "${BLUE}📄 Backing up uploaded documents...${NC}"
    if [ -d "media" ]; then
        tar -czf "$BACKUP_DIR/documents_backup_$TIMESTAMP.tar.gz" media/ 2>/dev/null || true
        echo -e "${GREEN}✅ Documents backed up${NC}"
    else
        echo -e "${YELLOW}⚠️  No media directory found${NC}"
    fi
}

# Function to backup configuration
backup_config() {
    echo -e "${BLUE}⚙️ Backing up configuration...${NC}"
    
    # Create config backup directory
    mkdir -p "$BACKUP_DIR/config_$TIMESTAMP"
    
    # Backup important files
    if [ -f ".env" ]; then
        cp .env "$BACKUP_DIR/config_$TIMESTAMP/"
    fi
    
    if [ -f ".version" ]; then
        cp .version "$BACKUP_DIR/config_$TIMESTAMP/"
    fi
    
    if [ -f "requirements.txt" ]; then
        cp requirements.txt "$BACKUP_DIR/config_$TIMESTAMP/"
    fi
    
    # Backup Django settings (without sensitive data)
    if [ -f "ai_report_writer/settings.py" ]; then
        cp ai_report_writer/settings.py "$BACKUP_DIR/config_$TIMESTAMP/"
    fi
    
    echo -e "${GREEN}✅ Configuration backed up${NC}"
}

# Function to backup custom code
backup_code() {
    echo -e "${BLUE}💻 Backing up custom code...${NC}"
    
    # Create code backup directory
    mkdir -p "$BACKUP_DIR/code_$TIMESTAMP"
    
    # Backup custom apps
    for app in breakdown user_review breakdown_review creation; do
        if [ -d "$app" ]; then
            cp -r "$app" "$BACKUP_DIR/code_$TIMESTAMP/"
        fi
    done
    
    # Backup templates
    if [ -d "templates" ]; then
        cp -r templates "$BACKUP_DIR/code_$TIMESTAMP/"
    fi
    
    # Backup static files
    if [ -d "static" ]; then
        cp -r static "$BACKUP_DIR/code_$TIMESTAMP/"
    fi
    
    echo -e "${GREEN}✅ Custom code backed up${NC}"
}

# Function to create full backup archive
create_full_backup() {
    echo -e "${BLUE}📦 Creating full backup archive...${NC}"
    
    # Create full backup
    tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        --exclude='backups' \
        . 2>/dev/null || true
    
    echo -e "${GREEN}✅ Full backup created: $BACKUP_NAME.tar.gz${NC}"
}

# Function to cleanup old backups
cleanup_old_backups() {
    echo -e "${BLUE}🧹 Cleaning up old backups...${NC}"
    
    # Keep only last 5 backups
    ls -t "$BACKUP_DIR"/*.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm
    
    echo -e "${GREEN}✅ Old backups cleaned up${NC}"
}

# Function to display backup summary
display_backup_summary() {
    echo -e "${BLUE}"
    echo "📊 Backup Summary"
    echo "================="
    echo -e "${NC}"
    
    echo -e "${GREEN}✅ Backup completed successfully!${NC}"
    echo ""
    echo "📁 Backup location: $BACKUP_DIR/"
    echo "📦 Full backup: $BACKUP_NAME.tar.gz"
    echo ""
    echo "🔧 To restore from backup:"
    echo "1. Extract: tar -xzf $BACKUP_DIR/$BACKUP_NAME.tar.gz"
    echo "2. Run setup: ./setup.sh"
    echo ""
    echo "💡 Backup includes:"
    echo "- Database (SQLite)"
    echo "- Uploaded documents"
    echo "- Configuration files"
    echo "- Custom code and templates"
    echo -e "${NC}"
}

# Function to check available space
check_disk_space() {
    echo -e "${BLUE}💾 Checking available disk space...${NC}"
    
    # Get available space in MB
    AVAILABLE_SPACE=$(df . | awk 'NR==2 {print $4}')
    AVAILABLE_SPACE_MB=$((AVAILABLE_SPACE / 1024))
    
    if [ $AVAILABLE_SPACE_MB -gt 1000 ]; then
        echo -e "${GREEN}✅ Sufficient disk space available (${AVAILABLE_SPACE_MB}MB)${NC}"
    else
        echo -e "${YELLOW}⚠️  Low disk space (${AVAILABLE_SPACE_MB}MB)${NC}"
    fi
}

# Main execution
main() {
    echo -e "${BLUE}Starting backup process...${NC}"
    
    # Check disk space
    check_disk_space
    
    # Create backup directory
    create_backup_dir
    
    # Perform backups
    backup_database
    backup_documents
    backup_config
    backup_code
    
    # Create full backup
    create_full_backup
    
    # Cleanup old backups
    cleanup_old_backups
    
    # Display summary
    display_backup_summary
}

# Run main function
main "$@" 