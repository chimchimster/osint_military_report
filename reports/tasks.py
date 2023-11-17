import uuid
import asyncio
from hashlib import md5
from datetime import datetime

from pathlib import Path
from typing import Final, Dict
from collections import defaultdict

from fastapi.responses import FileResponse

from reports.api.models import ClientSettings
from reports.database import *
from reports.builders.xlsx_report import *
from reports.builders.csv_report import *
from reports.builders.pptx_report import *
from reports.builders.pdf_report import *
from reports.dataframes.dataframes import *
from reports.utils.utils import *

REPORT_STACK_LOCK = asyncio.Lock()
PREVIOUS_REPORTS_STACK: Final[Dict] = defaultdict(list)

PATH_TO_TEMPLATE: Path = Path('osint_military_report') / 'reports' / 'templates'


class ReportDistributor:
    __slots__ = ('resp_obj', 'report_path',)

    path_to_temp: Path = Path('osint_military_report') / 'reports' / 'temp'

    def __init__(self, resp_obj: ClientSettings):
        self.resp_obj = resp_obj

    async def generate_report(self) -> FileResponse:
        """ r_type: тип отчета. 1 - пользователи, 2 - подписки.
            r_format: формат отчета. xlsx, pdf, pptx, csv.
            user_id: идентификатор модератора в системе. """

        r_type = self.resp_obj.r_type
        r_format = self.resp_obj.r_format
        user_id = self.resp_obj.user_id

        report_file_name: str = f'{uuid.uuid4()}-{md5(str(datetime.now()).encode()).hexdigest()}.{r_format}'
        report_path: Path = self.path_to_temp / report_file_name

        if r_format == 'pptx':
            users_data = await get_users_data_for_counters(user_id)

            dataframe = await generate_dataframe_for_counters(users_data)

        elif r_format == 'pdf':
            top_10_sources_data = await top_10_sources()

        elif r_type == 1:

            users_data = await get_users_data_mapped_to_moderator(user_id)

            dataframe = await generate_dataframe_for_users(users_data)

        elif r_type == 2:

            subscriptions_data = await get_subscriptions_data_mapped_to_moderator(user_id)

            dataframe = await generate_dataframe_for_subscriptions(subscriptions_data)

        else:
            raise RuntimeError(f'Непредусмотренный тип {r_type} отчета.')

        running_loop = asyncio.get_running_loop()
        if r_format == 'pdf':
            await running_loop.run_in_executor(None, render_pdf_document, top_10_sources_data, report_path)

        if r_format == 'pptx':
            await running_loop.run_in_executor(None, render_pptx_document, dataframe, report_path,
                                               PATH_TO_TEMPLATE / 'pptx_template.pptx')
        if r_format == 'xlsx':
            await running_loop.run_in_executor(None, render_xlsx_document, dataframe, report_path)

        if r_format == 'csv':
            await running_loop.run_in_executor(None, render_csv_document, dataframe, report_path)

        filename = f'Отчет от {datetime.now().strftime("%d-%m-%Y %H:%M:%S")} военнослужащие.{r_format}'

        response_file = FileResponse(
            path=report_path,
            filename=filename,
            media_type='multipart/form-data',
        )

        async with REPORT_STACK_LOCK:
            if PREVIOUS_REPORTS_STACK[user_id]:
                prev_report_name = PREVIOUS_REPORTS_STACK[user_id].pop()
                await remove_report(self.path_to_temp, prev_report_name)

            PREVIOUS_REPORTS_STACK[user_id].append(report_file_name)

        return response_file
