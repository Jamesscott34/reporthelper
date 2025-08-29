# 🚀 Getting Started with AI Report Writer

Welcome to AI Report Writer! This guide will walk you through your first document processing experience and help you understand the platform's core features.

## 📋 Prerequisites

Before you begin, ensure you have:
- ✅ Python 3.9+ installed
- ✅ Git installed
- ✅ A text editor or IDE
- ✅ OpenRouter API key (for AI processing)

## 🏁 Quick Setup

### 1. Clone and Install
```bash
# Clone the repository
git clone https://github.com/yourusername/AI_Report_Writer.git
cd AI_Report_Writer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
OPENROUTER_API_KEY=your-api-key-here
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 3. Initialize Database
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user (optional)
python manage.py createsuperuser
```

### 4. Start the Server
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application!

## 🎯 Your First Document

### Step 1: Upload a Document
1. Navigate to `http://localhost:8000/upload/`
2. Click "Choose File" and select a PDF or DOCX document
3. Click "Upload and Process"
4. Wait for the AI processing to complete

### Step 2: Review the Breakdown
1. After processing, you'll see the document breakdown
2. The AI will have converted your document into structured steps
3. Review each section for accuracy and completeness

### Step 3: Add Annotations
1. Highlight any text in the breakdown
2. Click "Add Annotation" in the popup
3. Choose annotation type (note, question, improvement)
4. Add your comments and save

### Step 4: Export Your Report
1. Click "Export" in the top menu
2. Choose your preferred format (DOCX or PDF)
3. Download and review your processed document

## 🔧 Key Features Overview

### Document Processing
- **Supported Formats**: PDF, DOCX, DOC, TXT
- **AI Models**: Multiple OpenRouter models for different tasks
- **Processing Time**: Typically 2-5 seconds per page
- **Quality**: Professional-grade text extraction

### Annotation System
- **Real-time Collaboration**: Multiple users can annotate simultaneously
- **Annotation Types**: Notes, questions, improvements, highlights
- **Context Preservation**: Annotations link to specific document sections
- **Export Integration**: Annotations included in final reports

### User Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Mode**: Automatic theme switching
- **Keyboard Shortcuts**: Efficient navigation and editing
- **Progress Indicators**: Clear feedback during processing

## 🛠️ Common Tasks

### Changing AI Models
```bash
# List available models
python scripts/switch_model.py --list

# Switch to a different model
python scripts/switch_model.py --model "openai/gpt-4"
```

### Running Tests
```bash
# Full test suite
python run_tests.py

# Quick tests only
python run_tests.py --fast

# With coverage report
python run_tests.py --coverage
```

### Development Mode
```bash
# Enable debug mode
export DEBUG=True

# Run with auto-reload
python manage.py runserver --settings=ai_report_writer.settings_dev
```

## 🚨 Troubleshooting

### Common Issues

#### "ModuleNotFoundError"
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### "API Key Invalid"
1. Check your `.env` file has the correct `OPENROUTER_API_KEY`
2. Verify the key is active at https://openrouter.ai/
3. Ensure no extra spaces or quotes around the key

#### "Database Locked"
```bash
# Reset database (WARNING: loses data)
rm db.sqlite3
python manage.py migrate
```

#### "Port Already in Use"
```bash
# Use different port
python manage.py runserver 8001

# Or find and kill the process
lsof -ti:8000 | xargs kill  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

### Getting Help

1. **Check Logs**: Look in the console output for error messages
2. **Test API**: Use `python run_tests.py` to verify setup
3. **Documentation**: Review [docs/](../docs/) for detailed guides
4. **Issues**: Create a GitHub issue with error details
5. **Community**: Join discussions for community support

## 📚 Next Steps

### Learn More
- **[API Reference](API_REFERENCE.md)**: Complete API documentation
- **[Security Guide](SECURITY.md)**: Security best practices
- **[Development Setup](DEVELOPMENT_SETUP.md)**: Advanced development configuration

### Customize Your Setup
- **Models**: Configure different AI models for specific tasks
- **Templates**: Create custom document templates
- **Integrations**: Connect with external services
- **Themes**: Customize the user interface

### Join the Community
- **GitHub**: Star the repository and watch for updates
- **Discussions**: Share ideas and get help from other users
- **Contributing**: Help improve the platform for everyone

---

**🎉 Congratulations! You're now ready to transform documents with AI Report Writer.**

*Need help? Check our [troubleshooting guide](#-troubleshooting) or create an issue on GitHub.*
