
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """Application settings (loaded from .env)"""
    
    APP_NAME: str = "Nova AI Service"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # OpenAI Configuration (supports both Azure and regular OpenAI)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    
    # Azure OpenAI Configuration (preferred if available)
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_KEY: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = "gpt-4o"
    AZURE_OPENAI_API_VERSION: str = "2024-12-01-preview"
    
    # Universal Validation API Keys
    SERPAPI_KEY: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    
    # Feature Flags
    GOOGLE_TRENDS_ENABLED: bool = False
    
    # Smart Comparison Search
    PRODUCTHUNT_API_TOKEN: Optional[str] = None

    # Database
    DATABASE_URL: str = "sqlite:///./novadb.sqlite"
    POSTGRES_USER: str = "nova"
    POSTGRES_PASSWORD: str = "nova_password"
    POSTGRES_DB: str = "novadb"
    
    # Redis Configuration (Optional - graceful degradation if not configured)
    REDIS_HOST: Optional[str] = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"

    # Integration
    JAVA_BACKEND_URL: str = "http://localhost:8080"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    """Singleton getter for settings"""
    return Settings()
