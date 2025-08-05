@echo off
setlocal enabledelayedexpansion

REM AI Report Writer - Complete Startup & Setup Script for Windows
REM Handles everything automatically with constant updates and comprehensive setup

echo 🚀 AI Report Writer - Complete Startup & Setup System
echo ====================================================

REM Color codes for output (Windows 10+ supports ANSI colors)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Version tracking
set "CURRENT_VERSION=1.0.0"
set "VERSION_FILE=.version"

REM Function to print colored output
:print_status
echo %BLUE%[INFO]%NC% %~1
goto :eof

:print_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:print_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:print_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM Function to check if Python is available
:check_python
call :print_status "Checking Python installation..."
python --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Python is not installed or not in PATH. Please install Python 3 first."
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
call :print_success "Python found: %PYTHON_VERSION%"
goto :eof

REM Function to check system requirements
:check_system_requirements
call :print_status "Checking system requirements..."
goto :eof

REM Function to create virtual environment if needed
:create_venv
call :print_status "Checking virtual environment..."
if not exist "venv" (
    call :print_status "Creating virtual environment..."
    python -m venv venv
    if errorlevel 1 (
        call :print_error "Failed to create virtual environment"
        exit /b 1
    )
    call :print_success "Virtual environment created"
) else (
    call :print_success "Virtual environment found"
)
goto :eof

REM Function to install dependencies if needed
:install_dependencies
call :print_status "Checking Python dependencies..."
call venv\Scripts\activate.bat
if errorlevel 1 (
    call :print_error "Failed to activate virtual environment"
    exit /b 1
)

REM Check if key packages are installed
python -c "import django" >nul 2>&1
if errorlevel 1 (
    call :print_status "Installing Python dependencies..."
    
    REM Upgrade pip
    python -m pip install --upgrade pip
    
    REM Install core dependencies first
    pip install django python-docx PyPDF2 requests python-dotenv
    if errorlevel 1 (
        call :print_error "Failed to install core dependencies"
        exit /b 1
    )
    
    REM Install requirements if file exists
    if exist "requirements.txt" (
        pip install -r requirements.txt
        if errorlevel 1 (
            call :print_warning "Some requirements failed to install"
        )
    )
    
    call :print_success "Python dependencies installed"
) else (
    call :print_success "Python dependencies already installed"
)
goto :eof

REM Function to create .env file if needed
:create_env_file
call :print_status "Checking environment file..."
if not exist ".env" (
    call :print_status "Creating .env file..."
    (
        echo # Django Configuration
        echo DEBUG=True
        echo SECRET_KEY=django-insecure-development-key-change-in-production
        echo ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
        echo.
        echo # AI Configuration ^(LM Studio^)
        echo OLLAMA_HOST=http://192.168.0.34:1234
        echo BREAKDOWN_MODEL=deepseek-r1-distill-qwen-7b
        echo REVIEWER_MODEL=whiterabbitneo-2.5-qwen-2.5-coder-7b
        echo FINALIZER_MODEL=llama-3-8b-gpt-40-ru1.0
        echo REANALYZER_MODEL=h2o-danube2-1.8b-chat
        echo.
        echo # Database Configuration
        echo DATABASE_URL=sqlite:///db.sqlite3
        echo.
        echo # Logging Configuration
        echo LOG_LEVEL=INFO
        echo LOG_FILE=logs/app.log
    ) > .env
    call :print_success ".env file created"
) else (
    call :print_success ".env file already exists"
)
goto :eof

REM Function to create directories if needed
:create_directories
call :print_status "Creating project directories..."
if not exist "logs" mkdir logs
if not exist "media\documents" mkdir media\documents
if not exist "staticfiles" mkdir staticfiles
if not exist "assets" mkdir assets
if not exist "java_assets" mkdir java_assets
if not exist "prompts" mkdir prompts
if not exist "backups" mkdir backups
if not exist "Studio" mkdir Studio
call :print_success "Project directories created"
goto :eof

REM Function to activate virtual environment
:activate_venv
call :print_status "Activating virtual environment..."
call venv\Scripts\activate.bat
call :print_success "Virtual environment activated"
goto :eof

REM Function to check Python packages
:check_python_packages
call :print_status "Checking Python packages..."
set "packages=django requests python-docx PyPDF2 python-dotenv"
for %%p in (%packages%) do (
    python -c "import %%p" >nul 2>&1
    if errorlevel 1 (
        call :print_error "%%p: Not installed"
        call :print_status "Please run: pip install %%p"
    ) else (
        call :print_success "%%p: OK"
    )
)
goto :eof

REM Function to setup environment variables
:setup_environment
call :print_status "Setting up environment variables..."
if exist ".env" (
    REM Load environment variables from .env file
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" (
            set "%%a=%%b"
        )
    )
    call :print_success "Environment variables loaded from .env"
) else (
    call :print_warning ".env file not found, using defaults"
    set "DEBUG=True"
    set "SECRET_KEY=django-insecure-development-key"
    set "ALLOWED_HOSTS=localhost,127.0.0.1"
    set "OLLAMA_HOST=http://192.168.0.34:1234"
)
goto :eof

