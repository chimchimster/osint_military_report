from typing import List, Dict, Union

import json
import pathlib
import aiofiles


async def read_schema(path: pathlib.Path, key: str) -> Union[List, Dict]:

    async with aiofiles.open(path, 'r') as file:
        data = await file.read()
        return json.loads(data).get(key)


async def remove_report(path: pathlib.Path, report_name: str) -> None:

    for file_name in path.iterdir():
        if file_name.name == report_name:
            file_name.unlink()


__all__ = [
    'read_schema',
    'remove_report',
]
