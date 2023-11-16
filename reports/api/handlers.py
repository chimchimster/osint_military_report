from fastapi import APIRouter

from .models import ClientSettings
from reports.tasks import ReportDistributor

router = APIRouter()


@router.post('/report/')
async def report_handler(item: ClientSettings):

    distributor = ReportDistributor(item)

    response_file = await distributor.generate_report()

    return response_file


__all__ = [
    'router',
]
