from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_hostname: str = "localhost"
    database_port: str = "5432"
    database_password: str = "postgres"
    database_name: str = "fastapi_posts"
    database_username: str = "postgres"
    secret_key: str = "default-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env")
#si falta un atributo en el archivo .env, pydantic mandara error    

settings = Settings()
