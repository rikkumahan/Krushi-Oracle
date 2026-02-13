"""
Test Azure OpenAI Integration
Verify Azure credentials work before testing full endpoint
"""

import asyncio
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_azure_openai():
    """Test Azure OpenAI helper with actual credentials"""
    
    print("=" * 70)
    print("🔍 Azure OpenAI Integration Test")
    print("=" * 70)
    
    try:
        # Test 1: Config loading
        print("\n📋 Test 1: Configuration Loading")
        from core.config import get_settings
        settings = get_settings()
        
        print(f"  Endpoint: {settings.AZURE_OPENAI_ENDPOINT}")
        print(f"  Deployment: {settings.AZURE_OPENAI_DEPLOYMENT}")
        print(f"  API Version: {settings.AZURE_OPENAI_API_VERSION}")
        print(f"  Key configured: {bool(settings.AZURE_OPENAI_KEY)}")
        
        if not settings.AZURE_OPENAI_ENDPOINT or not settings.AZURE_OPENAI_KEY:
            print("❌ Azure OpenAI credentials not configured in .env")
            return
        
        print("✅ Configuration loaded successfully")
        
        # Test 2: Client initialization
        print("\n🔌 Test 2: OpenAI Client Initialization")
        from utils.openai_helper import get_openai_client, get_model_name
        
        client = get_openai_client()
        model = get_model_name()
        
        if not client:
            print("❌ Failed to create OpenAI client")
            return
        
        print(f"✅ Client initialized: Azure OpenAI")
        print(f"  Model/Deployment: {model}")
        
        # Test 3: Simple API call
        print("\n🧪 Test 3: Simple API Call (Keyword Extraction)")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Extract 3 relevant search keywords from the user's idea. Return as JSON array."
                },
                {
                    "role": "user",
                    "content": "AI-powered code review assistant for developers"
                }
            ],
            temperature=0,
            max_tokens=100
        )
        
        result = response.choices[0].message.content
        print(f"✅ API call successful!")
        print(f"  Response: {result}")
        print(f"  Model used: {response.model}")
        print(f"  Tokens: {response.usage.total_tokens}")
        
        # Test 4: Universal validator dependency
        print("\n🔗 Test 4: Universal Validator Dependencies")
        from verification.dependencies import get_universal_validator
        
        validator = get_universal_validator()
        print(f"✅ Universal validator loaded successfully")
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED - Azure OpenAI is working!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_azure_openai())
