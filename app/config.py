from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str = "localhost"
    database_password: str = "lendmarketsurvey"
    database_username: str = "root"
    database_name: str = "api"
    database_port: str = "5432"
    secret_key: str = "fastapipassword"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class onfig:
        env_file = ".env"

settings = Settings()