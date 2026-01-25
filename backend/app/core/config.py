from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+psycopg://wa_user:wa_password@localhost:5432/wa_database"

    # JWT Settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # WhatsApp Cloud API
    wa_phone_number_id: str = ""
    wa_business_account_id: str = ""
    wa_access_token: str = ""
    wa_verify_token: str = "my_verify_token"
    wa_app_secret: str = ""

    # API Base URL
    wa_api_base_url: str = "https://graph.facebook.com/v18.0"

    # Evolution API Settings
    evolution_api_url: str = "http://evolution:8080"
    evolution_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
