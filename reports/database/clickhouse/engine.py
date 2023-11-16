from sqlalchemy.ext.asyncio import create_async_engine
from osint_military_report.reports.database.config import conf


class ClickHouseEngine:
    db_url = conf.clickhouse_db.get_secret_value()
    engine = create_async_engine(db_url)


clh_engine = ClickHouseEngine()
