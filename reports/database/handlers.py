from sqlalchemy import select, join, Sequence, Row, func, case, text, desc
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
        ), 0).label('subscriptions_count')
    ).order_by(desc(text('subscriptions_count'))).select_from(
        join(User, UserMonitoringProfile, User.id == UserMonitoringProfile.id).
        join(MonitoringProfile, UserMonitoringProfile.profile_id == MonitoringProfile.profile_id).
        join(MonitoringProfileSource, UserMonitoringProfile.profile_id == MonitoringProfileSource.profile_id).
        join(UserProfile, MonitoringProfileSource.res_id == UserProfile.res_id).
        outerjoin(SourceUserSubscription, UserProfile.res_id == SourceUserSubscription.user_res_id).
        outerjoin(UserLastSeen, UserProfile.res_id == UserLastSeen.res_id).
        outerjoin(Alerts, Alerts.res_id == UserLastSeen.res_id)
    ).group_by(
            UserProfile.user_name, UserLastSeen.time, UserLastSeen.platform
        ).filter(User.id == moderator_id)

    result = await session.execute(select_stmt)

    return result.fetchall()

"""
SQL запрос в базу 
SELECT
    sp2.user_name,
    uls.time,
    uls.platform,
    SUM(
        CASE WHEN sbc1.subscription_res_id IN (
        	SELECT alerts.res_id FROM alerts
    ) THEN 1 ELSE 0 END
       ) AS alerts_count
FROM user AS u
	INNER JOIN user_monitoring_profile ON u.id = user_monitoring_profile.id
	INNER JOIN monitoring_profile ON monitoring_profile.profile_id = user_monitoring_profile.profile_id
	INNER JOIN monitoring_profile_source ON user_monitoring_profile.profile_id = monitoring_profile_source.profile_id
	INNER JOIN source_user_profile AS sp2 ON sp2.res_id = monitoring_profile_source.res_id
	LEFT JOIN source_user_subscription AS sbc1 ON sbc1.user_res_id = sp2.res_id
	LEFT JOIN user_last_seen AS uls ON uls.res_id = sbc1.user_res_id
	LEFT JOIN alerts as alrt ON alrt.res_id = uls.res_id
WHERE u.id = 2
GROUP BY sp2.user_name, uls.time, uls.platform
ORDER BY alerts_count DESC; 
"""