from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

PATH_TO_ENV: Path = Path('/home/newuser/osint_military_reports/osint_military_report/reports/database/.env')


class DBConfz(BaseSettings):
    msql_db: SecretStr
    clickhouse_db: SecretStr
    model_config = SettingsConfigDict(env_file=PATH_TO_ENV, env_file_encoding='utf-8')


conf = DBConfz()
