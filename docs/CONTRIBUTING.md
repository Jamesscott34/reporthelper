# 🤝 Contributing to AI Report Writer

Thank you for your interest in contributing to AI Report Writer! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Process](#-development-process)
- [Pull Request Guidelines](#-pull-request-guidelines)
- [Testing Requirements](#-testing-requirements)
- [Code Style](#-code-style)
- [Documentation](#-documentation)

## 🤗 Code of Conduct

### Our Pledge
We are committed to making participation in this project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards
**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Harassment, discrimination, or derogatory comments
- Publishing others' private information without permission
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Other conduct which could reasonably be considered inappropriate

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Git
- Virtual environment tool
- Basic understanding of Django and REST APIs

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/AI_Report_Writer.git
cd AI_Report_Writer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup pre-commit hooks
make pre-commit

# Run tests to verify setup
python run_tests.py
```

### Project Structure
```
AI_Report_Writer/
├── ai_report_writer/       # Django project settings
├── breakdown/              # Main application
├── docs/                   # Documentation
├── scripts/               # Utility scripts
├── static/                # Static files
├── templates/             # HTML templates
├── tests/                 # Test files
└── requirements.txt       # Dependencies
```

## 🔄 Development Process

### 1. Find or Create an Issue
- Check existing issues for bugs or feature requests
- Create a new issue if none exists
- Discuss the approach before starting work
- Get approval for major changes

### 2. Create a Feature Branch
```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 3. Make Your Changes
- Follow the existing code style and patterns
- Add tests for new functionality
- Update documentation as needed
- Run quality checks frequently

### 4. Test Your Changes
```bash
# Run full test suite
python run_tests.py

# Run code quality checks
make quality

# Test specific functionality
python manage.py test breakdown.tests.TestYourFeature
```

### 5. Commit Your Changes
```bash
# Add changes
git add .

# Commit with descriptive message
git commit -m "feat: add annotation export functionality"
```

## 📝 Pull Request Guidelines

### Before Submitting
- [ ] All tests pass (`python run_tests.py`)
- [ ] Code follows style guidelines (`make quality`)
- [ ] Documentation is updated
- [ ] Commit messages are descriptive
- [ ] Changes are focused and atomic

### PR Template
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or marked as such)
```

### Review Process
1. **Automated Checks**: CI/CD runs tests and quality checks
2. **Code Review**: Maintainers review code and provide feedback
3. **Approval**: At least one maintainer approval required
4. **Merge**: Maintainer merges the PR

## 🧪 Testing Requirements

### Test Coverage
- **Minimum**: 80% code coverage
- **New Features**: 90%+ coverage required
- **Bug Fixes**: Include regression tests

### Test Types
```bash
# Unit tests
python manage.py test breakdown.tests.unit

# Integration tests  
python manage.py test breakdown.tests.integration

# API tests
python manage.py test breakdown.tests.api

# Security tests
python manage.py test breakdown.tests.security
```

### Writing Tests
```python
# Example test structure
from django.test import TestCase
from breakdown.models import Document

class DocumentTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        
    def test_document_creation(self):
        """Test document creation."""
        document = Document.objects.create(
            title="Test Document",
            user=self.user
        )
        self.assertEqual(document.title, "Test Document")
        self.assertEqual(document.user, self.user)
```

## 🎨 Code Style

### Python Style Guide
We follow **PEP 8** with some modifications:
- **Line Length**: 88 characters (Black standard)
- **Import Organization**: isort with Django-aware grouping
- **Docstrings**: Google style docstrings
- **Type Hints**: Encouraged for new code

### Automated Formatting
```bash
# Format code
make format

# Check formatting
make lint

# All quality checks
make quality
```

### Example Code Style
```python
"""Module docstring describing the purpose."""

from typing import List, Optional

from django.db import models
from django.contrib.auth.models import User

from .utils import process_document


class Document(models.Model):
    """Document model for storing uploaded files.
    
    Attributes:
        title: The document title
        user: The user who uploaded the document
        created_at: When the document was created
    """
    
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def process(self) -> Optional[dict]:
        """Process the document with AI.
        
        Returns:
            Processing result dictionary or None if failed.
        """
        try:
            return process_document(self.content)
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return None
```

## 📚 Documentation

### Documentation Types
- **Code Comments**: Explain complex logic
- **Docstrings**: All public functions and classes
- **API Documentation**: OpenAPI/Swagger specs
- **User Guides**: Step-by-step instructions
- **Developer Docs**: Architecture and setup guides

### Writing Guidelines
- **Clear and Concise**: Use simple, direct language
- **Examples**: Include code examples where helpful
- **Up-to-date**: Keep docs synchronized with code changes
- **Accessible**: Consider different skill levels

### Documentation Structure
```python
def process_document(content: str, model: str = "default") -> dict:
    """Process document content with AI model.
    
    Takes raw document content and processes it using the specified
    AI model to generate structured breakdowns and sections.
    
    Args:
        content: Raw document text content
        model: AI model name to use for processing
        
    Returns:
        Dictionary containing:
            - success: Boolean indicating success
            - breakdown: Processed content breakdown
            - sections: List of document sections
            - metadata: Processing metadata
            
    Raises:
        ValueError: If content is empty or invalid
        APIError: If AI service request fails
        
    Example:
        >>> result = process_document("Document content here")
        >>> if result['success']:
        ...     print(result['breakdown'])
    """
```

## 🏷️ Issue Labels

### Priority Labels
- `priority/critical` - Security issues, data loss
- `priority/high` - Important features, major bugs
- `priority/medium` - Standard features and bugs
- `priority/low` - Nice-to-have improvements

### Type Labels
- `type/bug` - Something isn't working
- `type/feature` - New functionality
- `type/enhancement` - Improve existing functionality
- `type/documentation` - Documentation improvements
- `type/security` - Security-related issues

### Status Labels
- `status/needs-triage` - Needs initial review
- `status/ready` - Ready for development
- `status/in-progress` - Currently being worked on
- `status/blocked` - Blocked by external dependency

## 🎯 Contribution Areas

### High-Impact Areas
- **Performance Optimization**: Database queries, caching
- **Security Improvements**: Authentication, validation
- **User Experience**: UI/UX enhancements
- **API Development**: New endpoints, better responses
- **Testing**: Increase coverage, add edge cases

### Good First Issues
Look for issues labeled `good-first-issue`:
- Documentation improvements
- Small bug fixes
- Code cleanup
- Test additions

### Advanced Contributions
- **AI Integration**: New model support, prompt optimization
- **Real-time Features**: WebSocket enhancements
- **Export System**: New formats, templates
- **Analytics**: Usage tracking, reporting
- **Mobile Support**: Responsive design improvements

## 🚀 Release Process

### Version Numbering
We use [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH` (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Schedule
- **Major Releases**: Quarterly
- **Minor Releases**: Monthly
- **Patch Releases**: As needed for critical fixes

## 🙏 Recognition

### Contributors
All contributors are recognized in:
- `CONTRIBUTORS.md` file
- GitHub contributors page
- Release notes for significant contributions

### Maintainer Path
Active contributors may be invited to become maintainers based on:
- Consistent, quality contributions
- Community involvement
- Understanding of project goals
- Demonstrated responsibility

## 📞 Getting Help

### Communication Channels
- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, general discussion
- **Email**: maintainers@ai-report-writer.com
- **Documentation**: Comprehensive guides in `/docs/`

### Response Times
- **Issues**: Within 48 hours
- **Pull Requests**: Within 72 hours
- **Security Issues**: Within 24 hours

---

## 🎉 Thank You!

Every contribution, no matter how small, helps make AI Report Writer better for everyone. We appreciate your time and effort in improving this project.

**Happy Contributing!** 🚀
