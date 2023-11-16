from sqlalchemy import Column, Integer, ForeignKey, String, SmallInteger, Date, Text, JSON, BigInteger, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    monitoring_profiles = relationship('UserMonitoringProfile', back_populates='user', uselist=True)


class UserMonitoringProfile(Base):

    __tablename__ = 'user_monitoring_profile'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    profile_id = Column(Integer, ForeignKey('monitoring_profile.profile_id'))

    user = relationship('User', back_populates='monitoring_profiles', uselist=False)
    profile = relationship('MonitoringProfile', back_populates='monitoring_profiles', uselist=True)


class MonitoringProfile(Base):

    __tablename__ = 'monitoring_profile'

    profile_id = Column(Integer, primary_key=True)
    monitoring_profiles = relationship('UserMonitoringProfile', back_populates='profile', uselist=False)
    monitoring_profile_source = relationship('MonitoringProfileSource', back_populates='profile', uselist=False)


class MonitoringProfileSource(Base):

    __tablename__ = 'monitoring_profile_source'

    profile_id = Column(Integer, ForeignKey('monitoring_profile.profile_id'), primary_key=True)
    res_id = Column(Integer, ForeignKey('source_user_profile.res_id'), primary_key=True)

    profile = relationship('MonitoringProfile', back_populates='monitoring_profile_source', uselist=False)
    user = relationship('UserProfile', back_populates='monitoring_profile_source', uselist=False)


class UserProfile(Base):

    __tablename__ = 'source_user_profile'

    res_id = Column(Integer, primary_key=True)
    user_name = Column(String(length=255))
    deactivated = Column(Integer)
    is_closed = Column(SmallInteger)
    sex = Column(Integer)
    birth_date = Column(Date)
    profile_image = Column(Text)
    info_json = Column(JSON)

    monitoring_profile_source = relationship('MonitoringProfileSource', back_populates='user', uselist=False)


class SourceUserSubscription(Base):

    __tablename__ = 'source_user_subscription'

    user_res_id = Column(Integer, primary_key=True)
    subscription_res_id = Column(Integer)


class UserLastSeen(Base):

    __tablename__ = 'user_last_seen'

    res_id = Column(Integer, primary_key=True)
    time = Column(BigInteger)
    platform = Column(Integer)


class Alerts(Base):

    __tablename__ = 'alerts'

    res_id = Column(Integer, primary_key=True)
    alert_type = Column(Integer)


class SourceSubscriptionProfile(Base):

    __tablename__ = 'source_subscription_profile'

    res_id = Column(Integer, primary_key=True)
    subscription_name = Column(String(length=255))
    members_count = Column(Integer)
    is_closed = Column(Boolean)


class Source(Base):

    __tablename__ = 'source'

    res_id = Column(Integer, primary_key=True)
    source_id = Column(Integer)
    soc_type = Column(Integer)
    source_type = Column(Integer)


class Posts(Base):

    __tablename__ = 'posts'

    res_id = Column(Integer, primary_key=True)
    lang = Column(Integer)
    sentiment = Column(Integer)
    post_type = Column(Integer)


__all__ = [
    'UserProfile',
    'MonitoringProfileSource',
    'UserMonitoringProfile',
    'MonitoringProfile',
    'User',
    'SourceUserSubscription',
    'UserLastSeen',
    'Alerts',
    'SourceSubscriptionProfile',
    'Source',
    'Posts',
]
