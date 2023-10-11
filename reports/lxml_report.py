import asyncio
import json

from typing import List, Tuple

from .database import *


async def render_lxml_document(users_data: List[Tuple[UserProfile, int, int, int]]):

    tasks = [asyncio.create_task(prepare_data(*user_data)) for user_data in users_data]

    prepared_data = await asyncio.gather(*tasks)

    print(prepared_data)


async def prepare_data(
        profile: UserProfile,
        last_seen_time_unix: int,
        platform_type: int,
):

    user_name, sex, info_json = profile.user_name, profile.sex, profile.info_json

    contacts, relation = json.loads(info_json).get('contacts'), json.loads(info_json).get('relation')

    return [user_name, sex, contacts, relation, 0, last_seen_time_unix, platform_type]
