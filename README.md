# 🤖 AI Report Writer

A comprehensive Django-based AI document assistant platform that transforms documents into structured, step-by-step reports using OpenRoute AI models.

## 🎯 Overview

AI Report Writer is a modular platform that:

- **Accepts** PDF, DOCX, DOC, and TXT documents
- **Extracts** text content automatically
- **Breaks down** documents into structured, step-by-step instructions using AI
- **Allows** interactive review and editing of breakdowns
- **Generates** final reports in human-readable format
- **Exports** results as DOCX and PDF files
- **Automatically updates** with new features and improvements

## 🏗️ Architecture

### AI Agents Pipeline

1. **🧠 AI 1 – Breakdown AI** (`deepseek/deepseek-r1-0528-qwen3-8b:free`)
   - Converts raw document text into step-by-step bullet point instructions
   - Uses structured prompts for consistent output
   - **API Key**: DeepSeek (sk-or-v1-...)

2. **👓 AI 2 – Reviewer AI** (`tngtech/deepseek-r1t2-chimera:free`)
   - Provides multiple reviewer perspectives (academic, technical, casual)
   - Gives feedback and suggestions on breakdowns
   - **API Key**: TNGTech (sk-or-v1-...)

3. **🧹 AI 3 – Finalizer AI** (`deepseek/deepseek-r1-0528-qwen3-8b:free`)
   - Rewrites breakdowns into human-sounding, professional reports
   - Ensures natural language flow and readability
   - **API Key**: DeepSeek (sk-or-v1-...)

4. **🧪 AI 4 – Re-analyzer AI** (`openrouter/horizon-beta`) *(Optional)*
   - Analyzes and optimizes existing breakdowns
   - Suggests improvements and simplifications
   - **API Key**: OpenRouter (sk-or-v1-...)

### Tech Stack

- **Backend**: Django 4.2.23 (Python)
- **AI**: OpenRoute AI (cloud-based AI models)
- **Frontend**: HTML, CSS, JavaScript (Bootstrap 5)
- **Database**: SQLite (default), PostgreSQL (optional)
- **File Processing**: python-docx, PyPDF2
- **Background Tasks**: Celery + Redis (optional)

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenRoute AI API keys
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Report_AI
   ```

2. **Create `.env` file** from the template (see Configuration section below)
   ```bash
   cp env.example .env
   # Edit .env with your API keys and settings
   ```

3. **Run the enhanced setup script**
   ```bash
   # Make setup script executable
   chmod +x scripts/setup.sh
   
   # Run setup (handles everything automatically)
   ./scripts/setup.sh
   ```

4. **Automatic Startup Features**
   The setup script now automatically:
   - ✅ Starts Django server
   - ✅ Applies any updates
   - ✅ Runs health checks
   - ✅ Displays status dashboard

5. **Access the application**
   - Open: http://127.0.0.1:8000
   - Admin: http://127.0.0.1:8000/admin (admin/admin123)

### Manual Startup (if needed)

If you need to start services manually:

```bash
# Start Django (in another terminal)
./scripts/start_django.sh

