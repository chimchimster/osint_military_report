import json
import asyncio
import math
from pathlib import Path

from typing import List

from pandas import to_datetime, DataFrame

from .database import *
from .utils import *


schema_path = Path('osint_military_report') / 'reports' / 'schemas' / 'map.JSON'


async def generate_dataframe_for_users(
        users_data: List[List],
) -> DataFrame:

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

    tasks = [
        asyncio.create_task(
            prepare_subscription_data(*subscription_data)
        ) for subscription_data in subscriptions_data
    ]

    prepared_data = await asyncio.gather(*tasks)

    langs_schema = await read_schema(schema_path, 'langs')
    sentiment_schema = await read_schema(schema_path, 'sentiment')

    dataframe = DataFrame(data=prepared_data, columns=[
        'Сообщество',
        'Язык',
        'Тональность',
        'Доступность',
        'Статус',
    ])

    dataframe['Язык'] = dataframe['Язык'].fillna('Неопределен').astype(str).map(langs_schema)
    dataframe['Тональность'] = dataframe['Тональность'].astype(str).map(sentiment_schema)

    return dataframe


async def prepare_subscription_data(
        subscription_title: str,
        posts_lang: int,
        posts_sentiment: int,
        availability: bool,
        status: int,
) -> List:

    availability = 'Сообщество доступно' if not availability else 'Сообщество закрыто либо удалено'

    status = 'Содержит деструктивный контент' if status > 0 else 'Не содержит деструктивный контент'

    try:
        posts_lang = math.ceil(posts_lang) if posts_lang % 10 >= 5 else math.floor(posts_lang)
    except TypeError:
        posts_lang = 0

    try:
        posts_sentiment = math.ceil(posts_sentiment) if posts_sentiment % 10 >= 5 else math.floor(posts_sentiment)
    except TypeError:
        posts_sentiment = 0

    return [subscription_title, posts_lang, posts_sentiment, availability, status]


async def prepare_user_data(
        profile: UserProfile,
        last_seen_time_unix: int,
        platform_type: int,
        destructive_subscriptions_count: int,
) -> List:

    user_name, sex, info_json = profile.user_name, profile.sex, profile.info_json

    contacts, relation = json.loads(info_json).get('contacts'), json.loads(info_json).get('relation')

    return [user_name, sex, contacts, relation, destructive_subscriptions_count, last_seen_time_unix, platform_type]


__all__ = [
    'generate_dataframe_for_subscriptions',
    'generate_dataframe_for_users',
]