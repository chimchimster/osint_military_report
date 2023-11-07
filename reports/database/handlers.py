from sqlalchemy import select, join, Sequence, Row, func, case, text, desc, distinct
from sqlalchemy.orm import aliased
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
        case(
            (
                Source.soc_type == 1, func.concat('https://vk.com/public', Source.source_id)),
            else_=func.concat(
                'https://instagram.com/',
                text("""trim(both '"' from json_extract(source_subscription_profile.info_json, '$.username'))""")
            )
        ),
        Source.soc_type,
        text("""
        (select lang
             from (
                 select count(*) as cnt
                 from posts
                    inner join source_subscription_profile on posts.res_id = source_subscription_profile.res_id
                 where source_subscription_profile.res_id = posts.res_id
                 group by posts.lang
                 order by cnt desc
                 limit 1
             ) AS subquery
         ) AS mode_lang
        """),
        func.avg(Posts.sentiment),
        SourceSubscriptionProfile.is_closed,
        func.group_concat(distinct(Alerts.alert_type)).label('alerts_count')
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
        outerjoin(Posts, Posts.res_id == SourceSubscriptionProfile.res_id).
        outerjoin(Alerts, Alerts.res_id == SourceSubscriptionProfile.res_id)
    ).group_by(
        SourceSubscriptionProfile.res_id, Alerts.res_id
    ).filter(
        User.id == moderator_id
    )

    result = await session.execute(select_stmt)

    return result.fetchall()


@execute_transaction
async def get_users_data_for_counters(moderator_id: int, **kwargs) -> Sequence[Row]:
    session = kwargs.get('session')

    select_stmt = select(
        UserMonitoringProfile.profile_id,
        MonitoringProfileSource.res_id,
        SourceUserSubscription.subscription_res_id,
        Source.soc_type,
        Source.source_type,
        Alerts.alert_type
    ).select_from(
        join(
            UserMonitoringProfile,
            MonitoringProfileSource,
            MonitoringProfileSource.profile_id == UserMonitoringProfile.profile_id
        ).
        outerjoin(SourceUserSubscription, SourceUserSubscription.user_res_id == MonitoringProfileSource.res_id).
        outerjoin(Source, SourceUserSubscription.subscription_res_id == Source.res_id).
        outerjoin(Alerts, Alerts.res_id == SourceUserSubscription.subscription_res_id)
    ).filter(
        UserMonitoringProfile.id == moderator_id
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
    (case 
    when source.soc_type = 1 then 
        concat('https://vk.com/', source.source_id) 
    else 
        concat('https://instagram.com/', json_extract(source_subscription_profile.info_json, '$.username')) 
	end) as link,
    source.soc_type as social_type,
    avg(posts.sentiment) as subscription_sentiment,
    (select lang
        from (
            select count(*) as cnt
            from posts
            	inner join source_subscription_profile on posts.res_id = source_subscription_profile.res_id
            where source_subscription_profile.res_id = posts.res_id
            group by posts.lang
            order by cnt desc
            limit 1
        ) AS subquery
    ) AS mode_lang,
    count(posts.res_id) as subscription_posts_count,
    source_subscription_profile.is_closed as subscription_availability,
    group_concat(distinct alerts.alert_type) as subscription_status
from user
  inner join user_monitoring_profile on user_monitoring_profile.id = user.id
  inner join monitoring_profile_source ON user_monitoring_profile.profile_id = monitoring_profile_source.profile_id
  inner join source_user_profile on monitoring_profile_source.res_id = source_user_profile.res_id
  inner join source_user_subscription on source_user_profile.res_id = source_user_subscription.user_res_id
  inner join source_subscription_profile on source_subscription_profile.res_id = source_user_subscription.subscription_res_id
  inner join source on source.res_id = source_subscription_profile.res_id
  left join posts on source_subscription_profile.res_id = posts.res_id
  left join alerts on source_subscription_profile.res_id = alerts.res_id
where user.id = 1
group by source_subscription_profile.res_id, alerts.res_id
order by subscription_status desc, subscription_title desc, source.soc_type desc;
"""

"""
SELECT ump.profile_id, mps.res_id, sus.user_res_id, sus.subscription_res_id, s.soc_type, s.source_type, a.alert_type
FROM user_monitoring_profile AS ump
LEFT JOIN monitoring_profile_source AS mps ON ump.profile_id = mps.profile_id
LEFT JOIN source_user_subscription as sus ON sus.user_res_id = mps.res_id
LEFT JOIN source as s ON sus.subscription_res_id = s.res_id
LEFT JOIN alerts as a ON a.res_id = sus.subscription_res_id
WHERE ump.id = moderator_id;
"""

"""
НА ДОРАБОТКЕ
select 
    MP.full_name as f_name, 
    group_concat(
        case when S.source_type = 1 and S.soc_type = 1 then concat('https://vk.com/id', S.source_id) else null end
        order by S.res_id asc separator ' '
    ) as vk_res_ids,
    group_concat(
      concat('https://instagram.com/', json_unquote(json_extract(SSP.info_json, '$.username')))
        order by SSP.res_id asc separator ' '
    ) as inst_res_ids
from monitoring_profile as MP
    left join monitoring_profile_source as MPS using(profile_id)
    left join source as S using(res_id)
    left join source_subscription_profile as SSP using(res_id)
group by f_name;
"""