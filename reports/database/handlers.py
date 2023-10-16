from sqlalchemy import select, join, Sequence, Row, func, case, text, desc, distinct
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
    ).filter(
        User.id == moderator_id
    )

    result = await session.execute(select_stmt)

    return result.fetchall()


@execute_transaction
async def get_subscriptions_data_mapped_to_moderator(
        moderator_id: int,
        **kwargs,
) -> Sequence[Row]:

    session = kwargs.get('session')

    select_stmt = select(
        coalesce(SourceSubscriptionProfile.subscription_name, Source.source_id).label('subscription_title'),
        func.avg(Posts.lang),
        func.avg(Posts.sentiment),
        SourceSubscriptionProfile.is_closed,
        func.count(distinct(Alerts.alert_type)).label('alerts_count')
    ).order_by(
        desc(text('alerts_count')),
        desc(text('subscription_title'))
    ).select_from(
        join(User, UserMonitoringProfile, User.id == UserMonitoringProfile.id).
        join(MonitoringProfileSource, UserMonitoringProfile.profile_id == MonitoringProfileSource.profile_id).
        join(UserProfile, UserProfile.res_id == MonitoringProfileSource.res_id).
        join(SourceUserSubscription, MonitoringProfileSource.res_id == SourceUserSubscription.user_res_id).
        join(SourceSubscriptionProfile, SourceUserSubscription.subscription_res_id == SourceSubscriptionProfile.res_id).
        join(Source, Source.res_id == SourceSubscriptionProfile.res_id).
        join(Posts, Posts.res_id == SourceSubscriptionProfile.res_id).
        outerjoin(Alerts, Alerts.res_id == SourceSubscriptionProfile.res_id)
    ).group_by(
        SourceSubscriptionProfile.res_id, Alerts.res_id
    ).filter(
        User.id == moderator_id
    )

    result = await session.execute(select_stmt)

    return result.fetchall()


"""
SQL запрос в базу для пользователей
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

"""
Запрос в базу для групп
select
    coalesce(source_subscription_profile.subscription_name, source.source_id) as subscription_title,
    avg(posts.sentiment) as subscription_sentiment,
    avg(posts.lang) as subscription_language,
    count(posts.res_id) as subscription_posts_count,
    source_subscription_profile.is_closed as subscription_availability,
    count(distinct alerts.alert_type) as subscription_status
from user
  inner join user_monitoring_profile on user_monitoring_profile.id = user.id
  inner join monitoring_profile_source ON user_monitoring_profile.profile_id = monitoring_profile_source.profile_id
  inner join source_user_profile on monitoring_profile_source.res_id = source_user_profile.res_id
  inner join source_user_subscription on source_user_profile.res_id = source_user_subscription.user_res_id
  inner join source_subscription_profile on source_subscription_profile.res_id = source_user_subscription.subscription_res_id
  inner join source on source.res_id = source_subscription_profile.res_id
  inner join posts on source_subscription_profile.res_id = posts.res_id
  left join alerts on source_subscription_profile.res_id = alerts.res_id
where user.id = 4
group by source_subscription_profile.res_id, alerts.res_id
order by subscription_status desc, subscription_title desc;
"""
