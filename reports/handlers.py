import uuid
import asyncio

from pathlib import Path
from typing import Final, List

from fastapi import APIRouter
from fastapi.responses import FileResponse

from pandas import concat

from .utils import *
from .database import *
from .models import ClientSettings
from .lxml_report import render_xlsx_document, generate_dataframe

router = APIRouter()

REPORT_STACK_LOCK = asyncio.Lock()
PREVIOUS_REPORTS_STACK: Final[List[str]] = []
UNIQUE_IDENTIFIER_COLUMNS: Final[List[str]] = [
        'Военнослужащий',
        'Пол',
        'Номер телефона',
        'Социальные отношения',
        'Время последнего входа в сеть',
        'Платформа последнего входа в сеть'
    ]


@router.post('/report/')
async def report_handler(item: ClientSettings):

    moderator_id: int = item.user_id
    report_type: int = item.r_type

    path_to_temp: Path = Path.cwd() / 'reports' / 'temp'
    report_file_name: str = str(uuid.uuid4()) + '.xlsx'
    report_path: Path = path_to_temp / report_file_name

    destructive_users_data = await get_destructive_users_data_mapped_to_moderator(moderator_id)

    normal_user_data = await get_normal_users_data_mapped_to_moderator(moderator_id)

    dataframe_destructive = await generate_dataframe(destructive_users_data)
    dataframe_normal = await generate_dataframe(normal_user_data)

    dataframe_updated = dataframe_normal.merge(dataframe_destructive, on=UNIQUE_IDENTIFIER_COLUMNS, how='left')
    dataframe_updated['Количество деструктивных подписок_x'].fillna(dataframe_updated['Количество деструктивных подписок_y'], inplace=True)
    dataframe_updated = dataframe_updated.drop(['Количество деструктивных подписок_y'], axis=1)
    dataframe_updated.rename(columns={'Количество деструктивных подписок_x': 'Количество деструктивных подписок'}, inplace=True)

    running_loop = asyncio.get_running_loop()

    await running_loop.run_in_executor(None, render_xlsx_document, dataframe_updated, report_path)

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