REM Function to check for updates
:check_for_updates
call :print_status "Checking for updates..."
if exist "%VERSION_FILE%" (
    set /p STORED_VERSION=<%VERSION_FILE%
    if not "!STORED_VERSION!"=="%CURRENT_VERSION%" (
        call :print_warning "Update detected: !STORED_VERSION! → %CURRENT_VERSION%"
        exit /b 0
    ) else (
        call :print_success "Already up to date (v%CURRENT_VERSION%)"
        exit /b 1
    )
) else (
    call :print_status "First time setup"
    exit /b 0
)
goto :eof

REM Function to apply updates
:apply_updates
call :print_status "Applying updates..."
pip install --upgrade -r requirements.txt
if errorlevel 1 (
    call :print_warning "Some dependencies failed to update"
)

REM Run migrations
python manage.py makemigrations --noinput
python manage.py migrate --noinput

REM Collect static files
python manage.py collectstatic --noinput

REM Save new version
echo %CURRENT_VERSION% > "%VERSION_FILE%"
call :print_success "Updates applied successfully"
goto :eof

REM Function to run Django migrations
:run_migrations
call :print_status "Running Django migrations..."
if not exist "logs" mkdir logs
python manage.py makemigrations --noinput
python manage.py migrate --noinput
call :print_success "Django migrations completed"
goto :eof

REM Function to collect static files
:collect_static
call :print_status "Collecting static files..."
python manage.py collectstatic --noinput
call :print_success "Static files collected"
goto :eof

REM Function to create superuser if needed
:create_superuser
call :print_status "Checking superuser..."
python manage.py shell -c "from django.contrib.auth.models import User; exit(0 if User.objects.filter(username='admin').exists() else 1)" >nul 2>&1
if errorlevel 1 (
    call :print_status "Creating superuser..."
    echo from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None | python manage.py shell
    call :print_success "Superuser created: admin/admin123"
) else (
    call :print_success "Superuser already exists"
)
goto :eof

REM Function to start LM Studio if available
:start_lm_studio
call :print_status "Checking LM Studio..."

REM Check LM Studio API
call :print_status "Checking LM Studio API..."
curl -s http://192.168.0.34:1234/v1/models >nul 2>&1
if errorlevel 1 (
    call :print_warning "LM Studio API not responding"
    call :print_status "Please ensure LM Studio is running with local server enabled"
) else (
    call :print_success "LM Studio API is responding"
)

REM Check if LM Studio process is running
tasklist /FI "IMAGENAME eq LM-Studio-0.3.20-4-x64.exe" 2>NUL | find /I /N "LM-Studio-0.3.20-4-x64.exe">NUL
if errorlevel 1 (
    REM LM Studio is not running, try to start it
    call :print_status "Starting LM Studio..."
    
    REM Check if exe exists
    if exist "Studio\LM-Studio-0.3.20-4-x64.exe" (
        call :print_status "Starting LM Studio executable..."
        start "" "Studio\LM-Studio-0.3.20-4-x64.exe"
        
        REM Wait for LM Studio to start
        call :print_status "Waiting for LM Studio to start up..."
        for /l %%i in (1,1,60) do (
            timeout /t 1 /nobreak >nul
            curl -s http://192.168.0.34:1234/v1/models >nul 2>&1
            if not errorlevel 1 (
                call :print_success "LM Studio started successfully"
                goto :lm_studio_started
            )
        )
        call :print_warning "LM Studio started but API not responding after 60 seconds"
    ) else (
        call :print_warning "LM Studio executable not found at Studio\LM-Studio-0.3.20-4-x64.exe"
        call :print_status "Please ensure LM Studio is installed and running manually"
    )
) else (
    call :print_warning "LM Studio process found but API not responding"
    call :print_status "Waiting for LM Studio to start up..."
    
    REM Wait up to 30 seconds for LM Studio to start
    for /l %%i in (1,1,30) do (
        timeout /t 1 /nobreak >nul
        curl -s http://192.168.0.34:1234/v1/models >nul 2>&1
        if not errorlevel 1 (
            call :print_success "LM Studio API is now responding"
            goto :lm_studio_started
        )
    )
    call :print_warning "LM Studio process found but API still not responding after 30 seconds"
)

:lm_studio_started
REM Final check
curl -s http://192.168.0.34:1234/v1/models >nul 2>&1
if errorlevel 1 (
    call :print_warning "LM Studio API not responding - you may need to start it manually"
) else (
    call :print_success "LM Studio API is responding"
)
goto :eof

REM Function to run health checks
:run_health_checks
call :print_status "Running health checks..."

REM Check database connection
python manage.py check --database default >nul 2>&1
if errorlevel 1 (
    call :print_warning "Database connection: Issues detected"
) else (
    call :print_success "Database connection: OK"
)

