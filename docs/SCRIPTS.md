# 🛠️ Scripts Reference Guide

Complete reference for all automation scripts in AI Report Writer. These scripts help with development, deployment, maintenance, and troubleshooting.

## 📁 Scripts Overview

All scripts are located in the `scripts/` directory and organized by functionality:

```
scripts/
├── start_simple.ps1      # Simple Windows startup (PowerShell)
├── start.bat            # Full Windows startup (Batch)
├── start.sh             # Unix/Linux startup script
├── status.sh            # System status checker
├── backup.sh            # Backup and restore utility
├── update.sh            # Update and maintenance script
├── format_code.py       # Code quality and formatting
├── generate_secret_key.py # Django secret key generator
└── switch_model.py      # AI model switching utility
```

## 🚀 Startup Scripts

### `start_simple.ps1` (Windows PowerShell)
**Purpose**: Simple, fast startup for Windows users with PowerShell.

**When to use**: 
- Quick development sessions
- Windows 10/11 with PowerShell
- When you need minimal setup

**Usage**:
```powershell
# Run from project root
.\scripts\start_simple.ps1

# Or double-click in Windows Explorer
```

**Features**:
- ✅ Virtual environment detection and creation
- ✅ Dependency installation
- ✅ Environment file creation
- ✅ Database migrations
- ✅ Superuser creation (admin/admin123)
- ✅ Django development server startup

**Requirements**:
- Windows 10+ with PowerShell
- Python 3.9+
- Internet connection for package installation

---

### `start.bat` (Windows Batch)
**Purpose**: Comprehensive startup script for Windows with full system setup.

**When to use**:
- First-time setup
- Production-like development environment
- When you need comprehensive health checks
- Older Windows systems

**Usage**:
```cmd
# Run from project root
scripts\start.bat

# With options
scripts\start.bat setup      # Setup only
scripts\start.bat migrate    # Migrations only
scripts\start.bat test       # Run tests
scripts\start.bat help       # Show help
```

**Features**:
- 🔧 Complete environment setup
- 📦 Dependency management with updates
- 🗄️ Database migrations and health checks
- 👤 Automatic superuser creation
- 🎯 Version tracking and updates
- 📊 Comprehensive health monitoring
- 🚀 Production-ready configuration

**Command Options**:
- `setup` - Run setup only (no server start)
- `migrate` - Run database migrations only
- `test` - Execute test suite
- `shell` - Open Django shell
- `createsuperuser` - Create Django superuser
- `update` - Apply updates only
- `status` - Check system status
- `help` - Display help information

---

### `start.sh` (Unix/Linux/macOS)
**Purpose**: Full-featured startup script for Unix-based systems.

**When to use**:
- Linux/macOS development
- Production deployments
- Docker containers
- Comprehensive system setup

**Usage**:
```bash
# Make executable (first time)
chmod +x scripts/start.sh

# Run with options
./scripts/start.sh           # Full startup
./scripts/start.sh setup     # Setup only
./scripts/start.sh migrate   # Migrations only
./scripts/start.sh test      # Run tests
```

**Features**:
- 🐧 Cross-platform Unix compatibility
- 🔄 Automatic updates and version management
- 🏥 Health checks and system validation
- 📊 Resource monitoring
- 🔒 Security checks
- 🚀 Production deployment ready

## 📊 Monitoring & Maintenance Scripts

### `status.sh`
**Purpose**: Comprehensive system status checker and health monitor.

**When to use**:
- Troubleshooting issues
- Regular health monitoring
- Before starting development
- Production system checks

**Usage**:
```bash
./scripts/status.sh
```

**Checks Performed**:
- 📦 Virtual environment status
- 🗄️ Database connectivity
- 🤖 OpenRouter AI API status
- 🌐 Django server status
- 🔐 File permissions
- 💾 Disk space availability
- 📈 Service status summary

**Output Example**:
```
🔍 AI Report Writer Status Dashboard
===================================
📦 Virtual Environment Status:
  ✅ Virtual environment: Exists
  ✅ Status: Activated

🗄️ Database Status:
  ✅ Database file: Exists
  ✅ Connection: OK

🤖 OpenRoute AI Status:
  ✅ Configuration: Found
  ✅ API Keys: Configured
  ✅ API: Responding

📊 Summary
==========
Services running: 1/1
🎉 All services are running!
```

---

### `backup.sh`
**Purpose**: Comprehensive backup and restore utility for data protection.

**When to use**:
- Before major updates
- Regular data backups
- Before system changes
- Disaster recovery preparation

**Usage**:
```bash
./scripts/backup.sh
```

**Backup Contents**:
- 🗄️ **Database**: Complete SQLite backup
- 📄 **Documents**: All uploaded files and media
- ⚙️ **Configuration**: Settings, environment files
- 💻 **Custom Code**: Templates, static files, modifications
- 📦 **Full Archive**: Complete project backup

**Output**:
- `backups/ai_report_writer_backup_YYYYMMDD_HHMMSS.tar.gz`
- Individual component backups
- Automatic cleanup (keeps last 5 backups)

**Restore Process**:
```bash
# Extract backup
tar -xzf backups/ai_report_writer_backup_20250829_140000.tar.gz

# Run setup
./scripts/start.sh setup
```

---

### `update.sh`
**Purpose**: Automated update and maintenance system.

**When to use**:
- Regular maintenance
- Applying new features
- Dependency updates
- System upgrades

**Usage**:
```bash
./scripts/update.sh
```

