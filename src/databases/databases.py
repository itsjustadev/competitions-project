from datetime import datetime, timedelta, time
from typing import DefaultDict
from aiogram.types import user
from sqlalchemy import create_engine, Column, String, text, Integer, Boolean, ForeignKey
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import random
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from databases.models_db import *
import os
from dotenv import load_dotenv

load_dotenv()
username = str(os.getenv('USERNAME'))
password = str(os.getenv('PASSWORD'))
host = str(os.getenv('HOST'))
port = str(os.getenv('PORT'))
database = str(os.getenv('DATABASE'))

connection_string = f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}'
engine = create_engine(connection_string)

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone="Europe/Moscow")


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


# def add_member(chat: int):
#     activity = ListOfMembers(chat_id=chat)
#     session.merge(activity)
#     session.commit()


def add_user(chat: int):
    activity = User(chat_id=chat)
    session.merge(activity)
    session.commit()


def add_channel(channel_id: int, chat: int):
    activity = Channel(channel_id=channel_id, chat_id=chat)
    session.merge(activity)
    session.commit()


def add_post_to_publish(post_id: int, channel_id: int, date_start: datetime, date_finish: datetime, repeat_or_not: bool, text: str):
    activity = Post(post_id=post_id, channel_id=channel_id, date_start=date_start,
                    date_finish=date_finish, repeat_or_not=repeat_or_not, text=text)
    session.merge(activity)
    session.commit()


def find_user_for_post(post_id):
    # Находим пост
    post = session.query(Post).filter_by(post_id=post_id).first()
    if post:
        # Получаем связанный канал
        channel = post.channel
        if channel:
            # Возвращаем пользователя, связанного с каналом
            return channel.user.chat_id
    return None


def add_participant_user_channel(participant_chat_id, channel_id):
    channel = session.query(Channel).filter_by(channel_id=channel_id).first()
    if channel:
        new_record = ParticipantsUsersAndChannels(
            user_chat_id=channel.chat_id,
            participant_chat_id=participant_chat_id,
            channel_id=channel_id
        )
        session.add(new_record)
        session.commit()


def get_all_channels(chat_id):
    channels_array = []
    # Находим пост
    channels = session.query(Channel).filter_by(chat_id=chat_id).all()
    if channels:
        for item in channels:
            channels_array.append(item.channel_id)
    return channels_array if channels else None


def add_task_info(chat: int, day_week_month: int):
    activity = CronTasks(chat_id=chat, every_day_week_month=day_week_month)
    session.merge(activity)
    session.commit()


def add_prepared_post(chat: int, photo_id, text):
    activity = PostsOfUsers(chat_id=chat, photo_id=photo_id, text=text)
    session.merge(activity)
    session.commit()


def add_prepared_photo_for_post(chat: int, photo_id):
    activity = PostsOfUsers(chat_id=chat, photo_id=photo_id,
                            video_id='', animation_id='', document_id='')
    session.merge(activity)
    session.commit()


def add_prepared_video_for_post(chat: int, video_id):
    activity = PostsOfUsers(chat_id=chat, video_id=video_id,
                            photo_id='', animation_id='', document_id='')
    session.merge(activity)
    session.commit()


def add_prepared_animation_for_post(chat: int, animation_id):
    activity = PostsOfUsers(chat_id=chat, animation_id=animation_id,
                            photo_id='', video_id='', document_id='')
    session.merge(activity)
    session.commit()


def add_prepared_document_for_post(chat: int, document_id):
    activity = PostsOfUsers(chat_id=chat, document_id=document_id,
                            photo_id='', video_id='', animation_id='')
    session.merge(activity)
    session.commit()


def add_prepared_text_for_post(chat: int, text, winners_number):
    activity = PostsOfUsers(chat_id=chat, text=text,
                            winners_number=winners_number)
    session.merge(activity)
    session.commit()

# def add_user_in_cron_tasks(chat: int):
#     activity = HasUserCronTask(chat_id=chat)
#     session.merge(activity)
#     session.commit()


def add_new_cron_task(chat: int):
    activity = CronTasks(chat_id=chat)
    session.merge(activity)
    session.commit()


def check_member_exists(participant_chat_id: int, channel_id: int):
    activity = session.query(ParticipantsUsersAndChannels).filter_by(
        participant_chat_id=participant_chat_id, channel_id=channel_id).first()
    return True if activity else False


def is_repeat_needed(post_id: int):
    activity = session.query(Post).filter_by(post_id=post_id).first()
    if activity:
        return True if activity.repeat_or_not else False
    else:
        return False


def get_channel_id_by_chat_id(chat_id: int):
    channel = session.query(Channel).filter(Channel.chat_id == chat_id).first()
    return channel.channel_id if channel else None


def delete_post_from_post_table(post_id: int):
    activity = session.query(Post).filter_by(post_id=post_id).first()
    if activity:
        session.delete(activity)
        # Фиксируем изменения в базе данных
        session.commit()
    else:
        pass


