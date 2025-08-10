# AI Model Management System

This system provides intelligent fallback between different AI models when one fails, ensuring your AI-powered features remain reliable.

## 🚀 Quick Start

### 1. Switch to Premium Models (Most Reliable)
```bash
python switch_model.py premium
```

### 2. Switch to Standard Models (Good Balance)
```bash
python switch_model.py standard
```

### 3. Switch to Free Models (Basic Performance)
```bash
python switch_model.py free
```

### 4. Return to Legacy Models (Current Setup)
```bash
python switch_model.py legacy
```

## 📋 Available Model Presets

### Premium Models (Most Reliable)
- **Breakdown**: `openai/gpt-4o` - Most advanced GPT model
- **Reviewer**: `anthropic/claude-3.5-sonnet` - Excellent reasoning
- **Finalizer**: `openai/gpt-4o-mini` - Reliable, good performance
- **Reanalyzer**: `openai/gpt-4o` - Best analysis capabilities

### Standard Models (Good Balance)
- **Breakdown**: `openai/gpt-3.5-turbo` - Very reliable, cost-effective
- **Reviewer**: `mistralai/mistral-large` - Good reasoning, reliable
- **Finalizer**: `openai/gpt-3.5-turbo` - Very reliable
- **Reanalyzer**: `openai/gpt-3.5-turbo` - Very reliable

### Free Models (Basic Performance)
- **All Tasks**: `mistralai/mistral-small` - Free, basic performance

### Legacy Models (Current Setup)
- **Breakdown**: `deepseek/deepseek-r1-0528-qwen3-8b:free`
- **Reviewer**: `tngtech/deepseek-r1t2-chimera:free`
- **Finalizer**: `deepseek/deepseek-r1-0528-qwen3-8b:free`
- **Reanalyzer**: `openrouter/horizon-beta`

## 🔧 How It Works

### Automatic Fallback
When a model fails, the system automatically tries the next model in the priority list:

1. **Primary Models** (Premium) - Most reliable, highest cost
2. **Secondary Models** (Standard) - Good balance of cost/reliability  
3. **Fallback Models** (Free) - Basic performance, may have issues
4. **Legacy Models** - Current models for backward compatibility

### Model Priority Order
For each task type, models are tried in this order:
1. `openai/gpt-4o` (Premium)
2. `anthropic/claude-3.5-sonnet` (Premium)
3. `openai/gpt-4o-mini` (Premium)
4. `openai/gpt-3.5-turbo` (Standard)
5. `mistralai/mistral-small` (Free)

## 📁 Files Created

### 1. `ai_report_writer/model_config.py`
- Contains all available models organized by reliability
- Provides functions for model selection and fallback
- Defines model metadata and categories

### 2. `ai_report_writer/ai_utils.py`
- `ModelFallbackManager` class for tracking failed models
- `execute_with_fallback()` function for automatic retry
- Performance tracking and best model selection

### 3. `switch_model.py`
- Command-line tool for switching between model presets
- Updates `.env` file automatically
- Creates configuration templates

### 4. `models.txt`
- Human-readable list of all available models
- Organized by category and reliability
- Usage notes and recommendations

### 5. `MODEL_MANAGEMENT_README.md`
- This documentation file

## 🛠️ Usage Examples

### View Available Presets
```bash
python switch_model.py list
```

### Check Current Configuration
```bash
python switch_model.py current
```

### Create Environment Template
```bash
python switch_model.py template
```

### Get Help
```bash
python switch_model.py help
```

## 🔑 Required API Keys

Depending on which models you use, you'll need these API keys:

### For Premium Models
- `OPENAI_API_KEY` - For GPT-4 models
- `ANTHROPIC_API_KEY` - For Claude models
- `GOOGLE_API_KEY` - For Gemini models

### For Standard Models
- `OPENAI_API_KEY` - For GPT-3.5 models
- `OPENROUTE_API_KEY_OPENROUTER` - For other models via OpenRouter

### For Free Models
- `OPENROUTE_API_KEY_OPENROUTER` - For free models via OpenRouter

## 📝 Configuration Files

### Environment Variables (.env)
```bash
# Premium Models
BREAKDOWN_MODEL=openai/gpt-4o
REVIEWER_MODEL=anthropic/claude-3.5-sonnet
FINALIZER_MODEL=openai/gpt-4o-mini
REANALYZER_MODEL=openai/gpt-4o

# API Keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
OPENROUTE_API_KEY_OPENROUTER=your_key_here
```

### Django Settings (ai_report_writer/settings.py)
The system automatically imports the model configuration and uses the most reliable models by default.

## 🚨 Troubleshooting

### Model Not Working
1. **Check API Keys**: Ensure you have the required API keys
2. **Check Model Status**: Some models may be temporarily unavailable
3. **Use Fallback**: The system automatically tries alternative models
4. **Check Logs**: Look for error messages in your application logs

### Performance Issues
1. **Switch to Premium**: Use `python switch_model.py premium`
2. **Check API Limits**: Some models have rate limits
3. **Monitor Costs**: Premium models cost more but are more reliable

### Configuration Issues
1. **Restart Application**: Changes require application restart
2. **Check .env File**: Ensure environment variables are set correctly
3. **Use Template**: Run `python switch_model.py template` to create a proper .env file

## 🔄 Migration from Legacy

### Current Setup
Your system currently uses:
- `deepseek/deepseek-r1-0528-qwen3-8b:free` (Breakdown & Finalizer)
- `tngtech/deepseek-r1t2-chimera:free` (Reviewer)
- `openrouter/horizon-beta` (Reanalyzer)

### Recommended Migration Path
1. **Start with Standard**: `python switch_model.py standard`
2. **Test Performance**: Ensure everything works as expected
3. **Upgrade to Premium**: `python switch_model.py premium` (if budget allows)
4. **Keep Legacy as Backup**: Legacy models remain available as fallbacks

## 📊 Model Performance Tracking

The system automatically tracks:
- Success/failure rates for each model
- Response times and performance metrics
- Best performing models for each task type
- Automatic recovery when models become available again

## 🎯 Best Practices

1. **Start with Standard Models**: Good balance of cost and reliability
2. **Use Premium for Critical Tasks**: When you need maximum reliability
3. **Monitor Performance**: Let the system learn which models work best
4. **Keep API Keys Secure**: Never commit API keys to version control
5. **Test Regularly**: Ensure your chosen models are working properly

## 🆘 Support

If you encounter issues:
1. Check the logs for error messages
2. Verify your API keys are correct
3. Try switching to a different model preset
4. Check if the model service is experiencing outages
5. Use the fallback system - it's designed to handle failures gracefully

## 🔮 Future Enhancements

- **Cost Optimization**: Automatic selection based on cost vs. performance
- **Model Health Monitoring**: Real-time availability checking
- **Custom Model Configurations**: User-defined model preferences
- **Performance Analytics**: Detailed usage and performance reports
- **A/B Testing**: Compare different models for the same tasks
