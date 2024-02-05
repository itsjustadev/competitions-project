from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy import create_engine, Column, String, Text, Integer, Boolean, ForeignKey
# Создаем базовый класс моделей
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    chat_id = Column(Integer, primary_key=True)
    channels = relationship('Channel', back_populates='user')


class Channel(Base):
    __tablename__ = 'channels'
    channel_id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('users.chat_id'))
    user = relationship('User', back_populates='channels')
    posts = relationship('Post', back_populates='channel')


class Post(Base):
    __tablename__ = 'posts'
    post_id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('channels.channel_id'))
    date_start = Column(DateTime)
    date_finish = Column(DateTime)
    repeat_or_not = Column(Boolean, default=False)
    text = Column(String)
    channel = relationship('Channel', back_populates='posts')


class ParticipantsUsersAndChannels(Base):
    __tablename__ = 'participants_users_channels'
    id = Column(Integer, primary_key=True)
    user_chat_id = Column(Integer)
    participant_chat_id = Column(Integer)
    channel_id = Column(Integer)


class PostsOfUsers(Base):
    __tablename__ = 'posts_of_users'
    chat_id = Column(Integer, primary_key=True)
    photo_id = Column(String, default='')
    text = Column(String, default='')
    winners_number = Column(Integer, default=0)
    video_id = Column(String, default='')
    animation_id = Column(String, default='')
    document_id = Column(String, default='')


class HasUserCronTask(Base):
    __tablename__ = 'has_user_cron_task'
    chat_id = Column(Integer, primary_key=True)
    task = Column(Boolean, default=False)


class CronTasks(Base):
    __tablename__ = 'cron_tasks'
    chat_id = Column(Integer, primary_key=True)
    every_day_week_month = Column(Integer, default=0)
