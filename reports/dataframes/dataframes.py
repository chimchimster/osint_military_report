import json
import asyncio
import math
from pathlib import Path

from typing import List, Final, Dict

import pandas as pd
from pandas import to_datetime, DataFrame

from osint_military_report.reports.database import *
from reports.utils.utils import *

schema_path = Path('/home/newuser/osint_military_reports/osint_military_report/reports/schemas/map.JSON')

STATUSES: Final[Dict] = {
    "1": "Лудомания",
    "2": "Суицид\Депрессия",
    "3": "Религиозный радикализм",
    "4": "Сексуальная девиация"
}


async def generate_dataframe_for_users(
        users_data: List[List],
) -> DataFrame:
    """

    :param users_data:
    :return:
    """
    tasks = [
        asyncio.create_task(
            prepare_user_data(*user_data)
        ) for user_data in users_data
    ]

    prepared_data = await asyncio.gather(*tasks)

    sex_schema = await read_schema(schema_path, 'sex')
    relation_schema = await read_schema(schema_path, 'relation')
    platform_schema = await read_schema(schema_path, 'platform')

    dataframe = DataFrame(data=prepared_data, columns=[
        'Имя в аккаунте',
        'Пол',
        'Номер телефона',
        'Социальные отношения',
        'Количество деструктивных подписок',
        'Время последнего входа в сеть',
        'Платформа последнего входа в сеть',
    ])

    dataframe['Пол'] = dataframe['Пол'].fillna(0).astype(int)
    dataframe['Пол'] = dataframe['Пол'].astype(str).map(sex_schema).fillna(dataframe['Пол'])

    dataframe['Социальные отношения'] = (dataframe['Социальные отношения']
                                         .fillna(0).astype(int))

    dataframe['Социальные отношения'] = (dataframe['Социальные отношения'].
                                         astype(str).map(relation_schema).fillna(dataframe['Социальные отношения']))

    dataframe['Платформа последнего входа в сеть'] = (dataframe['Платформа последнего входа в сеть']
                                                      .fillna(0).astype(int))

    dataframe['Платформа последнего входа в сеть'] = (dataframe['Платформа последнего входа в сеть']
                                                      .astype(str).map(platform_schema)
                                                      .fillna(dataframe['Платформа последнего входа в сеть']))

    dataframe['Время последнего входа в сеть'] = to_datetime(dataframe['Время последнего входа в сеть'], unit='s')
    dataframe['Время последнего входа в сеть'] = (dataframe['Время последнего входа в сеть']
                                                  .dt.strftime('%d-%m-%Y %H:%M:%S'))

    return dataframe


async def generate_dataframe_for_subscriptions(
        subscriptions_data: List[List]
) -> DataFrame:
    """

    :param subscriptions_data:
    :return:
    """

    tasks = [
        asyncio.create_task(
            prepare_subscription_data(*subscription_data)
        ) for subscription_data in subscriptions_data
    ]

    prepared_data = await asyncio.gather(*tasks)

    langs_schema = await read_schema(schema_path, 'langs')
    sentiment_schema = await read_schema(schema_path, 'sentiment')
    social_media_schema = await read_schema(schema_path, 'social media type')

    dataframe = DataFrame(data=prepared_data, columns=[
        'Сообщество',
        'Ссылка',
        'Соцсеть',
        'Язык',
        'Тональность',
        'Доступность',
        'Статус',
        'Изображение',
        'Ссылки',
        'Видео',
        'Аудио',
        'Файлы',
        'Текст',
    ])

    dataframe['Язык'] = dataframe['Язык'].fillna('Неопределен').astype(str).map(langs_schema)
    dataframe['Тональность'] = dataframe['Тональность'].astype(str).map(sentiment_schema)
    dataframe['Соцсеть'] = dataframe['Соцсеть'].astype(str).map(social_media_schema)

    return dataframe


async def prepare_subscription_data(
        subscription_title: str,
        subscription_link: str,
        soc_type: str,
        posts_lang: int,
        posts_sentiment: int,
        availability: bool,
        status: str,
        pics_count: int,
        links_count: int,
        video_count: int,
        audio_count: int,
        files_count: int,
        text_count: int,
) -> List:
    """

    :param text_count:
    :param files_count:
    :param audio_count:
    :param video_count:
    :param links_count:
    :param pics_count:
    :param subscription_title:
    :param subscription_link:
    :param soc_type:
    :param posts_lang:
    :param posts_sentiment:
    :param availability:
    :param status:
    :return:
    """
    availability = 'Сообщество доступно' if not availability else 'Сообщество закрыто либо удалено'

    if status:
        status = ','.join([STATUSES[st] for st in status.split(',')])

    try:
        posts_lang = math.ceil(posts_lang) if posts_lang % 10 >= 5 else math.floor(posts_lang)
    except TypeError:
        posts_lang = 0

    try:
        posts_sentiment = math.ceil(posts_sentiment) if posts_sentiment % 10 >= 5 else math.floor(posts_sentiment)
    except TypeError:
        posts_sentiment = 0

    return [
        subscription_title,
        subscription_link,
        soc_type,
        posts_lang,
        posts_sentiment,
        availability,
        status,
        pics_count,
        links_count,
        video_count,
        audio_count,
        files_count,
        text_count,
    ]


async def prepare_user_data(
        profile: UserProfile,
        last_seen_time_unix: int,
        platform_type: int,
        destructive_subscriptions_count: int,
) -> List:
    """

    :param profile:
    :param last_seen_time_unix:
    :param platform_type:
    :param destructive_subscriptions_count:
    :return:
    """
    user_name, sex, info_json = profile.user_name, profile.sex, profile.info_json

    try:
        relation = json.loads(info_json).get('relation')
    except TypeError:
        info_json = json.dumps(info_json)
        relation = json.loads(info_json).get('relation')

    contacts = json.loads(info_json).get('contacts')

    return [user_name, sex, contacts, relation, destructive_subscriptions_count, last_seen_time_unix, platform_type]


async def generate_dataframe_for_counters(subscriptions_data: List[List]):
    return pd.DataFrame(
        subscriptions_data,
        columns=[
            'profile_id',
            'user_res_id',
            'subscription_res_id',
            'soc_type',
            'source_type',
            'alert_type'
        ]
    )

__all__ = [
    'generate_dataframe_for_subscriptions',
    'generate_dataframe_for_users',
    'generate_dataframe_for_counters',
]