# Check status
./scripts/status.sh
```

## 📁 Project Structure

```
Report_AI/
├── 📁 ai_report_writer/          # Main Django application
├── 📁 breakdown/                  # Document breakdown functionality
├── 📁 comparison_ai/              # AI comparison features
├── 📁 creation/                   # Document creation tools
├── 📁 user_review/                # User review system
├── 📁 breakdown_review/           # Breakdown review functionality
├── 📁 prompts/                    # AI prompt templates
├── 📁 static/                     # Static files (CSS, JS, images)
├── 📁 templates/                  # HTML templates
├── 📁 media/                      # User uploaded files
├── 📁 java_assets/                # Java document generator
├── 📁 docs/                       # Documentation files
│   ├── DOCUMENT_GENERATION_README.md
│   ├── MODEL_MANAGEMENT_README.md
│   ├── WINDOWS_SETUP.md
│   └── OPENROUTE_SETUP.md
├── 📁 scripts/                    # Utility and startup scripts
│   ├── start.sh                   # Main startup script
│   ├── start.bat                  # Windows startup script
│   ├── start_simple.ps1           # PowerShell startup script
│   ├── switch_model.py            # AI model switcher
│   ├── start_django.sh            # Django server starter
│   ├── status.sh                  # System status checker
│   └── ...                        # Other utility scripts
├── 📄 README.md                   # This file
├── 📄 requirements.txt            # Python dependencies
├── 📄 manage.py                   # Django management
├── 📄 env.example                 # Environment configuration template
└── 📄 .env                        # Environment configuration (create from template)
```

## 🔄 Automatic Updates

The project includes an intelligent update system that automatically detects and applies new features:

### Update System Features

- **Version Tracking**: Automatically tracks project versions
- **Dependency Updates**: Updates Python packages and requirements
- **Database Migrations**: Applies new database schema changes
- **New Apps Detection**: Creates missing Django apps
- **Configuration Updates**: Updates settings and configurations
- **Health Checks**: Validates system health after updates
- **Automatic Backups**: Creates backups before updates

### Update Commands

```bash
# Check current status
./scripts/check_status.sh

# Run automatic update
./scripts/update.sh

# Create backup
./scripts/backup.sh

# Full setup/update
./setup.sh
```

### Update Process

1. **Version Check**: Compares current version with stored version
2. **Backup**: Creates backup before making changes
3. **Dependency Update**: Updates all Python packages
4. **App Detection**: Checks for new Django apps
5. **Migration**: Applies database migrations
6. **Configuration**: Updates settings and configs
7. **Health Check**: Validates system health
8. **Version Save**: Saves new version number

## 📁 Project Structure

```
ai_report_writer/
├── ai_report_writer/          # Django project settings
├── breakdown/                 # Document upload and AI breakdown
│   ├── models.py             # Document and Breakdown models
│   ├── views.py              # Upload and processing views
│   ├── ai_breakdown.py       # AI service for breakdowns
│   └── utils.py              # Text extraction utilities
├── user_review/              # Interactive breakdown review
├── breakdown_review/         # AI reviewer functionality
├── creation/                 # Final report generation
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   └── breakdown/           # Breakdown app templates
├── static/                   # CSS, JS, images
├── scripts/                  # Startup and utility scripts
│   ├── start_django.sh      # Django startup
│   ├── check_status.sh      # System health check
│   ├── status.sh            # Quick status dashboard
│   ├── backup.sh            # Backup system
│   ├── update.sh            # Automatic updates
│   └── generate_secret_key.py # Secure key generator
├── assets/                   # Local AI assets
├── java_assets/             # Java files for DOCX/PDF generation
├── backups/                 # Automatic backups
├── setup.sh                 # Enhanced setup script
├── .version                 # Version tracking
└── requirements.txt         # Python dependencies
```

## 🔧 Configuration

### Environment Variables Setup

The project uses environment variables for configuration. We provide two files to help you set this up:

1. **`.env.example`** - Template showing all available configuration options
2. **`.env`** - Your actual configuration file (create this from the template)

#### Quick Setup

1. **Copy the template**:
   ```bash
   cp env.example .env
   ```

2. **Edit `.env`** with your actual values:
   ```bash
   # Edit the file with your API keys and settings
   nano .env
   ```

#### Environment Variables (.env)

Create a `.env` file in the project root with the following layout:

```env
# Django Configuration
DEBUG=True
SECRET_KEY=django-insecure-development-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# AI Configuration (OpenRoute AI)
OPENROUTE_HOST=https://openrouter.ai/api/v1
OPENROUTE_API_KEY_DEEPSEEK=apikey
OPENROUTE_API_KEY_TNGTECH=apikey
OPENROUTE_API_KEY_OPENROUTER=apikey
BREAKDOWN_MODEL=deepseek/deepseek-r1-0528-qwen3-8b:free
REVIEWER_MODEL=tngtech/deepseek-r1t2-chimera:free
FINALIZER_MODEL=deepseek/deepseek-r1-0528-qwen3-8b:free
REANALYZER_MODEL=openrouter/horizon-beta

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

