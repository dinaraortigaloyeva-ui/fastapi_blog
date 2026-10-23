
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    allowed_origins: str = "http://localhost:3000"
    allowed_hosts: str = "localhost,127.0.0.1"
    environment: str = "development"
    debug: bool = True

    @property
    def origins_list(self) -> List[str]:
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
        ]

    @property
    def hosts_list(self) -> List[str]:
        return [
            host.strip()
            for host in self.allowed_hosts.split(",")
        ]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    class Config:
        env_file = Path(__file__).resolve().parents[2] / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
