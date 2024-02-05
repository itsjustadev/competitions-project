from aiogram import types
import re
from aiogram.utils.markdown import hlink
import databases
import random
import logging
from aiogram.types import ChatMemberAdministrator
from databases.databases import scheduler
import databases.databases as databases
from buttons import keyboard8, keyboard13
from aiogram import Bot, Dispatcher, types, Router, F
from buttons import *
import logging
from aiogram import Bot, Dispatcher, types
from typing import Any
import random
from databases.databases import scheduler
from constants_and_helpers import *
from functions_helpers import *


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - Line %(lineno)d',
                    filename='bot.log',  # Указываем имя файла для логгирования
                    filemode='a')


async def show_main_menu_function(chat_id, state, bot):
    message = await bot.send_message(chat_id, 'Выберите необходимое действие по кнопке:', reply_markup=keyboard15)
    await state.update_data(old_message_id=message.message_id)


async def adding_new_channel(channel_id, message, state, bot):
    is_bot_admin = await check_if_bot_is_admin(channel_id, bot)
    if is_bot_admin is True:
        databases.add_channel(channel_id, message.chat.id)
        await bot.send_message(message.chat.id, "Все в порядке, канал добавлен!", reply_markup=keyboard8)
        await state.set_state(None)
    else:
        await bot.send_message(message.chat.id, "Попробуйте проверить что бот является админом и у него есть право на отправку сообщений, затем снова нажмите 'добавить канал'")
        await state.set_state(None)


def insert_links_into_text(message: types.Message):
    try:
        text = message.text
        if message.entities and text:
            # Сортируем сущности в обратном порядке, чтобы индексы вставки оставались корректными
            for entity in sorted(message.entities, key=lambda e: e.offset, reverse=True):
                if entity.type == "text_link":
                    # Определяем индекс конца слова-ссылки
                    end_index = entity.offset + entity.length
                    # Проверяем, является ли следующий символ пробелом или переносом строки
                    following_char = text[end_index-1]
                    if following_char in [' ', '\n']:
                        # Вставляем ссылку в круглых скобках и дублируем следующий символ
                        text = text[:end_index] + f"({entity.url})" + \
                            following_char + \
                            text[end_index:]
                    else:
                        # Вставляем ссылку в круглых скобках
                        text = text[:end_index] + \
                            f"({entity.url})" + text[end_index:]
        return text
    except:
        return ''


def hide_links_into_words(text):
    try:
        # Использование регулярного выражения для поиска паттернов "слово(ссылка)"
        pattern = r'\b(\w+)\s*\(\s*(https?://[^\s)]+)\s*\)'

        # Функция для замены найденных шаблонов
        def replace_pattern(match):
            word, url = match.groups()
            return hlink(word, url)

        # Замена всех найденных шаблонов в тексте
        return re.sub(pattern, replace_pattern, text)
    except:
        return ''


async def participants_with_username(participants, bot):
    new_array = participants.copy()
    elements_to_delete = []
    for chat_id in participants:
        try:
            if chat_id:
                chat = await bot.get_chat(chat_id=chat_id)
                if chat.username:
                    continue
                else:
                    elements_to_delete.append(chat_id)
            else:
                elements_to_delete.append(chat_id)
        except Exception as e:
            elements_to_delete.append(chat_id)
    for element in elements_to_delete:
        new_array.remove(element)
    return new_array


async def get_just_winners(winners_number, channel_id, bot):
    winners_list = []
    # Пытаемся преобразовать текст в число
    try:
        participants = databases.get_all_participants(channel_id)
        available_participants = await participants_with_username(participants, bot)
        members_count = len(available_participants)
        if winners_number:
            number_of_winners = int(winners_number)
            while number_of_winners > members_count:
                number_of_winners -= 1
            if number_of_winners:
                winners = random.sample(
                    available_participants, number_of_winners)
                for item in winners:
                    chat = await bot.get_chat(chat_id=item)
                    winners_list.append('@'+str(chat.username))
        return winners_list
    except Exception as e:
        logging.error(f"Произошла ошибка: {str(e)}", exc_info=True)


async def check_if_bot_is_admin(channel_id: int, bot):
    try:
        # Получение информации о канале
        chat = await bot.get_chat(channel_id)
        # Получение списка администраторов
        admins = await bot.get_chat_administrators(chat.id)
        # Проверка, есть ли бот среди администраторов и имеет ли права на отправку сообщений
        for admin in admins:
            if admin.user.id == bot.id:
                # Если бот является владельцем, он автоматически имеет все права
                if isinstance(admin, types.ChatMemberOwner):
                    return True
                # Проверяем, есть ли у бота права на отправку сообщений (если он не владелец)
                elif isinstance(admin, ChatMemberAdministrator) and admin.can_post_messages:
                    return True
        return False
    except Exception as e:
        print("Канал не найден")
        return False


