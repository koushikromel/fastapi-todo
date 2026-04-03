from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USERNAME: str = "postgres"
    DB_PASSWORD: SecretStr
    DB_HOSTNAME: str = "postgres"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"

    @property
    def DB_URL(self) -> str:
        return (
            f"postgresql://{self.DB_USERNAME}:"
            f"{self.DB_PASSWORD.get_secret_value()}@"
            f"{self.DB_HOSTNAME}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = {"env_file": ".env"}


def get_settings() -> Settings:
    return Settings()
