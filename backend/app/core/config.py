from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Hotel AI Agent Backend"
    app_version: str = "0.1.0"
    debug: bool = True
    database_url: str = "sqlite:///./hotel_agent.db"

    class Config:
        env_file = ".env"


settings = Settings()