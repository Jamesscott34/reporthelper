#!/usr/bin/env python3
"""
Test script for LM Studio integration
This script tests the connection and basic functionality with LM Studio
"""

import requests
import json
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_report_writer.settings')
import django
django.setup()

from django.conf import settings

def test_lm_studio_connection():
    """Test basic connection to LM Studio"""
    print("🧪 Testing LM Studio Connection")
    print("=" * 40)
    
    # Test models endpoint
    try:
        response = requests.get(f"{settings.OLLAMA_HOST}/v1/models", timeout=10)
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Models endpoint responding")
            print(f"📋 Available models: {[model.get('id', '') for model in models.get('data', [])]}")
            return True
        else:
            print(f"❌ Models endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to models endpoint: {e}")
        return False

def test_chat_completion():
    """Test chat completion functionality"""
    print("\n🤖 Testing Chat Completion")
    print("=" * 30)
    
    try:
        payload = {
            "model": settings.OLLAMA_MODELS['breakdown'],
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, this is a test. Please respond with 'Test successful' if you can see this message."
                }
            ],
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 50
        }
        
        response = requests.post(
            f"{settings.OLLAMA_HOST}/v1/chat/completions",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                print(f"✅ Chat completion successful")
                print(f"📝 Response: {content[:100]}...")
                return True
            else:
                print(f"❌ No choices in response")
                return False
        else:
            print(f"❌ Chat completion failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat completion test failed: {e}")
        return False

def test_ai_breakdown_service():
    """Test the AI breakdown service"""
    print("\n📄 Testing AI Breakdown Service")
    print("=" * 35)
    
    try:
        from breakdown.ai_breakdown import AIBreakdownService
        
        service = AIBreakdownService()
        
        # Test with a simple document
        test_text = """
        This is a test document for AI breakdown.
        
        Section 1: Introduction
        This section introduces the main topic and provides background information.
        
        Section 2: Methodology
        This section describes the approach and methods used in the study.
        
        Section 3: Results
        This section presents the findings and outcomes of the analysis.
        
        Section 4: Conclusion
        This section summarizes the key points and provides recommendations.
        """
        
        result = service.breakdown_document(test_text)
        
        if result.get('success'):
            print(f"✅ AI breakdown successful")
            print(f"📊 Sections created: {result['breakdown'].get('total_sections', 0)}")
            print(f"🤖 Model used: {result.get('model_used', 'Unknown')}")
            return True
        else:
            print(f"❌ AI breakdown failed")
            return False
            
    except Exception as e:
        print(f"❌ AI breakdown service test failed: {e}")
        return False

def test_model_availability():
    """Test if the required models are available"""
    print("\n🔍 Testing Model Availability")
    print("=" * 30)
    
    try:
        response = requests.get(f"{settings.OLLAMA_HOST}/v1/models", timeout=10)
        if response.status_code == 200:
            models = response.json()
            available_models = [model.get('id', '') for model in models.get('data', [])]
            
            required_models = [
                settings.OLLAMA_MODELS['breakdown'],
                settings.OLLAMA_MODELS['reviewer'],
                settings.OLLAMA_MODELS['finalizer'],
                settings.OLLAMA_MODELS['reanalyzer']
            ]
            
            missing_models = []
            for model in required_models:
                if model in available_models:
                    print(f"✅ {model}: Available")
                else:
                    print(f"❌ {model}: Not available")
                    missing_models.append(model)
            
            if missing_models:
                print(f"\n⚠️  Missing models: {', '.join(missing_models)}")
                print("Please load these models in LM Studio")
                return False
            else:
                print(f"\n✅ All required models are available")
                return True
        else:
            print(f"❌ Failed to get models list")
            return False
            
    except Exception as e:
        print(f"❌ Model availability test failed: {e}")
        return False

def test_error_handling():
    """Test error handling for various scenarios"""
    print("\n🛡️ Testing Error Handling")
    print("=" * 25)
    
    # Test with invalid model
    try:
        payload = {
            "model": "invalid-model-name",
            "messages": [
                {
                    "role": "user",
                    "content": "Test message"
                }
            ],
            "stream": False
        }
        
        response = requests.post(
            f"{settings.OLLAMA_HOST}/v1/chat/completions",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 400 or response.status_code == 404:
            print(f"✅ Error handling working (expected error for invalid model)")
            return True
        else:
            print(f"⚠️  Unexpected response for invalid model: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✅ Error handling working (exception caught: {type(e).__name__})")
        return True

def main():
    """Run all tests"""
    print("🚀 LM Studio Integration Test Suite")
    print("=" * 40)
    
    tests = [
        ("Connection Test", test_lm_studio_connection),
        ("Model Availability Test", test_model_availability),
        ("Chat Completion Test", test_chat_completion),
        ("AI Breakdown Service Test", test_ai_breakdown_service),
        ("Error Handling Test", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! LM Studio integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check your LM Studio setup.")
        print("\n💡 Troubleshooting tips:")
        print("1. Ensure LM Studio is running with local server enabled")
        print("2. Check that models are loaded in LM Studio")
        print("3. Verify the API endpoint is accessible at http://192.168.0.34:1234")
        print("4. Check firewall settings if connection fails")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 