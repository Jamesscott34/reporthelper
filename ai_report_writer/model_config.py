"""
AI Model Configuration for OpenRouter
This file contains all available models organized by reliability and
performance. The system will automatically try models in order of preference.
"""

# Primary Models (Most Reliable)
PRIMARY_MODELS = {
    'breakdown': [
        'openai/gpt-4o',  # Very reliable, excellent performance
        'anthropic/claude-3.5-sonnet',  # Very reliable, great reasoning
        'openai/gpt-4o-mini',  # Reliable, good performance
        'google/gemini-2.5-pro',  # Good performance, reliable
        'anthropic/claude-3.5-haiku',  # Fast and reliable
    ],
    'reviewer': [
        'openai/gpt-4o',  # Best for review tasks
        'anthropic/claude-3.5-sonnet',  # Excellent reasoning
        'openai/gpt-4o-mini',  # Good alternative
        'google/gemini-2.5-pro',  # Reliable alternative
        'mistralai/mistral-large',  # Good reasoning
    ],
    'finalizer': [
        'openai/gpt-4o',  # Best for finalization
        'anthropic/claude-3.5-sonnet',  # Excellent quality
        'openai/gpt-4o-mini',  # Good alternative
        'google/gemini-2.5-pro',  # Reliable alternative
        'anthropic/claude-3.5-haiku',  # Fast alternative
    ],
    'reanalyzer': [
        'openai/gpt-4o',  # Best for reanalysis
        'anthropic/claude-3.5-sonnet',  # Excellent reasoning
        'openai/gpt-4o-mini',  # Good alternative
        'google/gemini-2.5-pro',  # Reliable alternative
        'mistralai/mistral-large',  # Good alternative
    ]
}

# Secondary Models (Good Performance, More Reliable)
SECONDARY_MODELS = {
    'breakdown': [
        'openai/gpt-3.5-turbo',  # Very reliable, good performance
        'mistralai/mistral-large',  # Reliable, good reasoning
        'anthropic/claude-3-haiku',  # Fast and reliable
        'google/gemini-2.0-flash',  # Good performance
        'cohere/command-r-plus',  # Reliable alternative
    ],
    'reviewer': [
        'openai/gpt-3.5-turbo',  # Very reliable
        'mistralai/mistral-large',  # Good reasoning
        'anthropic/claude-3-haiku',  # Fast alternative
        'google/gemini-2.0-flash',  # Good alternative
        'cohere/command-r-plus',  # Reliable alternative
    ],
    'finalizer': [
        'openai/gpt-3.5-turbo',  # Very reliable
        'mistralai/mistral-large',  # Good quality
        'anthropic/claude-3-haiku',  # Fast alternative
        'google/gemini-2.0-flash',  # Good alternative
        'cohere/command-r-plus',  # Reliable alternative
    ],
    'reanalyzer': [
        'openai/gpt-3.5-turbo',  # Very reliable
        'mistralai/mistral-large',  # Good reasoning
        'anthropic/claude-3-haiku',  # Fast alternative
        'google/gemini-2.0-flash',  # Good alternative
        'cohere/command-r-plus',  # Reliable alternative
    ]
}

# Fallback Models (Free/Experimental, Less Reliable)
FALLBACK_MODELS = {
    'breakdown': [
        'mistralai/mistral-small',  # Free, basic performance
        'qwen/qwen3-8b',  # Free alternative
        'meta-llama/llama-3.1-8b-instruct',  # Free alternative
        'deepseek/deepseek-chat',  # Alternative DeepSeek model
        'deepseek/deepseek-v3-base',  # Another DeepSeek option
    ],
    'reviewer': [
        'mistralai/mistral-small',  # Free, basic performance
        'qwen/qwen3-8b',  # Free alternative
        'meta-llama/llama-3.1-8b-instruct',  # Free alternative
        'deepseek/deepseek-chat',  # Alternative DeepSeek model
        'deepseek/deepseek-v3-base',  # Another DeepSeek option
    ],
    'finalizer': [
        'mistralai/mistral-small',  # Free, basic performance
        'qwen/qwen3-8b',  # Free alternative
        'meta-llama/llama-3.1-8b-instruct',  # Free alternative
        'deepseek/deepseek-chat',  # Alternative DeepSeek model
        'deepseek/deepseek-v3-base',  # Another DeepSeek option
    ],
    'reanalyzer': [
        'mistralai/mistral-small',  # Free, basic performance
        'qwen/qwen3-8b',  # Free alternative
        'meta-llama/llama-3.1-8b-instruct',  # Free alternative
        'deepseek/deepseek-chat',  # Alternative DeepSeek model
        'deepseek/deepseek-v3-base',  # Another DeepSeek option
    ]
}

