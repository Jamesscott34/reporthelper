# 🛠️ Scripts and Utilities

This directory contains all the utility scripts and startup scripts for the Report AI system. These scripts handle system startup, maintenance, monitoring, and various utility functions.

## 📋 Script Overview

### 🚀 Startup Scripts

#### `start.sh` - Main Startup Script
- **Purpose**: Complete system initialization and startup
- **Platform**: Linux/macOS
- **Features**: 
  - Environment setup
  - Dependency checking
  - Django server startup
  - Health monitoring
  - Automatic updates

#### `start.bat` - Windows Startup Script
- **Purpose**: Windows-compatible system startup
- **Platform**: Windows
- **Features**: 
  - Windows-specific environment setup
  - Service initialization
  - Error handling for Windows

#### `start_simple.ps1` - PowerShell Startup Script
- **Purpose**: Simplified PowerShell-based startup
- **Platform**: Windows (PowerShell)
- **Features**: 
  - Quick startup for development
  - Minimal configuration
  - Fast execution

#### `start_django.sh` - Django Server Starter
- **Purpose**: Django application server management
- **Platform**: Linux/macOS
- **Features**: 
  - Django server startup
  - Port configuration
  - Process management

### 🔧 Utility Scripts

#### `switch_model.py` - AI Model Switcher
- **Purpose**: Switch between different AI model configurations
- **Language**: Python
- **Features**: 
  - Model preset management
  - Environment file updates
  - Cost optimization
  - Performance tuning

#### `status.sh` - System Status Checker
- **Purpose**: Monitor system health and status
- **Platform**: Linux/macOS
- **Features**: 
  - Service status monitoring
  - Resource usage tracking
  - Error reporting
  - Performance metrics

#### `check_status.sh` - Status Verification
- **Purpose**: Verify system components are running
- **Platform**: Linux/macOS
- **Features**: 
  - Component health checks
  - Dependency verification
  - Quick status overview

#### `update.sh` - System Update Manager
- **Purpose**: Manage system updates and upgrades
- **Platform**: Linux/macOS
- **Features**: 
  - Dependency updates
  - Security patches
  - Feature updates
  - Rollback capabilities

#### `backup.sh` - System Backup Utility
- **Purpose**: Create and manage system backups
- **Platform**: Linux/macOS
- **Features**: 
  - Database backups
  - File system backups
  - Configuration backups
  - Automated scheduling

### 🧪 Testing Scripts

#### `test_lmstudio_integration.py` - LM Studio Integration Test
- **Purpose**: Test LM Studio AI integration
- **Language**: Python
- **Features**: 
  - Connection testing
  - Model availability checks
  - Performance testing
  - Error diagnostics

#### `test_lmstudio.sh` - LM Studio Test Runner
- **Purpose**: Run LM Studio integration tests
- **Platform**: Linux/macOS
- **Features**: 
  - Automated testing
  - Result reporting
  - Performance metrics
  - Error logging

#### `generate_secret_key.py` - Secret Key Generator
- **Purpose**: Generate secure secret keys
- **Language**: Python
- **Features**: 
  - Cryptographically secure keys
  - Django-compatible format
  - Environment file updates
  - Security best practices

## 🚀 Usage Examples

### Starting the System
```bash
# Full system startup (Linux/macOS)
./start.sh

# Windows startup
start.bat

# PowerShell startup
powershell -ExecutionPolicy Bypass -File start_simple.ps1

# Django only
./start_django.sh
```

### Managing AI Models
```bash
# Switch to premium models
python switch_model.py premium

# Switch to free models
python switch_model.py free

# View available presets
python switch_model.py --list
```

### System Monitoring
```bash
# Check system status
./status.sh

# Quick status check
./check_status.sh

# Monitor continuously
watch -n 5 ./status.sh
```

### Maintenance Tasks
```bash
# Update system
./update.sh

# Create backup
./backup.sh

# Test integrations
./test_lmstudio.sh
```

## ⚙️ Configuration

### Environment Variables
Most scripts use environment variables from `.env` file:
- `DJANGO_SETTINGS_MODULE`
- `DATABASE_URL`
- `SECRET_KEY`
- AI model configurations

### Script Permissions
Ensure scripts are executable:
```bash
chmod +x *.sh
chmod +x *.py
```

### Windows Compatibility
For Windows users:
- Use `.bat` or `.ps1` files
- Ensure PowerShell execution policy allows scripts
- Install required Windows tools (Git Bash, WSL, etc.)

## 🔍 Troubleshooting

### Common Issues

#### Permission Denied
```bash
chmod +x script_name.sh
```

#### Script Not Found
```bash
# Check current directory
pwd
ls -la

# Use absolute paths if needed
/path/to/scripts/script_name.sh
```

#### Python Script Errors
```bash
# Check Python version
python --version

# Install dependencies
pip install -r requirements.txt

# Run with verbose output
python -v script_name.py
```

### Debug Mode
Enable debug output:
```bash
# Shell scripts
bash -x script_name.sh

# Python scripts
python -u script_name.py
```

## 📝 Script Development

### Adding New Scripts
When creating new scripts:
1. Follow naming conventions
2. Add comprehensive help/usage information
3. Include error handling
4. Document dependencies
5. Update this README

### Script Standards
- Use shebang lines for platform-specific scripts
- Include help text and usage examples
- Implement proper error handling
- Use consistent logging format
- Follow shell scripting best practices

## 🆘 Support

For script-related issues:
1. Check script help: `./script_name.sh --help`
2. Review error messages and logs
3. Verify environment configuration
4. Check script permissions and dependencies
5. Contact development team if needed

## 📅 Version Information

- **Last Updated**: December 2024
- **Scripts Version**: 1.0.0
- **Compatibility**: Linux, macOS, Windows
- **Dependencies**: Python 3.8+, Bash 4.0+

---

*These scripts are maintained by the Report AI development team.*
