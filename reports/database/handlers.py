from typing import List

from sqlalchemy import select, join, Sequence, Row, func, and_
from sqlalchemy.sql.functions import coalesce

from .models import *
from .decorators import execute_transaction


@execute_transaction
async def get_destructive_users_data_mapped_to_moderator(
        moderator_id: int,
        **kwargs,
) -> Sequence[Row]:

    session = kwargs.get('session')

    select_stmt = select(
        UserProfile.res_id,
        coalesce(func.count(SourceUserSubscription.subscription_res_id), 0),
    ).group_by(UserProfile.res_id).select_from(
        join(User, UserMonitoringProfile, User.id == UserMonitoringProfile.id).
        join(MonitoringProfile, UserMonitoringProfile.profile_id == MonitoringProfile.profile_id).
        join(MonitoringProfileSource, UserMonitoringProfile.profile_id == MonitoringProfileSource.profile_id).
        join(UserProfile, MonitoringProfileSource.res_id == UserProfile.res_id).
        join(SourceUserSubscription, UserProfile.res_id == SourceUserSubscription.user_res_id).
        join(UserLastSeen, UserProfile.res_id == UserLastSeen.res_id)
    ).filter(and_
        (
            SourceUserSubscription.subscription_res_id.in_(select(Alerts.res_id).distinct(Alerts.res_id)),
            User.id == moderator_id
        )
    )

    result = await session.execute(select_stmt)

    return result.fetchall()


@execute_transaction
async def get_normal_users_data_mapped_to_moderator(
        moderator_id: int,
        **kwargs,
) -> Sequence[Row]:

    session = kwargs.get('session')

    select_stmt = select(
        UserProfile,
        UserLastSeen.time,
        UserLastSeen.platform,
    ).select_from(
        join(User, UserMonitoringProfile, User.id == UserMonitoringProfile.id).
        join(MonitoringProfile, UserMonitoringProfile.profile_id == MonitoringProfile.profile_id).
        join(MonitoringProfileSource, UserMonitoringProfile.profile_id == MonitoringProfileSource.profile_id).
        join(UserProfile, MonitoringProfileSource.res_id == UserProfile.res_id).
        join(UserLastSeen, UserProfile.res_id == UserLastSeen.res_id)
    ).where(User.id == moderator_id)

    result = await session.execute(select_stmt)

    return result.fetchall()
