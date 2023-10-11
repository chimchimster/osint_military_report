from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class MySQLConf(BaseSettings):
    msql_db: SecretStr
    model_config = SettingsConfigDict(env_file='reports/database/.env', env_file_encoding='utf-8')


conf = MySQLConf()