**Update Process**:
1. 💾 **Pre-update backup**
2. 📦 **Dependency updates**
3. 🗄️ **Database migrations**
4. 📁 **Static file collection**
5. 🔍 **New app detection**
6. ⚙️ **Configuration updates**
7. 🏥 **Health checks**
8. 📝 **Version tracking**

**Version Management**:
- Tracks current version in `.version` file
- Automatic detection of updates needed
- Rollback capability with backups

## 🔧 Development Tools

### `format_code.py`
**Purpose**: Comprehensive code quality and formatting automation.

**When to use**:
- Before committing code
- Regular code maintenance
- CI/CD pipelines
- Code review preparation

**Usage**:
```bash
# Format and fix issues
python scripts/format_code.py

# Check only (no changes)
python scripts/format_code.py --check

# Explicit fix mode
python scripts/format_code.py --fix
```

**Quality Checks**:
1. 📐 **Import Sorting** (isort)
2. 🎨 **Code Formatting** (black)
3. 🔍 **Linting** (flake8)
4. 🏷️ **Type Checking** (mypy)
5. 🔒 **Security Scanning** (bandit)

**Output Example**:
```
🛠️  AI Report Writer - Code Quality Tools
==================================================
🔧 Running in FIX mode (files will be formatted)

🔄 Import sorting (isort)...
✅ Import sorting (isort) - PASSED

🔄 Code formatting (black)...
✅ Code formatting (black) - PASSED

🔄 Code linting (flake8)...
✅ Code linting (flake8) - PASSED

📊 Code Quality Summary: 5/5 checks passed
🎉 All code quality checks passed!
```

---

### `generate_secret_key.py`
**Purpose**: Generate secure Django secret keys.

**When to use**:
- Initial setup
- Security key rotation
- Production deployment
- Environment configuration

**Usage**:
```bash
python scripts/generate_secret_key.py
```

**Features**:
- 🔐 Cryptographically secure key generation
- 📋 Ready-to-use format
- 🔄 Multiple key generation
- 📝 Direct .env file integration

---

### `switch_model.py`
**Purpose**: AI model management and switching utility.

**When to use**:
- Changing AI models
- Testing different models
- Performance optimization
- Model configuration

**Usage**:
```bash
# List available models
python scripts/switch_model.py --list

# Switch to specific model
python scripts/switch_model.py --model "openai/gpt-4"

# Interactive model selection
python scripts/switch_model.py --interactive
```

**Supported Models**:
- OpenAI GPT models
- Anthropic Claude models
- DeepSeek models
- Local models via OpenRouter

## 🎯 Usage Scenarios

### Daily Development Workflow
```bash
# 1. Check system status
./scripts/status.sh

# 2. Start development environment
./scripts/start.sh

# 3. Make code changes...

# 4. Format code before committing
python scripts/format_code.py

# 5. Run tests
python run_tests.py
```

### First-Time Setup
```bash
# Windows PowerShell (simple)
.\scripts\start_simple.ps1

# Windows Batch (comprehensive)
scripts\start.bat setup

# Linux/macOS
./scripts/start.sh setup
```

### Production Deployment
```bash
# 1. Backup current system
./scripts/backup.sh

# 2. Update system
./scripts/update.sh

# 3. Run health checks
./scripts/status.sh

# 4. Start production server
./scripts/start.sh
```

### Troubleshooting
```bash
# 1. Check system status
./scripts/status.sh

# 2. Verify code quality
python scripts/format_code.py --check

# 3. Run comprehensive tests
python run_tests.py

# 4. Check recent backups
ls -la backups/
```

## ⚙️ Configuration

### Environment Variables
Scripts respect these environment variables:

```bash
# Development/Production mode
DEBUG=True|False

# Database configuration
DATABASE_URL=sqlite:///db.sqlite3

# AI model settings
OPENROUTER_API_KEY=your-key-here
BREAKDOWN_MODEL=deepseek/deepseek-r1-0528-qwen3-8b:free

# Script behavior
SCRIPT_VERBOSE=True|False
AUTO_UPDATE=True|False
BACKUP_RETENTION=5
```

### Script Customization
Most scripts can be customized by editing variables at the top:

```bash
# In backup.sh
BACKUP_DIR="backups"
BACKUP_RETENTION=5

# In update.sh
CURRENT_VERSION="1.0.0"
VERSION_FILE=".version"
```

## 🚨 Troubleshooting

### Common Issues

#### Permission Denied
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Fix ownership
sudo chown -R $USER:$USER scripts/
```

#### Virtual Environment Issues
```bash
# Remove and recreate
rm -rf venv .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Script Fails to Start
```bash
# Check Python installation
python3 --version

# Check script syntax
bash -n scripts/start.sh

# Run with debug output
bash -x scripts/start.sh
```

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Python not found" | Missing Python | Install Python 3.9+ |
| "Virtual env failed" | Permission/space issue | Check permissions and disk space |
| "Django not found" | Missing dependencies | Run `pip install -r requirements.txt` |
| "Port already in use" | Server running | Kill process or use different port |

## 📞 Getting Help

### Script-Specific Help
Most scripts have built-in help:

```bash
./scripts/start.sh help
scripts\start.bat help
python scripts/format_code.py --help
```

### Log Files
Scripts create log files in:
- `logs/startup.log` - Startup script logs
- `logs/backup.log` - Backup operation logs
- `logs/update.log` - Update process logs

### Support Resources
- **Documentation**: Complete guides in `/docs/`
- **Issues**: GitHub Issues for bug reports
- **Community**: GitHub Discussions for help
- **Examples**: Script examples in repository

---

**🎉 Happy scripting!** These tools are designed to make your development workflow smooth and efficient.
