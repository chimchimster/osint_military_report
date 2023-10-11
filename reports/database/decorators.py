import sys
from functools import wraps

from .session import LocalAsyncSession


def execute_transaction(coro):
    @wraps(coro)
    async def wrapper(*args, **kwargs):
        async with LocalAsyncSession() as session:
            async with session.begin() as transaction:
                try:
                    return await coro(*args, **kwargs, session=session)
                except Exception as e:
                    await transaction.rollback()
                    sys.stderr.write('Transaction error: ' + str(e))
                finally:
                    await transaction.commit()

    return wrapper

