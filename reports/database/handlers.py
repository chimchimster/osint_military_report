from sqlalchemy import select, join, Sequence, Row, func, case, text
from sqlalchemy.sql.functions import coalesce

from .models import *
from .decorators import execute_transaction


@execute_transaction
async def get_users_data_mapped_to_moderator(
        moderator_id: int,
        **kwargs,
) -> Sequence[Row]:

    session = kwargs.get('session')

    select_stmt = select(
        UserProfile,
        UserLastSeen.time,
        UserLastSeen.platform,
        coalesce(func.sum(
            case((SourceUserSubscription.subscription_res_id.in_(select(Alerts.res_id)), 1), else_=0)
        ), 0).alias('s_c')
    ).select_from(
        join(User, UserMonitoringProfile, User.id == UserMonitoringProfile.id).
        join(MonitoringProfile, UserMonitoringProfile.profile_id == MonitoringProfile.profile_id).
        join(MonitoringProfileSource, UserMonitoringProfile.profile_id == MonitoringProfileSource.profile_id).
        join(UserProfile, MonitoringProfileSource.res_id == UserProfile.res_id).
        outerjoin(SourceUserSubscription, UserProfile.res_id == SourceUserSubscription.user_res_id).
        outerjoin(UserLastSeen, UserProfile.res_id == UserLastSeen.res_id).
        outerjoin(Alerts, Alerts.res_id == UserLastSeen.res_id)
    ).where(User.id == moderator_id).group_by(
            UserProfile.user_name, UserLastSeen.time, UserLastSeen.platform
        ).order_by(text('s_c'))

    result = await session.execute(select_stmt)

    return result.fetchall()