async def choosing_channels(chat_id, message, bot):
    try:
        channels_array = databases.get_all_channels(chat_id)
        if channels_array:
            channel_ids_and_titles = {}
            for channel_id in channels_array:
                try:
                    chat = await bot.get_chat(channel_id)
                    if await check_if_bot_is_admin(channel_id, bot):
                        channel_ids_and_titles[channel_id] = chat.title
                    else:
                        databases.delete_channel(channel_id)
                        await bot.send_message(chat_id, f'В канале "{chat.title}" бот не является админом, добавьте этот канал снова, если он нужен для проведения в нем конкурсов')
                except:
                    continue
            if channel_ids_and_titles:
                buttons = [[types.InlineKeyboardButton(
                    text=str(value), callback_data=str(key))] for key, value in channel_ids_and_titles.items()]
                keyboard00 = types.InlineKeyboardMarkup(
                    inline_keyboard=buttons)
                if message:
                    message_id = message.message_id
                    await bot.edit_message_text('Пожалуйста, выберите канал для нового конкурса.', chat_id=chat_id, message_id=message_id, reply_markup=keyboard00)
        else:
            await bot.send_message(chat_id, 'У вас пока нет ни одного подключенного канала, пожалуйста, выберите команду "добавить канал"')
    except Exception as e:
        logging.error(f"Произошла ошибка: {str(e)}", exc_info=True)


def is_forwarded_message(message: types.Message):
    return message.forward_from_chat is not None


async def delete_old_message(chat_id, state, bot):
    try:
        user_data = await state.get_data()
        old_message_id = user_data.get('old_message_id')
        if old_message_id:
            await bot.delete_message(chat_id, old_message_id)
    except Exception as e:
        logging.error('error on delete old message: '+str(e))


async def delete_another_old_message(chat_id, state, name_of_message: str, bot):
    try:
        user_data = await state.get_data()
        old_message_id = user_data.get(name_of_message)
        if old_message_id:
            await bot.delete_message(chat_id, old_message_id)
    except Exception as e:
        logging.error('error on delete old message: '+str(e))


def get_word_endings(number_winners, all_prizes):
    string_with_prizes = ''
    keys = list(all_prizes.keys())
    last_key = keys[-1]

    for item in all_prizes:
        string_with_prizes += all_prizes[item]
        if item != last_key:
            string_with_prizes += ', '

    ending = ''
    ending2 = 'я'
    if number_winners in [2, 3, 4]:
        ending = 'а'
        ending2 = 'ей'
    elif number_winners != 1:
        ending = 'ов'
        ending2 = 'ей'
    final_result = []
    final_result.append(ending)
    final_result.append(ending2)
    return final_result


def get_string_from_dict(all_prizes):
    string_with_prizes = ''
    try:
        keys = list(all_prizes.keys())
        last_key = keys[-1]

        for item in all_prizes:
            string_with_prizes += all_prizes[item]
            if item != last_key:
                string_with_prizes += ', '
    except Exception as e:
        logging.error(str(e), exc_info=True)
    finally:
        return string_with_prizes


def get_winners_with_prizes(winners, all_prizes):
    string_with_prizes = ''
    try:
        string_with_prizes = ''

        for index, winner in enumerate(winners):
            prize_index = index + 1
            prize = all_prizes.get(prize_index)

            if prize is not None:
                string_with_prizes += winner + ' — ' + prize + '\n'
    except Exception as e:
        logging.error(str(e), exc_info=True)
    finally:
        return string_with_prizes


def forming_standart_template(number_winners, all_prizes, date_time_finish, new_text: str):
    string_with_prizes = get_string_from_dict(all_prizes)

    ending = ''
    ending2 = 'я'
    if number_winners in [2, 3, 4]:
        ending = 'а'
        ending2 = 'ей'
    elif number_winners != 1:
        ending = 'ов'
        ending2 = 'ей'

    if not new_text:
        TEXT = f'''Как насчет призов за подписку?

Мы решили разыграть {number_winners} приз{ending}:
{string_with_prizes}!

Чтобы выиграть, нужно:
1. Отправить этот пост 3 своим друзьям;
2. Нажать кнопку УЧАСТВУЮ.

{number_winners} победител{ending2} выберем {date_time_finish}
случайным образом. Всем удачи!'''
    else:
        TEXT = new_text.format(ending=ending, ending2=ending2)
    return TEXT


def extract_channel_id(s: str):
    # Разделение строки по символу '_'
    parts = s.split('_')
    # Проверка, достаточно ли частей в строке для извлечения значения
    if len(parts) >= 3:
        return parts[1]  # Возвращаем значение между первой и второй '_'
    else:
        return False


