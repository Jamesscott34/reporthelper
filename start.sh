#!/bin/bash

# AI Report Writer - Complete Startup & Setup Script
# Handles everything automatically with constant updates and comprehensive setup

set -e  # Exit on any error

echo "🚀 AI Report Writer - Complete Startup & Setup System"
echo "===================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Version tracking
CURRENT_VERSION="1.0.0"
VERSION_FILE=".version"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Python is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    print_success "Python 3 found: $(python3 --version)"
}

# Function to check system requirements
check_system_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    REQUIRED_VERSION="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
        print_success "Python version $PYTHON_VERSION is compatible"
    else
        print_error "Python version $PYTHON_VERSION is too old. Required: $REQUIRED_VERSION+"
        exit 1
    fi
    
    # Check for required system tools
    tools=("curl" "git" "libreoffice")
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            print_success "$tool: Available"
        else
            print_warning "$tool: Not found (may not be installed)"
        fi
    done
}

# Function to create virtual environment if needed
create_venv() {
    print_status "Checking virtual environment..."
    
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv || {
            print_error "Failed to create virtual environment"
            return 1
        }
        print_success "Virtual environment created"
    else
        print_success "Virtual environment found"
    fi
}

# Function to install dependencies if needed
install_dependencies() {
    print_status "Checking Python dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate || {
        print_error "Failed to activate virtual environment"
        return 1
    }
    
    # Check if key packages are installed
    if ! python -c "import django" 2>/dev/null; then
        print_status "Installing Python dependencies..."
        
        # Upgrade pip
        pip install --upgrade pip || echo -e "${YELLOW}⚠️  Failed to upgrade pip${NC}"
        
        # Install core dependencies first
        pip install django python-docx PyPDF2 requests python-dotenv || {
            print_error "Failed to install core dependencies"
            return 1
        }
        
        # Install requirements if file exists
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt || {
                print_warning "Some requirements failed to install"
            }
        fi
        
        print_success "Python dependencies installed"
    else
        print_success "Python dependencies already installed"
    fi
}

# Function to create .env file if needed
create_env_file() {
    print_status "Checking environment file..."
    
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        cat > .env << 'EOF'
# Django Configuration
DEBUG=True
SECRET_KEY=django-insecure-development-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# AI Configuration (LM Studio)
OLLAMA_HOST=http://192.168.0.34:1234
BREAKDOWN_MODEL=deepseek-r1-distill-qwen-7b
REVIEWER_MODEL=whiterabbitneo-2.5-qwen-2.5-coder-7b
FINALIZER_MODEL=llama-3-8b-gpt-40-ru1.0
REANALYZER_MODEL=h2o-danube2-1.8b-chat

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
EOF
        print_success ".env file created"
    else
        print_success ".env file already exists"
    fi
}

# Function to create directories if needed
create_directories() {
    print_status "Creating project directories..."
    
    mkdir -p logs
    mkdir -p media/documents
    mkdir -p staticfiles
    mkdir -p assets
    mkdir -p java_assets
    mkdir -p prompts
    mkdir -p backups
    mkdir -p Studio
    
    print_success "Project directories created"
}

# Function to activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Function to check Python packages
check_python_packages() {
    print_status "Checking Python packages..."
    
    # Test key packages
    packages=("django" "requests" "python-docx" "PyPDF2" "python-dotenv")
    
    for package in "${packages[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            print_success "$package: OK"
        else
            print_error "$package: Not installed"
            print_status "Please run: pip install $package"
        fi
    done
}

# Function to setup environment variables
setup_environment() {
    print_status "Setting up environment variables..."
    
    # Load .env file if it exists
    if [ -f ".env" ]; then
        print_status "Loading environment variables from .env"
        export $(grep -v '^#' .env | xargs)
    else
        print_warning ".env file not found, using defaults"
        export DEBUG=True
        export SECRET_KEY=django-insecure-development-key
        export ALLOWED_HOSTS=localhost,127.0.0.1
        export OLLAMA_HOST=http://192.168.0.34:1234
    fi
    
    print_success "Environment variables set"
}

# Function to check for updates
check_for_updates() {
    print_status "Checking for updates..."
    
    if [ -f "$VERSION_FILE" ]; then
        STORED_VERSION=$(cat "$VERSION_FILE" 2>/dev/null || echo "0.0.0")
        if [ "$STORED_VERSION" != "$CURRENT_VERSION" ]; then
            print_warning "Update detected: $STORED_VERSION → $CURRENT_VERSION"
            return 0
        else
            print_success "Already up to date (v$CURRENT_VERSION)"
            return 1
        fi
    else
        print_status "First time setup"
        return 0
    fi
}

