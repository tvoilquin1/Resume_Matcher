from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    FIRECRAWL_API_KEY: str
    ANTHROPIC_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    MIN_CHECK_FREQUENCY: int = 15  # minutes
    MAX_SOURCES_PER_USER: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
