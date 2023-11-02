from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

PATH_TO_ENV: Path = Path.cwd() / 'reports' / 'database' / '.env'


class MySQLConf(BaseSettings):
    msql_db: SecretStr
    model_config = SettingsConfigDict(env_file=PATH_TO_ENV, env_file_encoding='utf-8')


conf = MySQLConf()

