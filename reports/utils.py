import sys
import json
import pathlib
import aiofiles

from typing import List, Dict, Union


async def read_schema(path: pathlib.Path, key: str) -> Union[List, Dict]:

    async with aiofiles.open(path, 'r') as file:
        data = await file.read()
        return json.loads(data).get(key)


async def remove_report(
        path_to_temp: pathlib.Path,
        report_file_name: str,
) -> None:

    for child in path_to_temp.iterdir():
        if child.name.endswith(report_file_name):
            child.unlink()


async def cleanup_directory():

    directory_path = pathlib.Path.cwd() / 'reports' / 'temp'
    for item in directory_path.iterdir():
        if item.is_file():
            item.unlink()


async def graceful_exit(signum, frame):

    await cleanup_directory()

    sys.exit(0)


__all__ = [
    'read_schema',
    'remove_report',
    'graceful_exit',
    'cleanup_directory',
]