def check_user_has_cron_task(chat: int):
    activity = session.query(CronTasks).filter_by(chat_id=chat).first()
    return str(activity.chat_id) if activity else False


def get_text_from_post(chat: int):
    activity = session.query(PostsOfUsers).filter_by(chat_id=chat).first()
    return str(activity.text) if activity else False


def get_message_text_from_publication(post_id: int):
    activity = session.query(Post).filter_by(post_id=post_id).first()
    return str(activity.text) if activity else False


def get_winners_number_from_post(chat: int):
    activity = session.query(PostsOfUsers).filter_by(chat_id=chat).first()
    return str(activity.winners_number) if activity else False


def get_photo_id_from_post(chat: int):
    activity = session.query(PostsOfUsers).filter_by(chat_id=chat).first()
    return str(activity.photo_id) if activity else False


def get_video_id_from_post(chat: int):
    activity = session.query(PostsOfUsers).filter_by(chat_id=chat).first()
    return str(activity.video_id) if activity else False


def get_animation_id_from_post(chat: int):
    activity = session.query(PostsOfUsers).filter_by(chat_id=chat).first()
    return str(activity.animation_id) if activity else False


def get_document_id_from_post(chat: int):
    activity = session.query(PostsOfUsers).filter_by(chat_id=chat).first()
    return str(activity.document_id) if activity else False


def get_day_week_or_month(chat: int):
    activity = session.query(CronTasks).filter_by(chat_id=chat).first()
    return activity.every_day_week_month if activity else False


# def get_member(row_number: int):
#     member = session.query(ParticipantsUsersAndChannels.chat_id).offset(
#         row_number).limit(1).first()
#     # Возвращаем chat_id, если запись найдена, иначе возвращаем None.
#     return member.chat_id if member else None


def get_all_participants(channel_id):
    list_of_participants = []
    member = session.query(ParticipantsUsersAndChannels).filter_by(
        channel_id=channel_id).all()
    if member:
        for item in member:
            list_of_participants.append(item.participant_chat_id)
    # Возвращаем chat_id, если запись найдена, иначе возвращаем None.
    return list_of_participants


def delete_all_participants(channel_id):
    member = session.query(ParticipantsUsersAndChannels).filter_by(
        channel_id=channel_id)
    if member:
        member.delete()
        session.commit()


# def count_members():
#     activity = session.query(ListOfMembers).all()
#     counter = 0
#     if activity:
#         for item in activity:
#             counter += 1
#     return counter


def get_random_numbers(count_result, number_of_winners):
    count_result = count_result - 1
    n = count_result  # Example value for n
    count = number_of_winners  # Number of unique random numbers to generate

    # Check if count is not greater than the range of numbers
    if count > n + 1:
        return 0

    # Create a list of numbers from 0 to n
    numbers = list(range(n + 1))

    # Shuffle the list and take the first 'count' numbers to ensure uniqueness
    random.shuffle(numbers)
    unique_random_numbers = numbers[:count]
    return unique_random_numbers


def delete_channel(channel_id):
    channel = session.query(Channel).filter_by(
        channel_id=channel_id)
    if channel:
        channel.delete()
        session.commit()


def get_first_media_id(chat_id):
    result = session.query(
        PostsOfUsers.photo_id,
        PostsOfUsers.video_id,
        PostsOfUsers.animation_id,
        PostsOfUsers.document_id
    ).filter(PostsOfUsers.chat_id == chat_id).first()
    if result:
        if result.photo_id:
            return result.photo_id, 'photo'
        elif result.video_id:
            return result.video_id, 'video'
        elif result.animation_id:
            return result.animation_id, 'animation'
        elif result.document_id:
            return result.document_id, 'document'
    return None, None


# def get_winners(random_numbers):
#     unique_random_numbers = random_numbers
#     winners_chat_ids = []
#     if unique_random_numbers:
#         for item in unique_random_numbers:
#             member_chat_id = get_member(item)
#             winners_chat_ids.append(member_chat_id)
#     return winners_chat_ids

# print(get_winners([2, 1, 0]))


def find_indixes(elements, reference_array):
    # Создаем словарь, где ключи - это элементы `reference_array`, а значения - их индексы
    reference_dict = {element: idx for idx,
                      element in enumerate(reference_array)}

    # Используем словарь для быстрого поиска индексов
    indixes = [reference_dict[element]
               for element in elements if element in reference_dict]

    return indixes


def replace_number(array, table_size, index_to_replace):
    # Генерация множества всех возможных номеров записей
    possible_numbers = set(range(table_size))
    # Удаление номеров, которые уже есть в массиве
    possible_numbers -= set(array)
    # Выбор случайного номера для замены
    replacement_number = random.choice(list(possible_numbers))
    # Замена выбранного числа в массиве на новое
    array[index_to_replace] = replacement_number
    return array


session.close()