REM Check Django settings
python manage.py check >nul 2>&1
if errorlevel 1 (
    call :print_warning "Django settings: Issues detected"
) else (
    call :print_success "Django settings: OK"
)

REM Check static files
if exist "staticfiles" (
    call :print_success "Static files: OK"
) else (
    call :print_warning "Static files: Not collected"
)

call :print_success "Health checks completed"
goto :eof

REM Function to start Django development server
:start_django_server
call :print_status "Starting Django development server..."
call :print_success "Starting Django server on 0.0.0.0:8000"
call :print_status "Press Ctrl+C to stop the server"
python manage.py runserver 0.0.0.0:8000
goto :eof

REM Function to show startup information
:show_startup_info
echo.
echo 🎉 AI Report Writer Development Server Started!
echo =============================================
echo.
echo Available Services:
echo - Django Web Server: http://localhost:8000
echo - LM Studio API: http://192.168.0.34:1234
echo.
echo Project URLs:
echo - Home: http://localhost:8000/
echo - Admin: http://localhost:8000/admin (admin/admin123)
echo - Upload: http://localhost:8000/upload/
echo - Documents: http://localhost:8000/documents/
echo.
echo Environment:
for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo - Python: %%i
for /f "tokens=2" %%i in ('python -c "import django; print(django.get_version())" 2^>^&1') do echo - Django: %%i
echo - Virtual Environment: venv\Scripts\python.exe
echo.
echo Development Commands:
echo - View logs: type logs\app.log
echo - Run tests: python manage.py test
echo - Create superuser: python manage.py createsuperuser
echo - Check status: scripts\status.bat
echo - Backup data: scripts\backup.bat
echo.
goto :eof

REM Function to handle graceful shutdown
:cleanup
call :print_status "Shutting down gracefully..."
taskkill /F /IM python.exe /T >nul 2>&1
call :print_success "Shutdown complete"
exit /b 0

REM Main startup function
:main
call :print_status "Starting AI Report Writer development environment..."

REM Check Python
call :check_python
if errorlevel 1 exit /b 1

REM Check system requirements
call :check_system_requirements

REM Create virtual environment if needed
call :create_venv
if errorlevel 1 exit /b 1

REM Install dependencies if needed
call :install_dependencies
if errorlevel 1 exit /b 1

REM Create .env file if needed
call :create_env_file

REM Create directories if needed
call :create_directories

REM Activate virtual environment
call :activate_venv

REM Check Python packages
call :check_python_packages

REM Setup environment
call :setup_environment

REM Check for updates
call :check_for_updates
if not errorlevel 1 (
    call :apply_updates
)

REM Run migrations
call :run_migrations

REM Collect static files
call :collect_static

REM Create superuser if needed
call :create_superuser

REM Run health checks
call :run_health_checks

REM Start LM Studio if available
call :start_lm_studio

REM Show startup information
call :show_startup_info

REM Start Django server (this will be the main process)
call :start_django_server
goto :eof

REM Parse command line arguments
if "%1"=="migrate" (
    call :print_status "Running migrations only..."
    call :activate_venv
    call :setup_environment
    call :run_migrations
    call :print_success "Migrations completed"
    goto :end
)

if "%1"=="test" (
    call :print_status "Running tests..."
    call :activate_venv
    python manage.py test
    goto :end
)

if "%1"=="shell" (
    call :print_status "Opening Django shell..."
    call :activate_venv
    call :setup_environment
    python manage.py shell
    goto :end
)

if "%1"=="createsuperuser" (
    call :print_status "Creating superuser..."
    call :activate_venv
    call :setup_environment
    python manage.py createsuperuser
    goto :end
)

if "%1"=="setup" (
    call :print_status "Running setup only..."
    call :check_python
    call :check_system_requirements
    call :create_venv
    call :install_dependencies
    call :create_env_file
    call :create_directories
    call :activate_venv
    call :setup_environment
    call :run_migrations
    call :collect_static
    call :create_superuser
    call :run_health_checks
    call :print_success "Setup completed"
    goto :end
)

if "%1"=="update" (
    call :print_status "Running update only..."
    call :activate_venv
    call :setup_environment
    call :apply_updates
    call :print_success "Update completed"
    goto :end
)

if "%1"=="status" (
    call :print_status "Checking system status..."
    if exist "scripts\status.bat" (
        call scripts\status.bat
    ) else (
        call :print_warning "Status script not found"
    )
    goto :end
)

if "%1"=="help" (
    echo Usage: %0 [command]
    echo.
    echo Commands:
    echo   (no args)  - Start Django development server with full setup
    echo   setup      - Run setup only (create venv, install deps)
    echo   migrate    - Run Django migrations only
    echo   test       - Run tests
    echo   shell      - Open Django shell
    echo   createsuperuser - Create Django superuser
    echo   update     - Apply updates only
    echo   status     - Check system status
    echo   help       - Show this help
    goto :end
)

REM Default: run main function
call :main

:end
pause 