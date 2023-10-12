from fastapi import APIRouter
from fastapi.responses import FileResponse

from .utils import *
from .database import *
from .models import ClientSettings
from .lxml_report import render_lxml_document

router = APIRouter()


@router.post('/report/')
async def report_handler(item: ClientSettings):

    moderator_id: int = item.user_id
    report_type: int = item.r_type

    destructive_users_data = await get_destructive_users_data_mapped_to_moderator(moderator_id)

    normal_user_data = await get_normal_users_data_mapped_to_moderator(moderator_id)

    await render_lxml_document(normal_user_data)

    response_file = FileResponse(path='output.xlsx', filename='Отчет военнослужащие.xlsx', media_type='multipart/form-data')

    # await remove_report()

    return response_file

__all__ = [
    'router',
]
