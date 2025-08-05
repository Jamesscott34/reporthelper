# Windows Setup Guide for AI Report Writer

This guide will help you set up and run the AI Report Writer project on Windows.



## Prerequisites

1. **Python 3.8+** - Download and install from [python.org](https://www.python.org/downloads/)
2. **Git** - Download and install from [git-scm.com](https://git-scm.com/download/win)
3. **LM Studio** - The executable is included in the `Studio/` directory

## Quick Start

### Option 1: Using PowerShell (Recommended)

1. Open PowerShell as Administrator
2. Navigate to your project directory
3. Run the PowerShell script:

```powershell
# Allow script execution (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser


# Run the startup script
powershell -ExecutionPolicy Bypass -File start_simple.ps1  
```

### Option 2: Using Command Prompt

1. Open Command Prompt as Administrator
2. Navigate to your project directory
3. Run the batch script:

```cmd
start.bat
```

## What the Scripts Do

Both `start.bat` and `start.ps1` perform the following tasks automatically:

1. **Check Python installation** - Verifies Python 3.8+ is installed
2. **Create virtual environment** - Sets up a Python virtual environment
3. **Install dependencies** - Installs all required Python packages
4. **Create configuration** - Sets up `.env` file with default settings
5. **Create directories** - Creates necessary project directories
6. **Run migrations** - Sets up the database
7. **Collect static files** - Gathers static assets
8. **Create superuser** - Creates admin user (admin/admin123)
9. **Start LM Studio** - Launches the LM Studio executable
10. **Start Django server** - Runs the development server on port 8000

## Available Commands

Both scripts support the following commands:

```bash
# Full startup (default)
.\start.ps1
# or
start.bat

# Setup only (create venv, install deps)
.\start.ps1 setup
# or
start.bat setup

# Run migrations only
.\start.ps1 migrate
# or
start.bat migrate

# Run tests
.\start.ps1 test
# or
start.bat test

# Open Django shell
.\start.ps1 shell
# or
start.bat shell

# Create superuser
.\start.ps1 createsuperuser
# or
start.bat createsuperuser

# Apply updates only
.\start.ps1 update
# or
start.bat update

# Check system status
.\start.ps1 status
# or
start.bat status

# Show help
.\start.ps1 help
# or
start.bat help
```

## Accessing the Application

Once the scripts complete successfully, you can access:

- **Main Application**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin (admin/admin123)
- **Upload Page**: http://localhost:8000/upload/
- **Documents**: http://localhost:8000/documents/
- **LM Studio API**: http://192.168.0.34:1234

## Troubleshooting

### Common Issues

1. **Python not found**
   - Ensure Python is installed and added to PATH
   - Try running `python --version` in Command Prompt

2. **Permission denied**
   - Run Command Prompt or PowerShell as Administrator
   - For PowerShell, you may need to set execution policy:
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     ```

3. **LM Studio not starting**
   - Check if the executable exists in `Studio/LM-Studio-0.3.20-4-x64.exe`
   - Try running it manually first
   - Ensure your antivirus isn't blocking it

4. **Port already in use**
   - Check if something is running on port 8000
   - Stop other Django servers or change the port in the script

5. **Virtual environment issues**
   - Delete the `venv` folder and run the script again
   - Ensure you have sufficient disk space

### Manual Setup

If the scripts fail, you can set up manually:

1. **Create virtual environment**:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

3. **Run migrations**:
   ```cmd
   python manage.py migrate
   ```

4. **Create superuser**:
   ```cmd
   python manage.py createsuperuser
   ```

5. **Start server**:
   ```cmd
   python manage.py runserver
   ```

## File Structure

```
Report_AI/
├── start.bat              # Windows batch script
├── start.ps1              # Windows PowerShell script
├── start.sh               # Linux/macOS script
├── Studio/
│   └── LM-Studio-0.3.20-4-x64.exe  # LM Studio executable
├── venv/                  # Python virtual environment
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── .env                   # Environment configuration
```

## Support

If you encounter issues:

1. Check the logs in the `logs/` directory
2. Ensure all prerequisites are installed
3. Try running the script with verbose output
4. Check the Django documentation for specific errors

## Notes

- The scripts are designed to work on Windows 10/11
- PowerShell script requires PowerShell 5.1 or later
- Both scripts will automatically start LM Studio if the executable is found
- The virtual environment is created in the `venv/` directory
- All configuration is stored in the `.env` file 