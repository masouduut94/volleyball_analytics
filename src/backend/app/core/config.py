from typing import List

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    mode: str
    dev_username: str
    dev_password: str
    dev_host: str
    dev_db: str
    dev_port: int
    dev_driver: str
    test_db_url: str
    rbmq_username: str
    rbmq_password: str
    rbmq_host: str
    rbmq_vhost: str
    rbmq_port: int

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "127.0.0.1:8080"
    ]
    PROJECT_NAME: str = "volleyball_analytics"
    API_PREFIX: str = "/api/"

    def get_development_db_uri(self):
        return f"{self.dev_driver}://{self.dev_username}:{self.dev_password}@{self.dev_host}:{self.dev_port}/{self.dev_db}"

    def get_rabbitmq_uri(self):
        return f"amqp://{self.rbmq_username}:{self.rbmq_password}@{self.rbmq_host}:{self.rbmq_port}/{self.rbmq_vhost}"

    def get_test_uri(self):
        return self.test_db_url

    def get_db_uri(self):
        return self.get_test_uri() if self.mode == "test" else self.get_development_db_uri()


env_file = '/home/masoud/Desktop/projects/volleyball_analytics/conf/.env'
settings = Settings(_env_file=env_file, _env_file_encoding='utf-8')
# print(settings.get_development_db_uri())
# print(settings.get_test_uri())
# print(settings.get_rabbitmq_uri())
