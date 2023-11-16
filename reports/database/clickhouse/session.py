from clickhouse_sqlalchemy import make_session
from .engine import clh_engine

ClickHouseSession = make_session(clh_engine.engine, is_async=True)
