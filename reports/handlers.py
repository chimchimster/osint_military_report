import uuid
import asyncio

from pathlib import Path
from typing import Final, List

from fastapi import APIRouter
from fastapi.responses import FileResponse

from .utils import *
from .database import *
from .models import ClientSettings
from .xlsx_report import *

router = APIRouter()

REPORT_STACK_LOCK = asyncio.Lock()
PREVIOUS_REPORTS_STACK: Final[List[str]] = []


@router.post('/report/')
async def report_handler(item: ClientSettings):

    moderator_id: int = item.user_id
    report_type: int = item.r_type

    path_to_temp: Path = Path.cwd() / 'reports' / 'temp'
    report_file_name: str = str(uuid.uuid4()) + '.xlsx'
    report_path: Path = path_to_temp / report_file_name

    users_data = await get_users_data_mapped_to_moderator(moderator_id)

    dataframe = await generate_dataframe(users_data)

    running_loop = asyncio.get_running_loop()

    await running_loop.run_in_executor(None, render_xlsx_document, dataframe, report_path)

    response_file = FileResponse(
        path=report_path,
        filename='Отчет военнослужащие.xlsx',
        media_type='multipart/form-data',
    )

    async with REPORT_STACK_LOCK:
        if PREVIOUS_REPORTS_STACK:
            prev_report_name = PREVIOUS_REPORTS_STACK.pop()
            await remove_report(path_to_temp, prev_report_name)

        PREVIOUS_REPORTS_STACK.append(report_file_name)

    return response_file


__all__ = [
    'router',
]
