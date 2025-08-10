#!/usr/bin/env python3
"""
Quick Model Switcher for AI Report Writer
This script helps you quickly switch between different AI models.
"""

import os
import sys
from pathlib import Path

# Available model presets
MODEL_PRESETS = {
    'premium': {
        'name': 'Premium Models (Most Reliable)',
        'models': {
            'BREAKDOWN_MODEL': 'openai/gpt-4o',
            'REVIEWER_MODEL': 'anthropic/claude-3.5-sonnet',
            'FINALIZER_MODEL': 'openai/gpt-4o-mini',
            'REANALYZER_MODEL': 'openai/gpt-4o'
        }
    },
    'standard': {
        'name': 'Standard Models (Good Balance)',
        'models': {
            'BREAKDOWN_MODEL': 'openai/gpt-3.5-turbo',
            'REVIEWER_MODEL': 'mistralai/mistral-large',
            'FINALIZER_MODEL': 'openai/gpt-3.5-turbo',
            'REANALYZER_MODEL': 'openai/gpt-3.5-turbo'
        }
    },
    'free': {
        'name': 'Free Models (Basic Performance)',
        'models': {
            'BREAKDOWN_MODEL': 'mistralai/mistral-small',
            'REVIEWER_MODEL': 'mistralai/mistral-small',
            'FINALIZER_MODEL': 'mistralai/mistral-small',
            'REANALYZER_MODEL': 'mistralai/mistral-small'
        }
    },
    'legacy': {
        'name': 'Legacy Models (Current Setup)',
        'models': {
            'BREAKDOWN_MODEL': 'deepseek/deepseek-r1-0528-qwen3-8b:free',
            'REVIEWER_MODEL': 'tngtech/deepseek-r1t2-chimera:free',
            'FINALIZER_MODEL': 'deepseek/deepseek-r1-0528-qwen3-8b:free',
            'REANALYZER_MODEL': 'openrouter/horizon-beta'
        }
    }
}

def print_available_presets():
    """Print all available model presets."""
    print("\n📋 AVAILABLE MODEL PRESETS:")
    print("=" * 50)
    for key, preset in MODEL_PRESETS.items():
        print(f"\n🔹 {key.upper()}: {preset['name']}")
        for model_type, model in preset['models'].items():
            print(f"   {model_type}: {model}")

def print_current_models():
    """Print currently configured models."""
    print("\n🔍 CURRENT MODEL CONFIGURATION:")
    print("=" * 50)
    for env_var in ['BREAKDOWN_MODEL', 'REVIEWER_MODEL', 'FINALIZER_MODEL', 'REANALYZER_MODEL']:
        value = os.getenv(env_var, 'Not set')
        print(f"   {env_var}: {value}")

def switch_to_preset(preset_name):
    """Switch to a specific model preset."""
    if preset_name not in MODEL_PRESETS:
        print(f"❌ Error: Preset '{preset_name}' not found!")
        return False
    
    preset = MODEL_PRESETS[preset_name]
    print(f"\n🔄 Switching to {preset['name']}...")
    
    # Create or update .env file
    env_file = Path('.env')
    env_content = []
    
    # Read existing .env file if it exists
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.readlines()
    
    # Update or add model configurations
    updated = False
    for model_type, model in preset['models'].items():
        found = False
        for i, line in enumerate(env_content):
            if line.startswith(f'{model_type}='):
                env_content[i] = f'{model_type}={model}\n'
                found = True
                updated = True
                break
        
        if not found:
            env_content.append(f'{model_type}={model}\n')
            updated = True
    
    # Write updated .env file
    if updated:
        with open(env_file, 'w') as f:
            f.writelines(env_content)
        print(f"✅ Successfully updated .env file with {preset['name']}")
        print("\n📝 Updated models:")
        for model_type, model in preset['models'].items():
            print(f"   {model_type}: {model}")
        
        print(f"\n⚠️  IMPORTANT: Restart your application for changes to take effect!")
        return True
    else:
        print("ℹ️  No changes needed - models already match preset")
        return True

def create_env_template():
    """Create a template .env file with all available models."""
    env_file = Path('.env.template')
    
    template_content = """# AI Model Configuration Template
# Copy this file to .env and modify as needed

# Premium Models (Most Reliable)
BREAKDOWN_MODEL=openai/gpt-4o
REVIEWER_MODEL=anthropic/claude-3.5-sonnet
FINALIZER_MODEL=openai/gpt-4o-mini
REANALYZER_MODEL=openai/gpt-4o

# Standard Models (Good Balance)
# BREAKDOWN_MODEL=openai/gpt-3.5-turbo
# REVIEWER_MODEL=mistralai/mistral-large
# FINALIZER_MODEL=openai/gpt-3.5-turbo
# REANALYZER_MODEL=openai/gpt-3.5-turbo

# Free Models (Basic Performance)
# BREAKDOWN_MODEL=mistralai/mistral-small
# REVIEWER_MODEL=mistralai/mistral-small
# FINALIZER_MODEL=mistralai/mistral-small
# REANALYZER_MODEL=mistralai/mistral-small

# Legacy Models (Current Setup)
# BREAKDOWN_MODEL=deepseek/deepseek-r1-0528-qwen3-8b:free
# REVIEWER_MODEL=tngtech/deepseek-r1t2-chimera:free
# FINALIZER_MODEL=deepseek/deepseek-r1-0528-qwen3-8b:free
# REANALYZER_MODEL=openrouter/horizon-beta

# API Keys (Required)
OPENROUTE_API_KEY_OPENROUTER=your_openrouter_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
"""
    
    with open(env_file, 'w') as f:
        f.write(template_content)
    
    print(f"✅ Created .env.template file")
    print("📝 Edit this file and copy to .env to configure your models")

def main():
    """Main function."""
    print("🤖 AI Model Switcher for Report AI")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("\n📖 USAGE:")
        print("   python switch_model.py [command]")
        print("\n🔧 COMMANDS:")
        print("   list          - Show available presets")
        print("   current       - Show current configuration")
        print("   premium       - Switch to premium models")
        print("   standard      - Switch to standard models")
        print("   free          - Switch to free models")
        print("   legacy        - Switch to legacy models")
        print("   template      - Create .env template file")
        print("   help          - Show this help message")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        print_available_presets()
    
    elif command == 'current':
        print_current_models()
    
    elif command == 'template':
        create_env_template()
    
    elif command in ['premium', 'standard', 'free', 'legacy']:
        switch_to_preset(command)
    
    elif command == 'help':
        print("\n📖 USAGE:")
        print("   python switch_model.py [command]")
        print("\n🔧 COMMANDS:")
        print("   list          - Show available presets")
        print("   current       - Show current configuration")
        print("   premium       - Switch to premium models")
        print("   standard      - Switch to standard models")
        print("   free          - Switch to free models")
        print("   legacy        - Switch to legacy models")
        print("   template      - Create .env template file")
        print("   help          - Show this help message")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python switch_model.py help' for usage information")

if __name__ == "__main__":
    main()
