# 🚀 Quick GitHub Secrets Setup

**Copy-paste ready configuration for your GitHub repository secrets**

## 🔧 GitHub Repository Settings Path
1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
2. Click **"New repository secret"** for each item below

## 📋 Required Secrets (Copy these names exactly)

### Core Django Configuration
```
Name: SECRET_KEY
Value: [Generate with: python scripts/generate_secret_key.py]

Name: DEBUG
Value: False

Name: ALLOWED_HOSTS
Value: localhost,127.0.0.1,your-domain.com
```

### AI Configuration
```
Name: OPENROUTER_HOST
Value: https://openrouter.ai/api/v1



Name: OPENROUTER_API_KEY_OPENROUTER
Value: sk-or-v1-[your-openrouter-key-from-openrouter.ai]
```

### AI Models
```
Name: BREAKDOWN_MODEL
Value: model

Name: REVIEWER_MODEL
Value: model

Name: FINALIZER_MODEL
Value: model

Name: REANALYZER_MODEL
Value: model
```

### Database & Logging
```
Name: DATABASE_URL
Value: sqlite:///db.sqlite3

Name: LOG_LEVEL
Value: INFO

Name: LOG_FILE
Value: logs/app.log
```

## 🔑 Get Your API Key
1. Visit: https://openrouter.ai/keys
2. Create account if needed
3. Generate one OpenRouter API key
4. Copy key that starts with `sk-or-v1-`

## ✅ Verification Checklist
- [ ] All 9 secrets added to GitHub
- [ ] API key starts with `sk-or-v1-`
- [ ] No spaces in ALLOWED_HOSTS
- [ ] SECRET_KEY is long and random
- [ ] DATABASE_URL matches your database type

## 🧪 Test Your Setup
After adding secrets, trigger the workflow:
1. Go to **Actions** tab
2. Select **"AI Report Writer CI/CD Pipeline"**
3. Click **"Run workflow"**
4. Choose **staging** environment
5. Click **"Run workflow"** button

**✅ Your secrets are now configured and ready for the CI/CD pipeline!**