# Function to apply updates
apply_updates() {
    print_status "Applying updates..."
    
    # Update dependencies
    pip install --upgrade -r requirements.txt || {
        print_warning "Some dependencies failed to update"
    }
    
    # Run migrations
    python manage.py makemigrations --noinput || true
    python manage.py migrate --noinput || true
    
    # Collect static files
    python manage.py collectstatic --noinput || true
    
    # Save new version
    echo "$CURRENT_VERSION" > "$VERSION_FILE"
    
    print_success "Updates applied successfully"
}

# Function to run Django migrations
run_migrations() {
    print_status "Running Django migrations..."
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Run migrations
    python manage.py makemigrations --noinput || true
    python manage.py migrate --noinput || true
    
    print_success "Django migrations completed"
}

# Function to collect static files
collect_static() {
    print_status "Collecting static files..."
    python manage.py collectstatic --noinput || true
    print_success "Static files collected"
}

# Function to create superuser if needed
create_superuser() {
    print_status "Checking superuser..."
    
    # Check if superuser exists
    if ! python manage.py shell -c "from django.contrib.auth.models import User; exit(0 if User.objects.filter(username='admin').exists() else 1)" 2>/dev/null; then
        print_status "Creating superuser..."
        echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell
        print_success "Superuser created: admin/admin123"
    else
        print_success "Superuser already exists"
    fi
}

