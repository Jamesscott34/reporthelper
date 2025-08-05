#!/usr/bin/env python3
"""
Script to generate a secure Django secret key.
Run this script to generate a new secret key for production use.
"""

import os
import sys
from django.core.management.utils import get_random_secret_key

def generate_secret_key():
    """Generate a secure Django secret key."""
    secret_key = get_random_secret_key()
    print(f"Generated secure secret key: {secret_key}")
    print("\nTo use this key:")
    print("1. Copy the key above")
    print("2. Add it to your .env file:")
    print(f"   SECRET_KEY={secret_key}")
    print("3. Or set it as an environment variable:")
    print(f"   export SECRET_KEY='{secret_key}'")
    return secret_key

if __name__ == "__main__":
    try:
        generate_secret_key()
    except ImportError:
        print("Django not found. Please install Django first:")
        print("pip install django")
        sys.exit(1) 