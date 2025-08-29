# Simple AI Report Writer Startup Script for Windows
Write-Host "AI Report Writer - Simple Startup" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Change to project root directory
Set-Location -Path ".."

# Set virtual environment Python path
$venvPython = ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    $venvPython = "venv\Scripts\python.exe"
}

# Check if virtual environment exists
if (-not (Test-Path $venvPython)) {
    Write-Host "ERROR: Virtual environment not found. Please run setup first." -ForegroundColor Red
    Write-Host "INFO: Run 'python -m venv .venv' to create virtual environment" -ForegroundColor Yellow
    exit 1
}

Write-Host "SUCCESS: Virtual environment found" -ForegroundColor Green

# Check Django installation
try {
    $djangoVersion = & $venvPython -c "import django; print(django.get_version())" 2>&1
    Write-Host "SUCCESS: Django installed: $djangoVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Django not installed. Installing dependencies..." -ForegroundColor Red
    & $venvPython -m pip install -r requirements.txt
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "INFO: Creating .env file..." -ForegroundColor Yellow
    @"
# Django Configuration
DEBUG=True
SECRET_KEY=django-insecure-development-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# AI Configuration (OpenRoute AI)
OPENROUTE_HOST=https://openrouter.ai/api/v1

OPENROUTE_API_KEY_OPENROUTER=sk-or-v1-apikeyfa
BREAKDOWN_MODEL=deepseek/model
REVIEWER_MODEL=tngtech/model
FINALIZER_MODEL=deepseek/model
REANALYZER_MODEL=openrouter/model

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "SUCCESS: .env file created" -ForegroundColor Green
}

# Create directories
$directories = @("logs", "media\documents", "staticfiles", "assets", "java_assets", "prompts", "backups")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "SUCCESS: Directories created" -ForegroundColor Green

# Run migrations
Write-Host "INFO: Running migrations..." -ForegroundColor Yellow
& $venvPython manage.py migrate --noinput
Write-Host "SUCCESS: Migrations completed" -ForegroundColor Green

# Collect static files
Write-Host "INFO: Collecting static files..." -ForegroundColor Yellow
& $venvPython manage.py collectstatic --noinput
Write-Host "SUCCESS: Static files collected" -ForegroundColor Green

# Create superuser if needed
Write-Host "INFO: Checking superuser..." -ForegroundColor Yellow
try {
    $result = & $venvPython manage.py shell -c "from django.contrib.auth.models import User; exit(0 if User.objects.filter(username='admin').exists() else 1)" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "INFO: Creating superuser..." -ForegroundColor Yellow
        $superuserScript = @"
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
"@
        $superuserScript | & $venvPython manage.py shell
        Write-Host "SUCCESS: Superuser created: admin/admin123" -ForegroundColor Green
    } else {
        Write-Host "SUCCESS: Superuser already exists" -ForegroundColor Green
    }
} catch {
    Write-Host "WARNING: Could not check/create superuser" -ForegroundColor Yellow
}

# Check OpenRoute AI configuration
Write-Host "INFO: Checking OpenRoute AI configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found. Please create one with your OpenRoute API key." -ForegroundColor Yellow
    Write-Host "INFO: You can get your API key from https://openrouter.ai/keys" -ForegroundColor Yellow
} else {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "OPENROUTE_API_KEY=your-openroute-api-key-here") {
        Write-Host "WARNING: Please update your OpenRoute API key in the .env file" -ForegroundColor Yellow
        Write-Host "INFO: Get your API key from https://openrouter.ai/keys" -ForegroundColor Yellow
    } else {
        Write-Host "SUCCESS: OpenRoute AI configuration found" -ForegroundColor Green
    }
}

# Show startup information
Write-Host ""
Write-Host "SUCCESS: AI Report Writer Development Server Ready!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Available Services:" -ForegroundColor White
Write-Host "- Django Web Server: http://localhost:8000" -ForegroundColor White
Write-Host "- OpenRoute AI API: https://openrouter.ai/api/v1" -ForegroundColor White
Write-Host ""
Write-Host "Project URLs:" -ForegroundColor White
Write-Host "- Home: http://localhost:8000/" -ForegroundColor White
Write-Host "- Admin: http://localhost:8000/admin (admin/admin123)" -ForegroundColor White
Write-Host "- Upload: http://localhost:8000/upload/" -ForegroundColor White
Write-Host "- Documents: http://localhost:8000/documents/" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start Django server
Write-Host "INFO: Starting Django development server..." -ForegroundColor Green
& $venvPython manage.py runserver 0.0.0.0:8000
