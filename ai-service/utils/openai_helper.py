"""
OpenAI Client Helper
Priority order:
1. Sarvam.ai (if SARVAM_API_KEY is set) — FREE, OpenAI-compatible
2. Azure OpenAI (if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY are set)
3. Regular OpenAI (if OPENAI_API_KEY is set)
"""

from openai import OpenAI, AzureOpenAI
from core.config import get_settings
import logging

logger = logging.getLogger(__name__)


def get_openai_client():
    """
    Get appropriate OpenAI client based on configured provider.

    Priority:
    1. Sarvam.ai (SARVAM_API_KEY) — free drop-in replacement, OpenAI-compatible
    2. Azure OpenAI (AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_KEY)
    3. Regular OpenAI (OPENAI_API_KEY)
    4. None (services will use fallback/mock data)
    """
    settings = get_settings()

    # 1. Try Sarvam.ai first (free, OpenAI-compatible)
    if settings.SARVAM_API_KEY and settings.SARVAM_API_KEY != "your_sarvam_api_key_here":
        logger.info(f"Using Sarvam.ai: {settings.SARVAM_MODEL}")
        return OpenAI(
            api_key=settings.SARVAM_API_KEY,
            base_url=settings.SARVAM_BASE_URL,
        )

    # 2. Try Azure OpenAI
    if settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_KEY:
        logger.info(f"Using Azure OpenAI: {settings.AZURE_OPENAI_DEPLOYMENT}")
        return AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )

    # 3. Fall back to regular OpenAI
    if settings.OPENAI_API_KEY:
        logger.info(f"Using OpenAI API: {settings.OPENAI_MODEL}")
        return OpenAI(api_key=settings.OPENAI_API_KEY)

    # No API key configured
    logger.warning("No LLM credentials configured - some features will use fallback data")
    return None


def get_model_name():
    """
    Get the appropriate model/deployment name for the active provider.

    Returns:
        str: Model name for the configured LLM provider
    """
    settings = get_settings()

    # Sarvam.ai
    if settings.SARVAM_API_KEY and settings.SARVAM_API_KEY != "your_sarvam_api_key_here":
        return settings.SARVAM_MODEL

    # Azure uses deployment name
    if settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_KEY:
        return settings.AZURE_OPENAI_DEPLOYMENT

    # Regular OpenAI uses model name
    return settings.OPENAI_MODEL


def is_sarvam_active() -> bool:
    """Check if Sarvam.ai is the active LLM provider."""
    settings = get_settings()
    return bool(settings.SARVAM_API_KEY and settings.SARVAM_API_KEY != "your_sarvam_api_key_here")


def create_chat_completion(messages: list, temperature: float = 0, **kwargs):
    """
    Create a chat completion using available LLM client.

    NOTE: If using Sarvam.ai, response_format={"type": "json_object"} is
    automatically dropped and JSON instructions are injected into the system
    prompt instead, since Sarvam.ai doesn't officially document this parameter.

    Args:
        messages: List of message dicts
        temperature: Sampling temperature (0 for deterministic)
        **kwargs: Additional arguments to pass to API

    Returns:
        Chat completion response or None if no client available
    """
    client = get_openai_client()

    if not client:
        logger.warning("No LLM client available")
        return None

    # Sarvam.ai: patch response_format if present
    if is_sarvam_active() and "response_format" in kwargs:
        fmt = kwargs.pop("response_format")
        if fmt == {"type": "json_object"}:
            # Inject JSON instruction into last user message or add a system message
            _inject_json_instruction(messages)

    try:
        response = client.chat.completions.create(
            model=get_model_name(),
            messages=messages,
            temperature=temperature,
            **kwargs
        )
        return response
    except Exception as e:
        logger.error(f"LLM API error: {str(e)}")
        return None


def _inject_json_instruction(messages: list) -> None:
    """
    Inject a JSON output instruction into the messages list when
    response_format is not supported by the provider (e.g., Sarvam.ai).
    Modifies the list in-place.
    """
    json_instruction = "IMPORTANT: Respond with ONLY valid JSON. No explanation, no markdown, no code fences. Just the raw JSON object."

    # Check if there's already a system message
    for msg in messages:
        if msg.get("role") == "system":
            if json_instruction not in msg["content"]:
                msg["content"] = msg["content"].rstrip() + "\n\n" + json_instruction
            return

    # No system message — prepend one
    messages.insert(0, {"role": "system", "content": json_instruction})
