from sqlalchemy.ext.asyncio import create_async_engine

from osint_military_report.reports.database.config import conf


class MySQLEngine:
    db_url = conf.msql_db.get_secret_value()
    engine = create_async_engine(db_url)


ms_engine = MySQLEngine()
