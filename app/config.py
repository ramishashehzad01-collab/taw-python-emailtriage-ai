from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EmailTriage AI"
    database_url: str = "sqlite:///./emailtriage.db"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ai_provider: str = "local"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-20b"
    openrouter_api_key: str = ""
    openrouter_model: str = ""
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5-20250929"
    google_client_secret_file: str = "credentials.json"
    google_token_file: str = "token.json"
    gmail_enabled: bool = True
    gmail_scopes: str = "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.compose"
    max_emails_per_sync: int = 25
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