# Legacy Models (Current models, kept for backward compatibility)
LEGACY_MODELS = {
    'breakdown': 'deepseek/deepseek-r1-0528-qwen3-8b:free',
    'reviewer': 'tngtech/deepseek-r1t2-chimera:free',
    'finalizer': 'deepseek/deepseek-r1-0528-qwen3-8b:free',
    'reanalyzer': 'openrouter/horizon-beta',
}

def get_model_list(task_type):
    """
    Get a prioritized list of models for a specific task type.
    Returns models in order of preference (most reliable first).
    """
    if task_type not in PRIMARY_MODELS:
        return [LEGACY_MODELS.get(task_type, 'openai/gpt-3.5-turbo')]
    
    # Combine all model lists in priority order
    all_models = []
    all_models.extend(PRIMARY_MODELS[task_type])
    all_models.extend(SECONDARY_MODELS[task_type])
    all_models.extend(FALLBACK_MODELS[task_type])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_models = []
    for model in all_models:
        if model not in seen:
            seen.add(model)
            unique_models.append(model)
    
    return unique_models

def get_next_model(task_type, current_model, failed_models=None):
    """
    Get the next model to try when the current one fails.
    
    Args:
        task_type: The type of task (breakdown, reviewer, finalizer, reanalyzer)
        current_model: The current model that failed
        failed_models: List of models that have already failed
    
    Returns:
        The next model to try, or None if all models have been tried
    """
    if failed_models is None:
        failed_models = []
    
    model_list = get_model_list(task_type)
    
    # Find the current model in the list
    try:
        current_index = model_list.index(current_model)
    except ValueError:
        # If current model not found, start from the beginning
        current_index = -1
    
    # Find the next available model
    for i in range(current_index + 1, len(model_list)):
        if model_list[i] not in failed_models:
            return model_list[i]
    
    # If no more models in the list, try the legacy model
    legacy_model = LEGACY_MODELS.get(task_type)
    if legacy_model and legacy_model not in failed_models:
        return legacy_model
    
    return None

def get_default_model(task_type):
    """
    Get the default (most reliable) model for a task type.
    """
    model_list = get_model_list(task_type)
    return model_list[0] if model_list else LEGACY_MODELS.get(task_type, 'openai/gpt-3.5-turbo')

# Model categories for UI display
MODEL_CATEGORIES = {
    'Premium': 'High-performance, most reliable models (GPT-4, Claude 3.5)',
    'Standard': 'Good performance, reliable models (GPT-3.5, Mistral Large)',
    'Free': 'Free models with basic performance (Mistral Small, Qwen)',
    'Legacy': 'Current models kept for backward compatibility'
}

# Model metadata for better understanding
MODEL_METADATA = {
    'openai/gpt-4o': {
        'category': 'Premium',
        'description': 'Most advanced GPT model, excellent performance',
        'reliability': 'Very High',
        'speed': 'Fast',
        'cost': 'High'
    },
    'anthropic/claude-3.5-sonnet': {
        'category': 'Premium',
        'description': 'Excellent reasoning and analysis capabilities',
        'reliability': 'Very High',
        'speed': 'Fast',
        'cost': 'High'
    },
    'openai/gpt-3.5-turbo': {
        'category': 'Standard',
        'description': 'Very reliable, good performance, cost-effective',
        'reliability': 'Very High',
        'speed': 'Very Fast',
        'cost': 'Medium'
    },
    'mistralai/mistral-large': {
        'category': 'Standard',
        'description': 'Good reasoning, reliable performance',
        'reliability': 'High',
        'speed': 'Fast',
        'cost': 'Medium'
    },
    'mistralai/mistral-small': {
        'category': 'Free',
        'description': 'Basic performance, free to use',
        'reliability': 'Medium',
        'speed': 'Very Fast',
        'cost': 'Free'
    }
}