# Function to make scripts executable
make_scripts_executable() {
    print_status "Making scripts executable..."
    
    # Make all scripts executable
    chmod +x scripts/*.sh 2>/dev/null || true
    chmod +x *.sh 2>/dev/null || true
    
    print_success "Scripts made executable"
}

# Function to start LM Studio if available
start_lm_studio() {
    print_status "Checking LM Studio..."
    
    # Check if LM Studio API is responding
    if curl -s http://192.168.0.34:1234/api/tags > /dev/null 2>&1; then
        print_success "LM Studio API is responding"
        return 0
    fi
    
    # Check if LM Studio process is running (multiple possible names)
    if pgrep -f "lm-studio" > /dev/null || pgrep -f "LM-Studio" > /dev/null || pgrep -f "lmstudio" > /dev/null; then
        print_warning "LM Studio process found but API not responding"
        print_status "Waiting for LM Studio to start up..."
        
        # Wait up to 30 seconds for LM Studio to start
        for i in {1..30}; do
            if curl -s http://192.168.0.34:1234/api/tags > /dev/null 2>&1; then
                print_success "LM Studio API is now responding"
                return 0
            fi
            sleep 1
        done
        
        print_warning "LM Studio process found but API still not responding after 30 seconds"
    fi
    
    # LM Studio is not running, try to start it
    print_status "Starting LM Studio..."
    
    # Check if AppImage exists
    if [ -f "Studio/LM-Studio-0.3.20-4-x64.AppImage" ]; then
        chmod +x Studio/LM-Studio-0.3.20-4-x64.AppImage
        print_status "Starting LM Studio AppImage..."
        nohup Studio/LM-Studio-0.3.20-4-x64.AppImage > /dev/null 2>&1 &
        LM_STUDIO_PID=$!
        
        # Wait for LM Studio to start
        print_status "Waiting for LM Studio to start up..."
        for i in {1..60}; do
            if curl -s http://192.168.0.34:1234/api/tags > /dev/null 2>&1; then
                print_success "LM Studio started successfully (PID: $LM_STUDIO_PID)"
                return 0
            fi
            sleep 1
        done
        
        print_warning "LM Studio started but API not responding after 60 seconds"
    else
        print_warning "LM Studio AppImage not found at Studio/LM-Studio-0.3.20-4-x64.AppImage"
        print_status "Please ensure LM Studio is installed and running manually"
    fi
    
    # Final check
    if curl -s http://192.168.0.34:1234/api/tags > /dev/null 2>&1; then
        print_success "LM Studio API is responding"
    else
        print_warning "LM Studio API not responding - you may need to start it manually"
    fi
}

# Function to run health checks
run_health_checks() {
    print_status "Running health checks..."
    
    # Check database connection
    if python manage.py check --database default > /dev/null 2>&1; then
        print_success "Database connection: OK"
    else
        print_warning "Database connection: Issues detected"
    fi
    
    # Check Django settings
    if python manage.py check > /dev/null 2>&1; then
        print_success "Django settings: OK"
    else
        print_warning "Django settings: Issues detected"
    fi
    
    # Check static files
    if [ -d "staticfiles" ]; then
        print_success "Static files: OK"
    else
        print_warning "Static files: Not collected"
    fi
    
    print_success "Health checks completed"
}

# Function to start Django development server
start_django_server() {
    print_status "Starting Django development server..."
    
    print_success "Starting Django server on 0.0.0.0:8000"
    print_status "Press Ctrl+C to stop the server"
    
    # Start Django server
    exec python manage.py runserver 0.0.0.0:8000
}

# Function to show startup information
show_startup_info() {
    echo ""
    echo "🎉 AI Report Writer Development Server Started!"
    echo "============================================="
    echo ""
    echo "Available Services:"
    echo "- Django Web Server: http://localhost:8000"
    echo "- LM Studio API: http://192.168.0.34:1234"
    echo ""
    echo "Project URLs:"
    echo "- Home: http://localhost:8000/"
    echo "- Admin: http://localhost:8000/admin (admin/admin123)"
    echo "- Upload: http://localhost:8000/upload/"
    echo "- Documents: http://localhost:8000/documents/"
    echo ""
    echo "Environment:"
    echo "- Python: $(python --version)"
    echo "- Django: $(python -c 'import django; print(django.get_version())')"
    echo "- Virtual Environment: $(which python)"
    echo ""
    echo "Development Commands:"
    echo "- View logs: tail -f logs/app.log"
    echo "- Run tests: python manage.py test"
    echo "- Create superuser: python manage.py createsuperuser"
    echo "- Check status: ./scripts/status.sh"
    echo "- Backup data: ./scripts/backup.sh"
    echo ""
}

# Function to handle graceful shutdown
cleanup() {
    print_status "Shutting down gracefully..."
    
    # Stop Django server
    pkill -f "manage.py runserver" 2>/dev/null || true
    
    print_success "Shutdown complete"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Main startup function
main() {
    print_status "Starting AI Report Writer development environment..."
    
    # Check Python
    check_python
    
    # Check system requirements
    check_system_requirements
    
    # Create virtual environment if needed
    create_venv
    
    # Install dependencies if needed
    install_dependencies
    
    # Create .env file if needed
    create_env_file
    
    # Create directories if needed
    create_directories
    
    # Activate virtual environment
    activate_venv
    
    # Check Python packages
    check_python_packages
    
    # Setup environment
    setup_environment
    
    # Make scripts executable
    make_scripts_executable
    
    # Check for updates
    if check_for_updates; then
        apply_updates
    fi
    
    # Run migrations
    run_migrations
    
    # Collect static files
    collect_static
    
    # Create superuser if needed
    create_superuser
    
    # Run health checks
    run_health_checks
    
    # Start LM Studio if available
    start_lm_studio
    
    # Show startup information
    show_startup_info
    
    # Start Django server (this will be the main process)
    start_django_server
}

# Parse command line arguments
case "${1:-}" in
    "migrate")
        print_status "Running migrations only..."
        activate_venv
        setup_environment
        run_migrations
        print_success "Migrations completed"
        ;;
    "test")
        print_status "Running tests..."
        activate_venv
        python manage.py test
        ;;
    "shell")
        print_status "Opening Django shell..."
        activate_venv
        setup_environment
        python manage.py shell
        ;;
    "createsuperuser")
        print_status "Creating superuser..."
        activate_venv
        setup_environment
        python manage.py createsuperuser
        ;;
    "setup")
        print_status "Running setup only..."
        check_python
        check_system_requirements
        create_venv
        install_dependencies
        create_env_file
        create_directories
        activate_venv
        make_scripts_executable
        setup_environment
        run_migrations
        collect_static
        create_superuser
        run_health_checks
        print_success "Setup completed"
        ;;
    "update")
        print_status "Running update only..."
        activate_venv
        setup_environment
        apply_updates
        print_success "Update completed"
        ;;
    "status")
        print_status "Checking system status..."
        ./scripts/status.sh
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  (no args)  - Start Django development server with full setup"
        echo "  setup      - Run setup only (create venv, install deps)"
        echo "  migrate    - Run Django migrations only"
        echo "  test       - Run tests"
        echo "  shell      - Open Django shell"
        echo "  createsuperuser - Create Django superuser"
        echo "  update     - Apply updates only"
        echo "  status     - Check system status"
        echo "  help       - Show this help"
        ;;
    *)
        main
        ;;
esac 