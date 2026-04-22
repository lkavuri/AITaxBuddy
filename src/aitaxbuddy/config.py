"""Configuration management for AI Tax Buddy."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # LLM Provider
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    model_provider: Literal["openai", "anthropic"] = "openai"
    model_name: str = "gpt-4o"
    temperature: float = 0.0
    
    # Langfuse Observability
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str = "https://cloud.langfuse.com"
    
    # Mem0
    mem0_api_key: str | None = None
    
    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "password"
    
    # E2B
    e2b_api_key: str | None = None
    
    # Application
    environment: Literal["development", "production"] = "development"
    log_level: str = "INFO"
    max_iterations: int = 5
    
    # Security
    enable_pii_filtering: bool = True
    enable_content_guardrails: bool = True


settings = Settings()
