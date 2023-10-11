from fastapi import APIRouter, File

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
    print(normal_user_data)
    print(await render_lxml_document(normal_user_data))


    return item


__all__ = [
    'router',
]
