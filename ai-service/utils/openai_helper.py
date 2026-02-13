"""
OpenAI Client Helper
Automatically uses Azure OpenAI when configured, falls back to regular OpenAI
"""

from openai import OpenAI, AzureOpenAI
from core.config import get_settings
import logging

logger = logging.getLogger(__name__)


def get_openai_client():
    """
    Get appropriate OpenAI client (Azure or regular)
    
    Priority:
    1. Azure OpenAI (if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY are set)
    2. Regular OpenAI (if OPENAI_API_KEY is set)
    3. None (services will use fallback/mock data)
    """
    settings = get_settings()
    
    # Try Azure OpenAI first (preferred for student credits)
    if settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_KEY:
        logger.info(f"Using Azure OpenAI: {settings.AZURE_OPENAI_DEPLOYMENT}")
        return AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )
    
    # Fall back to regular OpenAI
    if settings.OPENAI_API_KEY:
        logger.info(f"Using OpenAI API: {settings.OPENAI_MODEL}")
        return OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # No API key configured
    logger.warning("No OpenAI credentials configured - some features will use fallback data")
    return None


def get_model_name():
    """
    Get the appropriate model/deployment name
    
    Returns:
        str: Deployment name for Azure OpenAI, or model name for regular OpenAI
    """
    settings = get_settings()
    
    # Azure uses deployment name
    if settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_KEY:
        return settings.AZURE_OPENAI_DEPLOYMENT
    
    # Regular OpenAI uses model name
    return settings.OPENAI_MODEL


def create_chat_completion(messages: list, temperature: float = 0, **kwargs):
    """
    Create a chat completion using available OpenAI client
    
    Args:
        messages: List of message dicts
        temperature: Sampling temperature (0 for deterministic)
        **kwargs: Additional arguments to pass to API
    
    Returns:
        Chat completion response or None if no client available
    """
    client = get_openai_client()
    
    if not client:
        logger.warning("No OpenAI client available")
        return None
    
    try:
        response = client.chat.completions.create(
            model=get_model_name(),
            messages=messages,
            temperature=temperature,
            **kwargs
        )
        return response
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return None
