# 🔐 GitHub Secrets Configuration Guide

Complete setup guide for configuring GitHub repository secrets to work with the AI Report Writer CI/CD pipeline.

## 🎯 Overview

Your GitHub repository secrets will replace the `.env` file variables in the CI/CD pipeline. This ensures secure handling of sensitive information while maintaining the same variable names for consistency.

## 📋 Required GitHub Secrets

### 🔧 Django Core Configuration

#### `SECRET_KEY`
**Purpose**: Django cryptographic signing key
**Example**: `django-insecure-your-secret-key-here-change-in-production`
**Generate**: Use `python scripts/generate_secret_key.py`

```bash
# Generate a new secret key
python scripts/generate_secret_key.py
```

#### `DEBUG`
**Purpose**: Django debug mode setting
**Values**: `True` (development) / `False` (production)
**Recommendation**: `False` for production secrets

#### `ALLOWED_HOSTS`
**Purpose**: Allowed hostnames for Django
**Example**: `your-domain.com,api.your-domain.com,localhost,127.0.0.1`
**Format**: Comma-separated list without spaces

### 🤖 AI Configuration (OpenRouter)

#### `OPENROUTER_HOST`
**Purpose**: OpenRouter API base URL
**Value**: `https://openrouter.ai/api/v1`
**Note**: Usually constant, but can be customized

