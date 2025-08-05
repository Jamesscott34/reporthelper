# OpenRoute AI Setup Guide

## Overview

This project now uses OpenRoute AI for document processing and AI-powered breakdowns. OpenRoute AI provides access to multiple AI models through a single API.

## Setup Instructions

### 1. Get OpenRoute API Key

1. Visit [OpenRoute AI](https://openrouter.ai/)
2. Sign up for an account
3. Go to [API Keys](https://openrouter.ai/keys)
4. Create a new API key
5. Copy the API key

### 2. Configure Environment

Create or update your `.env` file with the following:

```env
# Django Configuration
DEBUG=True
SECRET_KEY=django-insecure-development-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# AI Configuration (OpenRoute AI)
OPENROUTE_HOST=https://openrouter.ai/api/v1
OPENROUTE_API_KEY_DEEPSEEK=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
OPENROUTE_API_KEY_TNGTECH=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
OPENROUTE_API_KEY_OPENROUTER=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
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

### 3. Available Models

The project is configured to use these models with their respective API keys:

- **Breakdown Model**: `deepseek/deepseek-r1-0528-qwen3-8b:free` (uses DEEPSEEK API key)
- **Reviewer Model**: `tngtech/deepseek-r1t2-chimera:free` (uses TNGTECH API key)
- **Finalizer Model**: `deepseek/deepseek-r1-0528-qwen3-8b:free` (uses DEEPSEEK API key)
- **Reanalyzer Model**: `openrouter/horizon-beta` (uses OPENROUTER API key)

### 4. Model Performance

- **`deepseek/deepseek-coder-33b-instruct`**: Fast, efficient, great for structured tasks
- **`openai/gpt-4o`**: High quality, excellent reasoning, best for complex analysis

### 5. Testing Configuration

To test your OpenRoute AI configuration:

1. Start the Django server: `python manage.py runserver`
2. Upload a document
3. Check the console for API response messages
4. Verify the breakdown is generated successfully

### 6. Troubleshooting

#### Common Issues

1. **API Key Not Set**
   - Error: "OpenRoute API key not configured"
   - Solution: Add your API key to the `.env` file

2. **Model Not Available**
   - Error: "Model not found"
   - Solution: Check the model name in your `.env` file

3. **Rate Limiting**
   - Error: "Rate limit exceeded"
   - Solution: Check your OpenRoute AI usage limits

4. **Network Issues**
   - Error: "Connection timeout"
   - Solution: Check your internet connection

### 7. Cost Considerations

OpenRoute AI charges based on:
- Model used
- Number of tokens processed
- API calls made

Monitor your usage at: https://openrouter.ai/usage

### 8. Alternative Models

You can change models by updating the `.env` file:

```env
# Alternative models you can use
BREAKDOWN_MODEL=anthropic/claude-3-5-sonnet
REVIEWER_MODEL=openai/gpt-4-turbo
FINALIZER_MODEL=anthropic/claude-3-5-sonnet
REANALYZER_MODEL=openai/gpt-4-turbo
```

## Support

For OpenRoute AI support:
- Documentation: https://openrouter.ai/docs
- Discord: https://discord.gg/openrouter
- Email: support@openrouter.ai 