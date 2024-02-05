from aiogram.fsm.state import State, StatesGroup
import os
from dotenv import load_dotenv


load_dotenv()
BOT_TOKEN = str(os.getenv('TOKEN_FOR_BOT'))


class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


class Competition(StatesGroup):
    waiting_for_participant_count = State()
    get_winners = State()


class Channel(StatesGroup):
    adding_channel = State()
    channel_chosed = State()


class CompetitionPost(StatesGroup):
    prizes = State()
    date_time_start = State()
    date_time_finish = State()
    repeat_or_not = State()
    repeat_yes = State()
    content = State()  # Содержимое поста
    change_text = State()  # Содержимое поста
    pin_or_not = State()  # Содержимое поста


TEXT_STANDARD_TEMPLATE = '''Как насчет призов за подписку?

Мы решили разыграть {number_winners} приз{ending}:
{string_with_prizes}!

Чтобы выиграть, нужно:
1. Отправить этот пост 3 своим друзьям;
2. Нажать кнопку УЧАСТВУЮ.

{number_winners} победител{ending2} выберем {date_time_finish}
случайным образом. Всем удачи!'''
