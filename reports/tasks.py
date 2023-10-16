import asyncio
import uuid
from datetime import datetime

from pathlib import Path
from typing import List, Final

from fastapi.responses import FileResponse

from .models import ClientSettings
from .database import *
from .xlsx_report import *
from .dataframes import *
from .utils import *


REPORT_STACK_LOCK = asyncio.Lock()
PREVIOUS_REPORTS_STACK: Final[List[str]] = []


class ReportDistributor:

    __slots__ = ('resp_obj', 'report_path',)

    path_to_temp: Path = Path.cwd() / 'reports' / 'temp'

    def __init__(self, resp_obj: ClientSettings):
        self.resp_obj = resp_obj

    async def generate_report(self) -> FileResponse:
        """ r_type: тип отчета. 1 - пользователи, 2 - подписки.
            r_format: формат отчета. xlsx, pdf, pptx, csv.
            user_id: идентификатор модератора в системе. """

        r_type = self.resp_obj.r_type
        r_format = self.resp_obj.r_format
        user_id = self.resp_obj.user_id

        report_file_name: str = str(uuid.uuid4()) + '.' + r_format
        report_path: Path = self.path_to_temp / report_file_name

        if r_type == 1:

            users_data = await get_users_data_mapped_to_moderator(user_id)

            dataframe = await generate_dataframe_for_users(users_data)

        elif r_type == 2:

            subscriptions_data = await get_subscriptions_data_mapped_to_moderator(user_id)

            dataframe = await generate_dataframe_for_subscriptions(subscriptions_data)

        else:
            raise RuntimeError(f'Непредусмотренный тип {r_type} отчета.')

        running_loop = asyncio.get_running_loop()

        if r_format == 'xlsx':

            await running_loop.run_in_executor(None, render_xlsx_document, dataframe, report_path)

        filename = f'Отчет от {datetime.now()} военнослужащие.{r_format}'

        response_file = FileResponse(
            path=report_path,
            filename=filename,
            media_type='multipart/form-data',
        )

        async with REPORT_STACK_LOCK:
            if PREVIOUS_REPORTS_STACK:
                prev_report_name = PREVIOUS_REPORTS_STACK.pop()
                await remove_report(self.path_to_temp, prev_report_name)

            PREVIOUS_REPORTS_STACK.append(report_file_name)

        return response_file
