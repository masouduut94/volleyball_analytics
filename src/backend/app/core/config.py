from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    MODE: str
    DEV_USERNAME: str
    DEV_PASSWORD: str
    DEV_HOST: str
    DEV_DB: str
    DEV_PORT: int
    DEV_DRIVER: str
    TEST_DB_URL: str
    PROJECT_NAME: str = "volleyball_analytics"
    API_PREFIX: str = "/api/"

    def get_development_db_uri(self):
        return f"{self.DEV_DRIVER}://{self.DEV_USERNAME}:{self.DEV_PASSWORD}@{self.DEV_HOST}:{self.DEV_PORT}/{self.DEV_DB}"

    def get_test_uri(self):
        return self.TEST_DB_URL

    def get_db_uri(self):
        return self.get_test_uri() if self.MODE == "test" else self.get_development_db_uri()


env_file = 'conf/.env'
settings = Settings(_env_file=env_file, _env_file_encoding='utf-8')
