# 🤖 AI Report Writer

A comprehensive Django-based AI document assistant platform that transforms documents into structured, step-by-step reports using local AI models via LM Studio.

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

1. **🧠 AI 1 – Breakdown AI** (`deepseek-r1-distill-qwen-7b`)
   - Converts raw document text into step-by-step bullet point instructions
   - Uses structured prompts for consistent output

2. **👓 AI 2 – Reviewer AI** (`whiterabbitneo-2.5-qwen-2.5-coder-7b`)
   - Provides multiple reviewer perspectives (academic, technical, casual)
   - Gives feedback and suggestions on breakdowns

3. **🧹 AI 3 – Finalizer AI** (`llama-3-8b-gpt-40-ru1.0`)
   - Rewrites breakdowns into human-sounding, professional reports
   - Ensures natural language flow and readability

4. **🧪 AI 4 – Re-analyzer AI** (`h2o-danube2-1.8b-chat`) *(Optional)*
   - Analyzes and optimizes existing breakdowns
   - Suggests improvements and simplifications

### Tech Stack

- **Backend**: Django 4.2.23 (Python)
- **AI**: LM Studio (local AI models)
- **Frontend**: HTML, CSS, JavaScript (Bootstrap 5)
- **Database**: SQLite (default), PostgreSQL (optional)
- **File Processing**: python-docx, PyPDF2
- **Background Tasks**: Celery + Redis (optional)

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- LM Studio (with compatible models)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Report_AI
   ```

2. **Run the enhanced setup script**
   ```bash
   # Make setup script executable
   chmod +x setup.sh
   
   # Run setup (handles everything automatically)
   ./setup.sh
   ```

3. **Start the services**
   ```bash
   # Start LM Studio
   ./scripts/start_llmstudio.sh
   
   # Start Django (in another terminal)
   ./scripts/start_django.sh
   ```

4. **Access the application**
   - Open: http://127.0.0.1:8000
   - Admin: http://127.0.0.1:8000/admin (admin/admin123)

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
│   ├── start_llmstudio.sh   # LM Studio startup
│   ├── start_django.sh      # Django startup
│   ├── check_status.sh      # System health check
│   ├── backup.sh            # Backup system
│   └── update.sh            # Automatic updates
├── Studio/                   # LM Studio AppImage
├── assets/                   # Local AI assets
├── java_assets/             # Java files for DOCX/PDF generation
├── backups/                 # Automatic backups
├── setup.sh                 # Enhanced setup script
├── .version                 # Version tracking
└── requirements.txt         # Python dependencies
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# AI Configuration (LM Studio)
OLLAMA_HOST=http://192.168.0.34:1234
BREAKDOWN_MODEL=deepseek-r1-distill-qwen-7b
REVIEWER_MODEL=whiterabbitneo-2.5-qwen-2.5-coder-7b
FINALIZER_MODEL=llama-3-8b-gpt-40-ru1.0
REANALYZER_MODEL=h2o-danube2-1.8b-chat

# Optional: Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### LM Studio Setup

1. **Load Models**: Open LM Studio and load your models:
   - `deepseek-r1-distill-qwen-7b`
   - `whiterabbitneo-2.5-qwen-2.5-coder-7b`
   - `llama-3-8b-gpt-40-ru1.0`
   - `h2o-danube2-1.8b-chat`

2. **Start Local Server**: In LM Studio:
   - Go to "Local Server" tab
   - Click "Start Server"
   - Ensure it's running on `http://192.168.0.34:1234`

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
5. **Test**: Verify with sample documents

### Adding New AI Models

1. **Update Settings**: Add model to `OLLAMA_MODELS` in `settings.py`
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
# - LM Studio status
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

1. **LM Studio Not Responding**
   - Ensure LM Studio is running
   - Check if local server is started
   - Verify API endpoint: http://192.168.0.34:1234

2. **Model Not Found**
   - Load models in LM Studio
   - Check model names in settings
   - Verify model compatibility

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
- **Network**: Internet for initial setup

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

**Made with ❤️ using Django and LM Studio**

*Last updated: Version 1.0.0 - Automatic update system included*