#### View .env.example

The `.env.example` file contains comprehensive configuration options including:

- **Core Django Settings**: Debug, secret key, allowed hosts
- **AI Model Configuration**: Multiple providers (OpenAI, Anthropic, OpenRoute, LM Studio, Local)
- **Database Options**: SQLite, PostgreSQL, MySQL configurations
- **Optional Services**: Email, Redis, Celery, logging
- **Security Settings**: CSRF, CORS, SSL configurations
- **File Upload Settings**: Size limits, allowed types
- **Advanced Features**: Backup, monitoring, third-party integrations

To view all available options:
```bash
# View the complete template
cat env.example

# Or open in your editor
code env.example
```

### API Key Setup

1. **Get OpenRoute AI API Keys**:
   - Visit [OpenRoute AI](https://openrouter.ai/)
   - Sign up for an account
   - Navigate to API Keys section
   - Create API keys for each model provider:
     - **DeepSeek**: For `deepseek/deepseek-r1-0528-qwen3-8b:free`
     - **TNGTech**: For `tngtech/deepseek-r1t2-chimera:free`
     - **OpenRouter**: For `openrouter/horizon-beta`

2. **Add API Keys to .env**:
   - Replace `sk-or-v1-your-deepseek-api-key-here` with your actual DeepSeek API key
   - Replace `sk-or-v1-your-tngtech-api-key-here` with your actual TNGTech API key
   - Replace `sk-or-v1-your-openrouter-api-key-here` with your actual OpenRouter API key

3. **Model Configuration**:
   - Each model is automatically assigned to the correct API key based on the model name
   - DeepSeek models use the `OPENROUTE_API_KEY_DEEPSEEK`
   - TNGTech models use the `OPENROUTE_API_KEY_TNGTECH`
   - OpenRouter models use the `OPENROUTE_API_KEY_OPENROUTER`


```

## 📖 Usage

### Web Interface

1. **Upload Document**
   - Navigate to http://127.0.0.1:8000
   - Click "Upload Document"
   - Select PDF, DOCX, DOC, or TXT file
   - Wait for AI processing

2. **Review Breakdown**
   - View AI-generated breakdown
   - Edit sections if needed
   - Regenerate breakdown if desired

3. **Generate Report**
   - Review AI feedback
   - Generate final report
   - Export as DOCX or PDF

### Command Line

```bash
# Process a document via CLI
python manage.py run_report --input document.pdf --output report.docx

# Run specific AI tasks
python manage.py breakdown_document --file document.pdf
python manage.py review_breakdown --breakdown_id 1
python manage.py finalize_report --breakdown_id 1
```

## 🔄 Workflow

### Document Processing Pipeline

```
User Upload → Text Extraction → AI Breakdown → User Review → AI Review → Final Report → Export
     ↓              ↓              ↓              ↓            ↓            ↓           ↓
   PDF/DOCX    →  Raw Text   →  Structured   →  Editable   →  Feedback  →  Report   →  DOCX/PDF
```

### AI Agent Interaction

1. **Document Upload**: User uploads document
2. **Text Extraction**: System extracts text content
3. **AI Breakdown**: AI 1 creates step-by-step breakdown
4. **User Review**: User can edit and refine breakdown
5. **AI Review**: AI 2 provides multiple perspectives
6. **Final Report**: AI 3 generates human-readable report
7. **Export**: System creates DOCX and PDF files

## 🛠️ Development

### Running Tests

```bash
python manage.py test
```

### Adding New Features

1. **Update Version**: Increment version in `setup.sh` and `scripts/update.sh`
2. **Add Dependencies**: Update `requirements.txt`
3. **Create Migrations**: Run `python manage.py makemigrations`
4. **Update Scripts**: Add new functionality to update scripts
5. **Update Environment Template**: Add new variables to `env.example`
6. **Test**: Verify with sample documents

### Environment File Management

When adding new configuration options:

1. **Add to `env.example`**: Include the new variable with a descriptive comment
2. **Update README**: Document the new configuration option
3. **Set Defaults**: Provide sensible default values in the template
4. **Documentation**: Add usage examples and requirements

Example of adding a new environment variable:
```bash
# In env.example
# New Feature Configuration
NEW_FEATURE_ENABLED=True
NEW_FEATURE_API_KEY=your-api-key-here
```

### Adding New AI Models

1. **Update Settings**: Add model to `OPENROUTE_MODELS` in `settings.py`
2. **Create Service**: Add new AI service class
3. **Update Views**: Integrate new AI functionality
4. **Test**: Verify with sample documents

### Customizing Prompts

Edit prompt templates in:
- `breakdown/ai_breakdown.py` - Breakdown prompts
- `breakdown_review/reviewer.py` - Review prompts
- `creation/finalizer.py` - Finalization prompts

## 🔧 Maintenance

### System Health Check

```bash
# Check system status
./scripts/check_status.sh

# Output includes:
# - Virtual environment status
# - Django installation
# - Database connection
# - OpenRoute AI status
# - File permissions
# - Dependencies
```

### Backup and Restore

```bash
# Create backup
./scripts/backup.sh

# Restore from backup
tar -xzf backups/ai_report_writer_backup_YYYYMMDD_HHMMSS.tar.gz
./setup.sh
```

### Automatic Updates

```bash
# Check for updates
./scripts/update.sh

# Force full setup
./setup.sh
```

## 🐛 Troubleshooting

### Common Issues

1. **OpenRoute AI Not Responding**
   - Ensure API keys are correctly set in `.env`
   - Check if API keys are valid and have sufficient credits
   - Verify API endpoint: https://openrouter.ai/api/v1
   - **Tip**: Use `cat env.example` to see all available configuration options

2. **Configuration Issues**
   - Verify `.env` file exists and is properly formatted
   - Check that all required variables are set
   - Compare with `env.example` template for missing variables
   - Ensure no extra spaces or quotes around values

2. **Model Not Found**
   - Check model names in `.env` file
   - Verify model availability on OpenRoute AI
   - Ensure correct API key is assigned to model

3. **File Upload Issues**
   - Check file size (max 50MB)
   - Verify file format (PDF, DOCX, DOC, TXT)
   - Ensure proper permissions

4. **Update Issues**
   - Run `./scripts/check_status.sh` to diagnose
   - Check logs for specific errors
   - Try `./setup.sh` for full reset

### Django Security Warnings

When running `python manage.py check --deploy`, you may see security warnings. These are **normal for development** and indicate security best practices for production:

#### Common Warnings and Solutions:

1. **SECRET_KEY Warning** (`security.W009`)
   - **Issue**: Using default Django secret key
   - **Solution**: Generate a secure key:
     ```bash
     # Generate secure secret key
     python scripts/generate_secret_key.py
     # Add to .env file: SECRET_KEY=your-generated-key
     ```

2. **DEBUG Warning** (`security.W018`)
   - **Issue**: DEBUG=True in production
   - **Solution**: Set `DEBUG=False` in production
     ```bash
     # In .env file for production
     DEBUG=False
     ```

3. **HTTPS Warnings** (`security.W004`, `security.W008`, `security.W012`, `security.W016`)
   - **Issue**: Missing HTTPS/SSL settings
   - **Solution**: These are automatically handled by the settings.py file
   - **Development**: Warnings are suppressed when DEBUG=True
   - **Production**: Settings are automatically enabled when DEBUG=False

#### Development vs Production:

- **Development** (`DEBUG=True`): Warnings are informational only
- **Production** (`DEBUG=False`): Security settings are automatically enabled

#### Quick Fix for Development:

If you want to suppress warnings during development, you can run:
```bash
# Check without deployment warnings
python manage.py check

# Or run with specific checks
python manage.py check --deploy --fail-level WARNING
```

### Debug Mode

Enable debug mode in `.env`:
```env
DEBUG=True
```

### System Requirements

- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 2GB free space
- **Network**: Internet for OpenRoute AI API access

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Update version numbers
5. Add tests
6. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation
- Run `./scripts/check_status.sh` for diagnostics

---


*Last updated: Version 1.0.0 - Automatic update system included*