def extract_date(s: str):
    # Разделение строки по символу '_'
    parts = s.split('_')

    # Проверка, достаточно ли частей в строке для извлечения значения
    if len(parts) > 2:
        # Соединяем части обратно с подчеркиванием, за исключением первых двух и последней
        target_value = '_'.join(parts[2:-1])

        # Дополнительно разделяем это значение по символу '-'
        string_parts = target_value.split('-')
        if len(string_parts) == 2:
            # Возвращаем string1 и string2
            return string_parts[0], string_parts[1]
    return False, False  # Возвращаем False, если невозможно извлечь значение


async def get_invite_link(bot, channel_id):
    try:
        invite_link = await bot.export_chat_invite_link(chat_id=channel_id)
        return invite_link
    except Exception as e:
        return None


def replace_symbols_for_datetime(input_str):
    # Замены, которые нужно сделать
    replacements = {1: ".", 2: ".", 3: " в ", 4: ":"}
    count = 0
    # Функция для замены

    def replace(match):
        nonlocal count
        count += 1
        return replacements.get(count, match.group())
    try:
        # Проверяем, достаточно ли символов '_' в строке
        if input_str.count('_') < len(replacements):
            raise ValueError("Недостаточно символов '_' для замены")
        # Производим замену
        return re.sub("_", replace, input_str)
    except Exception as e:
        logging.error(str(e))
        return None


async def create_new_invite_link(bot: Bot, channel_id):
    try:
        new_invite_link = await bot.create_chat_invite_link(chat_id=channel_id)
        return new_invite_link.invite_link
    except Exception as e:
        print("Ошибка при создании инвайт-ссылки:", e)
        return None


async def form_string_with_started_competitions(chat_id: str, another_string_for_search, state, bot):
    try:
        date_start = date_finish = None
        if another_string_for_search:
            selected_jobs = [job for job in scheduler.get_jobs(
            ) if chat_id in job.id and another_string_for_search in job.id]
        else:
            selected_jobs = [job for job in scheduler.get_jobs(
            ) if chat_id in job.id and '_repeat' not in job.id]
            #  and sequence_to_exclude not in job.id]
        new_string = ''
        # Выводим найденные задачи
        for job in selected_jobs:
            if '_repeat' in job.id:
                await state.update_data(repeat_job_id=job.id)
                # new_string += (f"Found job with ID: {job.id}\n")
            channel_id = extract_channel_id(str(job.id))
            if not channel_id:
                continue
            if channel_id:
                chat = await bot.get_chat(channel_id)
                new_string += (f'Название канала: {chat.title}\n')
                date_start, date_finish = extract_date(str(job.id))
                link = await create_new_invite_link(bot, channel_id)
                if link:
                    new_string += (f'Ссылка на канал: {link}\n')
            if date_start and date_finish and not another_string_for_search:
                date_start = replace_symbols_for_datetime(date_start)
                date_finish = replace_symbols_for_datetime(date_finish)
                new_string += f'Время начала: {date_start}\nВремя итогов: {date_finish}\n\n'
        return (new_string, selected_jobs, date_start, date_finish) if date_start and date_finish else (new_string, selected_jobs, None, None)
    except Exception as e:
        logging.error(str(e), exc_info=True)
        return '', None, None, None


async def show_all_jobs(chat_id, bot: Bot, state):
    try:
        string_for_search = str(chat_id)
        # sequence_to_exclude = '_start'
        # Фильтрация задач
        new_string, selected_jobs, date_start, date_finish = await form_string_with_started_competitions(string_for_search, None, state, bot)
        # selected_jobs = [job for job in scheduler.get_jobs(
        # ) if string_for_search in job.id]
        # #  and sequence_to_exclude not in job.id]
        # new_string = ''
        # # Выводим найденные задачи
        # for job in selected_jobs:
        #     if '_repeat' in job.id:
        #         await state.update_data(repeat_job_id=job.id)
        #     # new_string += (f"Found job with ID: {job.id}\n")
        #     channel_id = extract_channel_id(str(job.id))
        #     if channel_id:
        #         chat = await bot.get_chat(channel_id)
        #         new_string += (f'Название канала: {chat.title}\n')
        #         date_start, date_finish = extract_date(str(job.id))
        #         link = await get_invite_link(bot, channel_id)
        #         if link:
        #             new_string += (f'Ссылка на канал: {link}\n')
        result_of_function = await form_string_with_started_competitions(str(chat_id), '_repeat', state, bot)
        repeated_jobs = result_of_function[0]
        if not selected_jobs or not new_string:
            old_message = await bot.send_message(chat_id, 'У вас нет запущенных конкурсов', reply_markup=keyboard13)
        if repeated_jobs:
            old_message = await bot.send_message(chat_id, new_string, reply_markup=keyboard16, disable_web_page_preview=True)
        else:
            old_message = await bot.send_message(chat_id, new_string, reply_markup=keyboard13, disable_web_page_preview=True)
        await state.update_data(old_message_id=old_message.message_id)
    except Exception as e:
        print(str(e))
