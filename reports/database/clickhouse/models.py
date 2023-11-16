from sqlalchemy import Column, Integer, BigInteger, Text
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Attachment(Base):

    __tablename__ = 'attachments'

    id = Column(BigInteger, primary_key=True)
    post_id = Column(BigInteger)
    attachment = Column(Text)
    type = Column(Integer)