#### `OPENROUTER_API_KEY_DEEPSEEK`
**Purpose**: DeepSeek model API key
**Format**: `sk-or-v1-your-deepseek-api-key-here`
**Get Key**: [OpenRouter Keys](https://openrouter.ai/keys)

#### `OPENROUTER_API_KEY_TNGTECH`
**Purpose**: TNG Tech model API key
**Format**: `sk-or-v1-your-tngtech-api-key-here`
**Get Key**: [OpenRouter Keys](https://openrouter.ai/keys)

#### `OPENROUTER_API_KEY_OPENROUTER`
**Purpose**: OpenRouter general API key
**Format**: `sk-or-v1-your-openrouter-api-key-here`
**Get Key**: [OpenRouter Keys](https://openrouter.ai/keys)

### 🤖 AI Model Configuration

#### `BREAKDOWN_MODEL`
**Purpose**: Model for document breakdown
**Default**: `deepseek/deepseek-r1-0528-qwen3-8b:free`
**Options**: Any OpenRouter supported model

#### `REVIEWER_MODEL`
**Purpose**: Model for content review
**Default**: `tngtech/deepseek-r1t2-chimera:free`
**Options**: Any OpenRouter supported model

#### `FINALIZER_MODEL`
**Purpose**: Model for final processing
**Default**: `deepseek/deepseek-r1-0528-qwen3-8b:free`
**Options**: Any OpenRouter supported model

#### `REANALYZER_MODEL`
**Purpose**: Model for re-analysis
**Default**: `openrouter/horizon-beta`
**Options**: Any OpenRouter supported model

### 🗄️ Database Configuration

#### `DATABASE_URL`
**Purpose**: Database connection string
**Examples**:
- SQLite: `sqlite:///db.sqlite3`
- PostgreSQL: `postgresql://user:password@host:port/dbname`
- MySQL: `mysql://user:password@host:port/dbname`

### 📊 Logging Configuration

#### `LOG_LEVEL`
**Purpose**: Application logging level
**Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
**Recommendation**: `INFO` for production

#### `LOG_FILE`
**Purpose**: Log file path
**Default**: `logs/app.log`
**Note**: Relative to project root

## 🔧 How to Set Up GitHub Secrets

### Step 1: Navigate to Repository Settings
1. Go to your GitHub repository
2. Click **Settings** tab
3. In the left sidebar, click **Secrets and variables**
4. Click **Actions**

### Step 2: Add Repository Secrets
For each secret, click **New repository secret** and add:

#### Core Django Secrets
```
Name: SECRET_KEY
Value: django-insecure-your-generated-secret-key-here

Name: DEBUG
Value: False

Name: ALLOWED_HOSTS
Value: your-domain.com,api.your-domain.com,localhost,127.0.0.1
```

#### AI Configuration Secrets
```
Name: OPENROUTER_HOST
Value: https://openrouter.ai/api/v1

Name: OPENROUTER_API_KEY_DEEPSEEK
Value: sk-or-v1-your-deepseek-api-key-here

Name: OPENROUTER_API_KEY_TNGTECH
Value: sk-or-v1-your-tngtech-api-key-here

Name: OPENROUTER_API_KEY_OPENROUTER
Value: sk-or-v1-your-openrouter-api-key-here
```

#### AI Model Configuration
```
Name: BREAKDOWN_MODEL
Value: deepseek/deepseek-r1-0528-qwen3-8b:free

Name: REVIEWER_MODEL
Value: tngtech/deepseek-r1t2-chimera:free

Name: FINALIZER_MODEL
Value: deepseek/deepseek-r1-0528-qwen3-8b:free

Name: REANALYZER_MODEL
Value: openrouter/horizon-beta
```

#### Database Configuration
```
Name: DATABASE_URL
Value: postgresql://user:password@host:port/dbname
```

#### Logging Configuration
```
Name: LOG_LEVEL
Value: INFO

Name: LOG_FILE
Value: logs/app.log
```

## 🌍 Environment-Specific Secrets

### Production Environment
Create these additional secrets for production:

```
Name: PRODUCTION_DATABASE_URL
Value: postgresql://prod_user:prod_pass@prod_host:5432/prod_db

Name: PRODUCTION_ALLOWED_HOSTS
Value: your-production-domain.com,api.your-production-domain.com

Name: PRODUCTION_SECRET_KEY
Value: your-super-secure-production-secret-key
```

### Staging Environment
Create these for staging environment:

```
Name: STAGING_DATABASE_URL
Value: postgresql://staging_user:staging_pass@staging_host:5432/staging_db

Name: STAGING_ALLOWED_HOSTS
Value: staging.your-domain.com,staging-api.your-domain.com

Name: STAGING_SECRET_KEY
Value: your-staging-secret-key
```

## 📋 Complete Secrets Checklist

Use this checklist to ensure all secrets are configured:

### ✅ Core Django Configuration
- [ ] `SECRET_KEY` - Django cryptographic key
- [ ] `DEBUG` - Debug mode setting
- [ ] `ALLOWED_HOSTS` - Allowed hostnames

### ✅ AI Configuration
- [ ] `OPENROUTER_HOST` - OpenRouter API URL
- [ ] `OPENROUTER_API_KEY_DEEPSEEK` - DeepSeek API key
- [ ] `OPENROUTER_API_KEY_TNGTECH` - TNG Tech API key
- [ ] `OPENROUTER_API_KEY_OPENROUTER` - OpenRouter API key

### ✅ AI Models
- [ ] `BREAKDOWN_MODEL` - Document breakdown model
- [ ] `REVIEWER_MODEL` - Content review model
- [ ] `FINALIZER_MODEL` - Final processing model
- [ ] `REANALYZER_MODEL` - Re-analysis model

### ✅ Database & Logging
- [ ] `DATABASE_URL` - Database connection string
- [ ] `LOG_LEVEL` - Logging level
- [ ] `LOG_FILE` - Log file path

### ✅ Optional Environment-Specific
- [ ] `PRODUCTION_*` secrets (if using production environment)
- [ ] `STAGING_*` secrets (if using staging environment)

## 🔒 Security Best Practices

### Secret Management
1. **🔐 Never commit secrets** to version control
2. **🔄 Rotate keys regularly** - Update API keys periodically
3. **🎯 Use least privilege** - Only grant necessary permissions
4. **📊 Monitor usage** - Track API key usage and costs
5. **🚨 Alert on changes** - Set up notifications for secret changes

### API Key Security
1. **💰 Set spending limits** on OpenRouter account
2. **📊 Monitor usage** regularly
3. **🔒 Use different keys** for different environments
4. **⏰ Set expiration dates** where possible
5. **🚫 Revoke unused keys** immediately

### Database Security
1. **🔐 Use strong passwords** for database connections
2. **🌍 Restrict network access** to database servers
3. **🔄 Regular backups** with encryption
4. **📊 Monitor connections** and query patterns
5. **🔧 Keep database updated** with security patches

## 🧪 Testing Secrets Configuration

### Local Testing
Create a `.env.test` file for local testing:

```bash
# .env.test - DO NOT COMMIT
DEBUG=True
SECRET_KEY=django-test-key-only-for-local-testing
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
DATABASE_URL=sqlite:///test_db.sqlite3

# Test AI keys (use test/free tier keys)
OPENROUTER_HOST=https://openrouter.ai/api/v1
OPENROUTER_API_KEY_DEEPSEEK=test-key-deepseek
OPENROUTER_API_KEY_TNGTECH=test-key-tngtech
OPENROUTER_API_KEY_OPENROUTER=test-key-openrouter

# Test models (use free tier)
BREAKDOWN_MODEL=deepseek/deepseek-r1-0528-qwen3-8b:free
REVIEWER_MODEL=tngtech/deepseek-r1t2-chimera:free
FINALIZER_MODEL=deepseek/deepseek-r1-0528-qwen3-8b:free
REANALYZER_MODEL=openrouter/horizon-beta

LOG_LEVEL=DEBUG
LOG_FILE=logs/test.log
```

### Workflow Testing
Test your secrets configuration:

1. **🧪 Manual Workflow Run**: Use "Run workflow" to test
2. **🔍 Check Logs**: Verify secrets are loaded correctly
3. **📊 Monitor API Usage**: Ensure API keys work
4. **🗄️ Database Connection**: Verify database connectivity

## 🚨 Troubleshooting

### Common Issues

#### Secret Not Found
```
Error: Secret 'SECRET_KEY' not found
```
**Solution**: Verify secret name matches exactly (case-sensitive)

#### Invalid API Key
```
Error: Invalid OpenRouter API key
```
**Solution**: 
- Check API key format (`sk-or-v1-...`)
- Verify key is active on OpenRouter
- Check spending limits

#### Database Connection Failed
```
Error: Database connection failed
```
**Solution**:
- Verify DATABASE_URL format
- Check database server accessibility
- Validate credentials

#### Workflow Permission Denied
```
Error: Permission denied accessing secrets
```
**Solution**:
- Check repository permissions
- Verify you're an admin/maintainer
- Check organization settings

### Debug Commands

#### Test Secret Loading
Add this to workflow for debugging:
```yaml
- name: 🔍 Debug Secrets
  run: |
    echo "SECRET_KEY length: ${#SECRET_KEY}"
    echo "DEBUG: $DEBUG"
    echo "ALLOWED_HOSTS: $ALLOWED_HOSTS"
    # Never echo actual secret values!
```

#### Test API Connectivity
```yaml
- name: 🧪 Test API Keys
  run: |
    python -c "
    import os
    import requests
    
    api_key = os.getenv('OPENROUTER_API_KEY_DEEPSEEK')
    if api_key and api_key.startswith('sk-or-v1-'):
        print('✅ API key format valid')
    else:
        print('❌ API key format invalid')
    "
```

## 📞 Getting Help

### Resources
- **📚 GitHub Secrets Documentation**: [GitHub Docs](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- **🔑 OpenRouter API Keys**: [OpenRouter Keys](https://openrouter.ai/keys)
- **🛠️ Django Secret Key Generator**: `python scripts/generate_secret_key.py`

### Support Channels
- **🐛 Issues**: Create GitHub issue for problems
- **💬 Discussions**: Use GitHub Discussions for questions
- **📖 Documentation**: Check other docs in `/docs/` folder

---

**🔐 Keep your secrets secure!** Never share API keys or commit them to version control. Use GitHub secrets for all sensitive configuration data.
