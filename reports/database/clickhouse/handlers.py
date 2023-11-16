""" No need in this module anymore. """

import sys
from typing import Dict

import clickhouse_sqlalchemy.exceptions
from clickhouse_sqlalchemy import select
from .models import Attachment
from .session import ClickHouseSession


async def get_posts_types_count(mapped_source_res_id_and_posts_ids: Dict):

    select.inherit_cache = True
    select_stmt = select(Attachment.type)

    async with ClickHouseSession as session:
        try:
            result = await session.execute(select_stmt)
            return result.fetchall()
        except clickhouse_sqlalchemy.exceptions.DatabaseException as e:
            sys.stderr.write(str(e))


__all__ = ['get_posts_types_count',]
