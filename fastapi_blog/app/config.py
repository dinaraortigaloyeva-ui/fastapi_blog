
from pydantic_settings import BaseSettings
from typing import List

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
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def hosts_list(self) -> List[str]:
        return [h.strip() for h in self.allowed_hosts.split(",")]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

