from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import Message, CallbackQuery, ChatJoinRequest
from aiogram.types.bot_command import BotCommand
from aiogram.types.bot_command_scope_default import BotCommandScopeDefault
from aiogram.filters.command import Command
from buttons import *
import databases.databases as databases
import logging
from datetime import datetime, time, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from typing import Any
import random
from string import Formatter
from databases.databases import scheduler
from dotenv import load_dotenv
import pytz
from constants_and_helpers import *
from dateutil.relativedelta import relativedelta
from typing import Union
from functions_helpers import *


load_dotenv()
moscow_tz = pytz.timezone('Europe/Moscow')
bot = Bot(token=BOT_TOKEN)
router = Router()
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(router)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - Line %(lineno)d',
                    filename='bot.log',  # Указываем имя файла для логгирования
                    filemode='a')


async def approve_request(chat_join: ChatJoinRequest, bot: Bot):
    try:
        message = 'Рад тебя приветствовать у нас!'
        await bot.send_message(chat_join.from_user.id, message)
        await chat_join.approve()
    except Exception as e:
        logging.error(f"Произошла ошибка: {str(e)}", exc_info=True)


@dp.message(is_forwarded_message)
async def handle_forwarded_message(message: types.Message, state: FSMContext):
    if message.forward_from_chat:
        channel_id = message.forward_from_chat.id
        try:
            await adding_new_channel(channel_id, message, state, bot)
        except Exception as e:
            logging.error(f"Произошла ошибка: {str(e)}", exc_info=True)


@dp.message(Command('prepare_new_post'))
@dp.message(F.text == "Запустить конкурс")
@dp.callback_query(lambda c: c.data == 'prepare_new_post')
async def start_competition(event: Union[types.Message, types.CallbackQuery], state: FSMContext):
    if isinstance(event, types.Message):
        chat_id = event.chat.id
        message = event
    elif isinstance(event, types.CallbackQuery):
        chat_id = event.from_user.id
        message = event.message
        await event.answer()
    if message:
        await state.update_data(old_message_id=message.message_id)
    await choosing_channels(chat_id, message, bot)
    await state.set_state(Channel.channel_chosed)


@dp.message(Command('main_menu'))
async def show_main_menu(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await delete_old_message(chat_id, state, bot)
    await show_main_menu_function(chat_id, state, bot)


@dp.callback_query(Channel.channel_chosed)
async def process(callback_query: CallbackQuery, state: FSMContext):
    # получили id канала
    chat_id = callback_query.from_user.id
    try:
        await delete_old_message(chat_id, state, bot)
    except:
        pass
    if callback_query.data:
        await state.update_data(channel_id=int(callback_query.data))
    old_message = await bot.send_message(callback_query.from_user.id, 'Пожалуйста, пришлите количество победителей.', reply_markup=keyboard13)
    await state.set_state(Competition.waiting_for_participant_count)
    await state.update_data(old_message_id=old_message.message_id)
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == 'back0')
@dp.callback_query(lambda c: c.data == 'back0', Channel.adding_channel)
@dp.callback_query(lambda c: c.data == 'back0', Competition.waiting_for_participant_count)
@dp.callback_query(lambda c: c.data == 'back0', CompetitionPost.prizes)
@dp.callback_query(lambda c: c.data == 'back0', CompetitionPost.date_time_start)
@dp.callback_query(lambda c: c.data == 'back0', CompetitionPost.date_time_finish)
@dp.callback_query(lambda c: c.data == 'back0', CompetitionPost.pin_or_not)
@dp.callback_query(lambda c: c.data == 'back0', CompetitionPost.repeat_or_not)
@dp.callback_query(lambda c: c.data == 'back0', CompetitionPost.content)
async def callback_process(callback_query: CallbackQuery, state: FSMContext):
    chat_id = callback_query.from_user.id
    message_id = 0
    if callback_query.message:
        message_id = callback_query.message.message_id
    current_state = await state.get_state()
    if current_state == None:
        await delete_old_message(chat_id, state, bot)
        await show_main_menu_function(chat_id, state, bot)
    elif current_state == Channel.adding_channel.state:
        await delete_old_message(chat_id, state, bot)
        await show_main_menu_function(chat_id, state, bot)
    elif current_state == Competition.waiting_for_participant_count.state:
        await choosing_channels(chat_id, callback_query.message, bot)
        await state.set_state(Channel.channel_chosed)
    elif current_state == CompetitionPost.prizes.state:
        await bot.edit_message_text('Пожалуйста, пришлите количество победителей.', chat_id=chat_id, message_id=message_id, reply_markup=keyboard13)
        await state.set_state(Competition.waiting_for_participant_count)
        await state.update_data(winners_data=None)
        await state.update_data(text=None)
    elif current_state == CompetitionPost.date_time_start.state:
        await bot.edit_message_text('Пожалуйста, введите приз для первого победителя!', chat_id=chat_id, message_id=message_id, reply_markup=keyboard13)
        await state.set_state(CompetitionPost.prizes)
        await state.update_data(prizes_list=None)
        await state.update_data(text=None)
    elif current_state == CompetitionPost.date_time_finish.state:
        await bot.edit_message_text('Теперь укажите дату начала конкурса в формате XX.XX.XXXX, либо выберите "опубликовать сейчас"', chat_id=chat_id, message_id=message_id, reply_markup=keyboard7)
        await state.set_state(CompetitionPost.date_time_start)
    elif current_state == CompetitionPost.pin_or_not.state:
        await bot.edit_message_text('Теперь укажите дату окончания конкурса в формате XX.XX.XXXX, либо выберите дату завершения из предложенных кнопок', chat_id=chat_id, message_id=message_id, reply_markup=keyboard9)
        await state.set_state(CompetitionPost.date_time_finish)
    elif current_state == CompetitionPost.repeat_or_not.state:
        await bot.edit_message_text('Закреплять конкурс?', chat_id=chat_id, message_id=message_id, reply_markup=keyboard6)
        await state.set_state(CompetitionPost.pin_or_not)
    elif current_state == CompetitionPost.content.state:
        await delete_another_old_message(chat_id, state, 'old_message_id1', bot)
        await delete_another_old_message(chat_id, state, 'old_message_id2', bot)
        await bot.edit_message_text('Повторять конкурс?', chat_id=chat_id, message_id=message_id, reply_markup=keyboard2)
        await state.set_state(CompetitionPost.repeat_or_not)
    await callback_query.answer()


@router.message(Competition.get_winners)
async def get_winners_state_handler(message: Message, state: FSMContext):
    # Пытаемся преобразовать текст в число
    try:
        user_id = message.chat.id
        channel_id = databases.get_channel_id_by_chat_id(user_id)
        participants = databases.get_all_participants(channel_id)
        available_participants = await participants_with_username(participants, bot)
        members_count = len(available_participants)
        if message.text:
            number_of_winners = int(message.text)
            if number_of_winners <= members_count and number_of_winners:
                winners = random.sample(
                    available_participants, number_of_winners)
                await message.answer('Победители:')
                for item in winners:
                    chat = await bot.get_chat(chat_id=item)
                    await message.answer('@'+str(chat.username))
                await state.update_data(winners_data=number_of_winners)
                await state.clear()
            else:
                await message.answer(f'Пожалуйста, введите число меньшее или равное {members_count} и чтобы оно было больше 0')
    except Exception as e:
        await message.answer('Пожалуйста, введите число')
        logging.error(f"Произошла ошибка: {str(e)}", exc_info=True)


@router.message(Competition.waiting_for_participant_count)
async def competition_count(message: Message, state: FSMContext):
    # Пытаемся преобразовать текст в число
    user_id = message.chat.id
    try:
        await delete_old_message(user_id, state, bot)
    except:
        pass
    try:
        if message.text:
            number_of_winners = int(message.text)
            await state.update_data(winners_data=number_of_winners)
            old_message = await message.answer('Пожалуйста, введите приз для первого победителя!', reply_markup=keyboard13)
            await state.set_state(CompetitionPost.prizes)
            await state.update_data(old_message_id=old_message.message_id)
    except Exception as e:
        old_message = await message.answer('Пожалуйста, введите число')
        await state.update_data(old_message_id=old_message.message_id)
        logging.error(f"Произошла ошибка: {str(e)}", exc_info=True)


@router.message(CompetitionPost.prizes)
async def prizes(message: Message, state: FSMContext):
    try:
        await delete_old_message(message.chat.id, state, bot)
    except:
        pass
    try:
        user_data = await state.get_data()
        winners_number = user_data.get('winners_data')
        prizes_list = user_data.get('prizes_list')
        if message.text:
            prizes_list = user_data.get('prizes_list')
            if prizes_list:
                for key in prizes_list:
                    if prizes_list[key] is not None:
                        continue
                    if prizes_list[len(prizes_list)] is None:
                        prizes_list[key] = message.text
                        if prizes_list[len(prizes_list)] is not None:
                            old_message = await message.answer('Теперь укажите дату начала конкурса в формате XX.XX.XXXX, либо выберите "опубликовать сейчас"', reply_markup=keyboard7)
                            await state.set_state(CompetitionPost.date_time_start)
                            await state.update_data(old_message_id=old_message.message_id)
                        else:
                            old_message = await message.answer(f'Пожалуйста, укажите приз для победителя {key+1}')
                            await state.update_data(old_message_id=old_message.message_id)
                            break
        if type(winners_number) is int:
            if winners_number == 1:
                list_with_numbers: dict[int, Any] = {
                    key: None for key in range(1, winners_number + 1)}
                list_with_numbers[1] = message.text
                await state.update_data(prizes_list=list_with_numbers)
                old_message = await message.answer('Теперь укажите дату начала конкурса в формате XX.XX.XXXX, либо выберите "опубликовать сейчас"', reply_markup=keyboard7)
                await state.set_state(CompetitionPost.date_time_start)
                await state.update_data(old_message_id=old_message.message_id)
            elif not prizes_list:
                list_with_numbers: dict[int, Any] = {
                    key: None for key in range(1, winners_number + 1)}
                list_with_numbers[1] = message.text
                await state.update_data(prizes_list=list_with_numbers)
                old_message = await message.answer(f'Пожалуйста, укажите приз для второго победителя')
                await state.update_data(old_message_id=old_message.message_id)
        else:
            await message.answer(f'Пожалуйста, введите точное количество победителей в числовом формате, проверьте правильность вводимых данных')
            await state.clear()
            await state.set_state(Competition.waiting_for_participant_count)
    except Exception as e:
        logging.error(f"Произошла ошибка: {str(e)}", exc_info=True)


@dp.callback_query(lambda c: c.data == 'date_start_now', CompetitionPost.date_time_start)
async def set_date_start_now(callback_query: CallbackQuery, state: FSMContext):
    time_now = time(datetime.now(moscow_tz).hour,
                    datetime.now(moscow_tz).minute)
    date_now = datetime.now(moscow_tz).date()
    await state.update_data(time_start=time_now)
    await state.update_data(date_start=date_now)
    await state.update_data(publish_now=True)
    chat_id = callback_query.from_user.id
    try:
        await delete_old_message(chat_id, state, bot)
    except:
        pass
    old_message = await bot.send_message(callback_query.from_user.id, 'Теперь укажите дату окончания конкурса в формате XX.XX.XXXX', reply_markup=keyboard9)
    await state.set_state(CompetitionPost.date_time_finish)
    await state.update_data(old_message_id=old_message.message_id)
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == 'tomorrow_finish_competition', CompetitionPost.date_time_finish)
@dp.callback_query(lambda c: c.data == 'week_finish_competition', CompetitionPost.date_time_finish)
@dp.callback_query(lambda c: c.data == 'month_finish_competition', CompetitionPost.date_time_finish)
async def set_date_finish_week(callback_query: CallbackQuery, state: FSMContext):
    time_finish = time(datetime.now(moscow_tz).hour,
                       datetime.now(moscow_tz).minute)
    date_finish = datetime.now(moscow_tz).date() + timedelta(weeks=1)
    await state.update_data(time=time_finish)
    await state.update_data(date=date_finish)
    if callback_query.data == 'tomorrow_finish_competition':
        await state.update_data(repeat_every='day')
    if callback_query.data == 'week_finish_competition':
        await state.update_data(repeat_every='week')
    if callback_query.data == 'month_finish_competition':
        await state.update_data(repeat_every='month')
    try:
        chat_id = callback_query.from_user.id
        await delete_old_message(chat_id, state, bot)
        if callback_query.message:
            await state.update_data(old_message_id=callback_query.message.message_id)
    except:
        pass
    old_message = await bot.send_message(callback_query.from_user.id, 'Закреплять конкурс?', reply_markup=keyboard6)
    await state.update_data(old_message_id=old_message.message_id)
    await state.set_state(CompetitionPost.pin_or_not)
    await callback_query.answer()


@router.message(CompetitionPost.date_time_start)
async def date_time_start(message: Message, state: FSMContext):
    try:
        chat_id = message.chat.id
        await delete_old_message(chat_id, state, bot)
    except:
        pass
    for i in range(1):
        if ':' in str(message.text):
            try:
                time_object = datetime.strptime(str(message.text), '%H:%M')
                time_only = time_object.time()
                if time_only > datetime.now(moscow_tz).time():
                    await state.update_data(time_start=time_only)
                    await state.update_data(publish_now=False)
                    # if time_only:
                    #     await bot.send_message(message.chat.id, 'hours: '+str(time_only.hour)+' minutes: '+str(time_only.minute))
                    old_message = await bot.send_message(message.chat.id, 'Теперь укажите дату окончания конкурса в формате XX.XX.XXXX, либо выберите дату завершения из предложенных кнопок', reply_markup=keyboard9)
                    await state.set_state(CompetitionPost.date_time_finish)
                    await state.update_data(old_message_id=old_message.message_id)
                    break
                else:
                    old_message = await bot.send_message(message.chat.id, 'Время публикации уже прошло\n\nВведите еще раз время в верном формате XX:XX')
                    await state.update_data(old_message_id=old_message.message_id)  
                    break
            except Exception as e:
                old_message = await bot.send_message(message.chat.id, 'Ошибка: Введите время еще раз в верном формате XX:XX')
                await state.update_data(old_message_id=old_message.message_id)
                break
        try:
            date_object = datetime.strptime(str(message.text), '%d.%m.%Y')
            date_only = date_object.date()
            if date_only and date_only >= datetime.now(moscow_tz).date():
                await state.update_data(date_start=date_only)
                old_message = await bot.send_message(message.chat.id, 'Теперь введите время старта конкурса по МСК в формате XX:XX')
            else:
                old_message = await bot.send_message(message.chat.id, 'Ошибка: Введите дату больше либо равную сегодняшнему дню в формате XX.XX.XXXX')
            await state.update_data(old_message_id=old_message.message_id)
        except Exception as e:
            old_message = await bot.send_message(message.chat.id, 'Ошибка: Введите дату еще раз в верном формате')
            await state.update_data(old_message_id=old_message.message_id)
            break


@router.message(CompetitionPost.date_time_finish)
async def date_time(message: Message, state: FSMContext):
    try:
        chat_id = message.chat.id
        await delete_old_message(chat_id, state, bot)
    except:
        pass
    for i in range(1):
        if ':' in str(message.text):
            try:
                time_object = datetime.strptime(str(message.text), '%H:%M')
                time_object = time_object.time()
                data = await state.get_data()
                date = data.get('date')
                date_start = data.get('date_start')
                time_start = data.get('time_start')
                if date and date_start and time_start:
                    date_and_time = datetime.combine(date, time_object)
                    start_date_and_time = datetime.combine(
                        date_start, time_start)
                    date_and_time = moscow_tz.localize(date_and_time)
                    start_date_and_time = moscow_tz.localize(
                        start_date_and_time)
                    if date_and_time > datetime.now(moscow_tz) and date_and_time > start_date_and_time:
                        await state.update_data(time=time_object)
                        old_message = await bot.send_message(message.chat.id, 'Закреплять конкурс?', reply_markup=keyboard6)
                        await state.set_state(CompetitionPost.pin_or_not)
                        await state.update_data(old_message_id=old_message.message_id)
                        break
                    else:
                        old_message = await bot.send_message(message.chat.id, 'Ошибка: Время и дата подведения итогов конкурса уже прошла либо вы ее назначили на более раннее время чем старт конкурса\n\nВведите еще раз дату окончания конкурса в формате XX.XX.XXXX')
                        await state.update_data(old_message_id=old_message.message_id)
                        break
            except Exception as e:
                old_message = await bot.send_message(message.chat.id, 'Ошибка: Введите время еще раз в верном формате XX:XX')
                await state.update_data(old_message_id=old_message.message_id)
                break
        try:
            date_object = datetime.strptime(str(message.text), '%d.%m.%Y')
            date_object = date_object.date()
            data = await state.get_data()
            date_start = data.get('date_start')
            if date_object and date_start and date_object >= datetime.now(moscow_tz).date() and date_object >= date_start:
                await state.update_data(date=date_object)
                old_message = await bot.send_message(message.chat.id, 'Теперь введите время окончания конкурса по МСК в формате XX:XX')
            else:
                old_message = await bot.send_message(message.chat.id, 'Ошибка: Введите дату больше либо равную стартовой дате конкурса в формате XX.XX.XXXX')
            await state.update_data(old_message_id=old_message.message_id)
        except Exception as e:
            old_message = await bot.send_message(message.chat.id, 'Введите дату еще раз в верном формате')
            await state.update_data(old_message_id=old_message.message_id)
            break


@dp.callback_query(lambda c: c.data == 'button_pressed')
async def process_callback_button1(callback_query: CallbackQuery):
    if callback_query.message:
        channel_id = callback_query.message.chat.id
        member = await bot.get_chat_member(channel_id, callback_query.from_user.id)
        if member.status in ['member', 'administrator', 'creator']:
            if databases.check_member_exists(callback_query.from_user.id, channel_id):
                await callback_query.answer('Вы уже участвуете в конкурсе', show_alert=True)
            else:
                await callback_query.answer('Спасибо за участие в конкурсе!', show_alert=True)
                try:
                    # databases.add_member(callback_query.from_user.id)
                    databases.add_participant_user_channel(
                        callback_query.from_user.id, channel_id)
                except Exception as e:
                    print('error with database')
                    logging.error(f"Произошла ошибка: {str(e)}", exc_info=True)
        else:
            await callback_query.answer("Вам необходимо быть подписанным на канал для участия в конкурсе!")
    else:
        logging.info(
            f'Cant get data from button on the compertition post for {callback_query.from_user.id}')
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == 'pin_yes', CompetitionPost.pin_or_not)
@dp.callback_query(lambda c: c.data == 'pin_no', CompetitionPost.pin_or_not)
async def callback_yes(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == 'pin_yes':
        await state.update_data(pin=True)
    elif callback_query.data == 'pin_no':
        await state.update_data(pin=False)
    try:
        chat_id = callback_query.from_user.id
        await delete_old_message(chat_id, state, bot)
        if callback_query.message:
            await state.update_data(old_message_id=callback_query.message.message_id)
    except:
        pass
    old_message = await bot.send_message(callback_query.from_user.id, 'Повторять конкурс?', reply_markup=keyboard2)
    await state.update_data(old_message_id=old_message.message_id)
    await state.set_state(CompetitionPost.repeat_or_not)
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == 'repeat_yes', CompetitionPost.repeat_or_not)
@dp.callback_query(lambda c: c.data == 'repeat_no', CompetitionPost.repeat_or_not)
async def process_callback_yes(callback_query: CallbackQuery, state: FSMContext):
    try:
        chat_id = callback_query.from_user.id
        await delete_old_message(chat_id, state, bot)
        if callback_query.message:
            await state.update_data(old_message_id=callback_query.message.message_id)
    except:
        pass
    has_task = databases.check_user_has_cron_task(callback_query.from_user.id)
    if has_task:
        chat_id = has_task
        try:
            for job in scheduler.get_jobs():
                if str(chat_id) in job.id and '_repeat' in job.id:
                    scheduler.remove_job(job.id)
        except Exception as e:
            logging.error(
                'Scheduler remove and add job error in Every day/month/week Callback' + str(e), exc_info=True)
    # await bot.send_message(callback_query.from_user.id, 'Повторять:', reply_markup=keyboard4)
    if callback_query.data == 'repeat_yes':
        user_data = await state.get_data()
        time_for_repeat = user_data.get('repeat_every')
        if time_for_repeat:
            if time_for_repeat == 'day':
                databases.add_task_info(callback_query.from_user.id, 1)
            elif time_for_repeat == 'week':
                databases.add_task_info(callback_query.from_user.id, 2)
            elif time_for_repeat == 'month':
                databases.add_task_info(callback_query.from_user.id, 3)
    elif callback_query.data == 'repeat_no':
        databases.add_task_info(callback_query.from_user.id, 0)
    old_message = await bot.send_message(callback_query.from_user.id, 'Пришлите фото или видео, или нажмите кнопку "без медиа"', reply_markup=keyboard3)
    await state.update_data(old_message_id=old_message.message_id)
    await state.set_state(CompetitionPost.content)
    await callback_query.answer()


async def final_forming_post_for_job(state, callback_query, message):
    try:
        user_data = await state.get_data()
        winners_number = user_data.get('winners_data')
        channel_id = user_data.get('channel_id')
        date = user_data.get('date')
        time = user_data.get('time')
        prizes_list = user_data.get('prizes_list')
        text = user_data.get('text')
        changed_template = user_data.get('template_changed')
        old_message = None
        old_message1 = None
        old_message2 = None
        if date:
            date = date.strftime("%d.%m.%Y")
        if time:
            time = time.strftime("%H:%M")
        if not text:
            text = forming_standart_template(
                winners_number, prizes_list, date_time_finish=f'{date} г. в {time} по МСК', new_text='')
            await state.update_data(text=text)
        if callback_query:
            await state.update_data(photo=None)
            databases.add_prepared_text_for_post(
                callback_query.from_user.id, str(text), winners_number)
            old_message1 = await bot.send_message(callback_query.from_user.id, 'Вот готовящийся к публикации шаблон:')
            old_message2 = await bot.send_message(callback_query.from_user.id, TEXT_STANDARD_TEMPLATE)
            old_message = await bot.send_message(callback_query.from_user.id, f'Значения переменных:\n{{number_winners}}: {winners_number}\n{{string_with_prizes}}: {get_string_from_dict(prizes_list)}\n{{date_time_finish}}: {date} г. в {time} по МСК', reply_markup=keyboard5)
            # chat = await bot.get_chat(channel_id)
            # await bot.send_message(chat_id=callback_query.from_user.id, text=f'Канал: {chat.title}\nВремя начала: {date_time_starting}\nВремя итогов: {date_time_finishing}')
            # await bot.send_message(callback_query.from_user.id, "Отправьте '/post' когда полностью готовы опубликовать пост в канал. Либо можете прислать фото для поста или изменить шаблон", reply_markup=keyboard5)
        elif message and not changed_template:
            if message.animation:
                await state.update_data(animation=message.animation.file_id)
                databases.add_prepared_animation_for_post(
                    message.chat.id, str(message.animation.file_id))
                databases.add_prepared_text_for_post(
                    message.chat.id, str(text), winners_number)
                old_message1 = await bot.send_message(chat_id=message.chat.id, text='Вот готовящийся к публикации шаблон:')
                old_message2 = await bot.send_animation(chat_id=message.chat.id, animation=message.animation.file_id, caption=TEXT_STANDARD_TEMPLATE)
                old_message = await bot.send_message(message.chat.id, f'Значения переменных:\n{{number_winners}}: {winners_number}\n{{string_with_prizes}}: {get_string_from_dict(prizes_list)}\n{{date_time_finish}}: {date} г. в {time} по МСК', reply_markup=keyboard5)
                # chat = await bot.get_chat(channel_id)
                # await bot.send_message(chat_id=message.chat.id, text=f'Канал: {chat.title}\nВремя начала: {date_time_starting}\nВремя итогов: {date_time_finishing}')
            elif message.document:
                await state.update_data(document=message.document.file_id)
                databases.add_prepared_document_for_post(
                    message.chat.id, str(message.document.file_id))
                databases.add_prepared_text_for_post(
                    message.chat.id, str(text), winners_number)
                old_message1 = await bot.send_message(chat_id=message.chat.id, text='Вот готовящийся к публикации шаблон:')
                old_message2 = await bot.send_document(chat_id=message.chat.id, document=message.document.file_id, caption=TEXT_STANDARD_TEMPLATE)
                old_message = await bot.send_message(message.chat.id, f'Значения переменных:\n{{number_winners}}: {winners_number}\n{{string_with_prizes}}: {get_string_from_dict(prizes_list)}\n{{date_time_finish}}: {date} г. в {time} по МСК', reply_markup=keyboard5)
                # chat = await bot.get_chat(channel_id)
                # await bot.send_message(chat_id=message.chat.id, text=f'Канал: {chat.title}\nВремя начала: {date_time_starting}\nВремя итогов: {date_time_finishing}')
            elif message.video:
                await state.update_data(video=message.video.file_id)
                databases.add_prepared_video_for_post(
                    message.chat.id, str(message.video.file_id))
                databases.add_prepared_text_for_post(
                    message.chat.id, str(text), winners_number)
                old_message1 = await bot.send_message(chat_id=message.chat.id, text='Вот готовящийся к публикации шаблон:')
                old_message2 = await bot.send_video(chat_id=message.chat.id, video=message.video.file_id, caption=TEXT_STANDARD_TEMPLATE)
                old_message = await bot.send_message(message.chat.id, f'Значения переменных:\n{{number_winners}}: {winners_number}\n{{string_with_prizes}}: {get_string_from_dict(prizes_list)}\n{{date_time_finish}}: {date} г. в {time} по МСК', reply_markup=keyboard5)
                # chat = await bot.get_chat(channel_id)
                # await bot.send_message(chat_id=message.chat.id, text=f'Канал: {chat.title}\nВремя начала: {date_time_starting}\nВремя итогов: {date_time_finishing}')
            elif message.photo:
                # Сохраняем фото в контексте состояния
                await state.update_data(photo=message.photo[-1].file_id)
                databases.add_prepared_photo_for_post(
                    message.chat.id, str(message.photo[-1].file_id))
                databases.add_prepared_text_for_post(
                    message.chat.id, str(text), winners_number)
                old_message1 = await bot.send_message(chat_id=message.chat.id, text='Вот готовящийся к публикации шаблон:')
                old_message2 = await bot.send_photo(chat_id=message.chat.id, photo=message.photo[-1].file_id, caption=TEXT_STANDARD_TEMPLATE)
                old_message = await bot.send_message(message.chat.id, f'Значения переменных:\n{{number_winners}}: {winners_number}\n{{string_with_prizes}}: {get_string_from_dict(prizes_list)}\n{{date_time_finish}}: {date} г. в {time} по МСК', reply_markup=keyboard5)
                # chat = await bot.get_chat(channel_id)
                # await bot.send_message(chat_id=message.chat.id, text=f'Канал: {chat.title}\nВремя начала: {date_time_starting}\nВремя итогов: {date_time_finishing}')
            # await message.answer("Отправьте '/post' когда полностью готовы опубликовать пост в канал. Либо можете прислать другое фото или видео или изменить шаблон", reply_markup=keyboard5)
        elif message and changed_template:
            date = user_data.get('date')
            file_id, media_type = databases.get_first_media_id(message.chat.id)
            if file_id and media_type:
                old_message1 = await bot.send_message(chat_id=message.chat.id, text='Вот готовящийся к публикации шаблон:')
                if media_type == 'photo':
                    old_message2 = await bot.send_photo(chat_id=message.chat.id, photo=file_id, caption=message.text)
                if media_type == 'video':
                    old_message2 = await bot.send_video(chat_id=message.chat.id, video=file_id, caption=message.text)
                if media_type == 'animation':
                    old_message2 = await bot.send_animation(chat_id=message.chat.id, animation=file_id, caption=message.text)
                if media_type == 'document':
                    old_message2 = await bot.send_document(chat_id=message.chat.id, document=file_id, caption=message.text)
                old_message = await bot.send_message(message.chat.id, f'Значения переменных:\n{{number_winners}}: {winners_number}\n{{string_with_prizes}}: {get_string_from_dict(prizes_list)}\n{{date_time_finish}}: {date} г. в {time} по МСК', reply_markup=keyboard5)
            else:
                old_message1 = await bot.send_message(message.chat.id, 'Вот готовящийся к публикации шаблон:')
                old_message2 = await bot.send_message(message.chat.id, message.text)
                old_message = await bot.send_message(message.chat.id, f'Значения переменных:\n{{number_winners}}: {winners_number}\n{{string_with_prizes}}: {get_string_from_dict(prizes_list)}\n{{date_time_finish}}: {date} г. в {time} по МСК', reply_markup=keyboard5)
        if old_message:
            await state.update_data(old_message_id=old_message.message_id)
        if old_message1:
            await state.update_data(old_message_id1=old_message1.message_id)
        if old_message2:
            await state.update_data(old_message_id2=old_message2.message_id)
    except Exception as e:
        logging.error(f"Произошла ошибка: {str(e)}", exc_info=True)


@dp.callback_query(lambda c: c.data == 'no_photo', CompetitionPost.content)
async def process_competition_post(callback_query: CallbackQuery, state: FSMContext):
    try:
        chat_id = callback_query.from_user.id
        await delete_old_message(chat_id, state, bot)
        if callback_query.message:
            await state.update_data(old_message_id=callback_query.message.message_id)
    except:
        pass
    await final_forming_post_for_job(state, callback_query=callback_query, message=None)
    await callback_query.answer()


@router.message(CompetitionPost.content)
async def process_competition_post1(message: types.Message, state: FSMContext):
    try:
        chat_id = message.chat.id
        await delete_old_message(chat_id, state, bot)
    except:
        pass
    await final_forming_post_for_job(state, callback_query=None, message=message)


@dp.callback_query(lambda c: c.data == 'change_text', CompetitionPost.content)
async def process_competition_post2(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(text=None)
    try:
        if callback_query.message:
            chat_id = callback_query.from_user.id
            await delete_old_message(chat_id, state, bot)
    except Exception as e:
        print(str(e))
    old_message = await bot.send_message(callback_query.from_user.id, f'''Пришлите в ответ измененный шаблон, вы можете переставлять переменные вместе с фигурными скобками.\n\nВНИМАНИЕ! Переменная может быть окончанием слова, для корректной работы скрипта переносите переменную вместе со словом. Пример: победител{{ending2}}.\n\nПришлите в ответ измененный вариант:''')
    # await bot.send_message(callback_query.from_user.id, TEXT_STANDARD_TEMPLATE)
    await state.set_state(CompetitionPost.change_text)
    await state.update_data(old_message_id3=old_message.message_id)
    await callback_query.answer()


@router.message(CompetitionPost.change_text)
async def process_competition_post3(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    try:
        chat_id = message.chat.id
        await delete_another_old_message(chat_id, state, 'old_message_id1', bot)
        await delete_another_old_message(chat_id, state, 'old_message_id2', bot)
        old_message = user_data.get('old_message_id3')
        if old_message:
            await delete_another_old_message(chat_id, state, 'old_message_id3', bot)
    except Exception as e:
        print(str(e))
    formatted_string = ''
    winners_number = user_data.get('winners_data')
    date = user_data.get('date')
    time = user_data.get('time')
    if date:
        date = date.strftime("%d.%m.%Y")
    if time:
        time = time.strftime("%H:%M")
    prizes_list = user_data.get('prizes_list')
    ending = get_word_endings(winners_number, prizes_list)[0]
    ending2 = get_word_endings(winners_number, prizes_list)[1]
    string_with_prizes = get_string_from_dict(prizes_list)
    if message.text:
        final_text = insert_links_into_text(message)
        safe_substitute = SafeDict()
        safe_substitute.update(
            {"number_winners": winners_number, "ending": ending, "string_with_prizes": string_with_prizes, "ending2": ending2, "date_time_finish": f"{date} г. в {time} по МСК"})
        if final_text:
            formatted_string = Formatter().vformat(final_text, (), safe_substitute)
            await state.update_data(text=formatted_string)
    if formatted_string:
        await bot.send_message(message.chat.id, 'Шаблон успешно заменен!')
        await state.update_data(template_changed='yes')
        await state.set_state(CompetitionPost.content)
        await final_forming_post_for_job(state, callback_query=None, message=message)
    #     formatted_string = hide_links_into_words(formatted_string)
    #     await bot.send_message(message.chat.id, f'Финальный вариант публикующегося поста:\n{formatted_string}', parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id, 'Попробуйте еще раз заменить шаблон, что-то пошло не так')
    # old_message = await message.answer("Запустить конкурс?\nЛибо можете прислать другое фото или видео или изменить шаблон", reply_markup=keyboard5)
    # await state.update_data(old_message_id=old_message.message_id)


def remove_past_non_repeating_jobs():
    try:
        timezone = pytz.timezone("Europe/Moscow")
        now = datetime.now(timezone)
        for job in scheduler.get_jobs():
            if isinstance(job.trigger, databases.DateTrigger) and job.next_run_time < now:
                scheduler.remove_job(job.id)
    except Exception as e:
        logging.error(str(e), exc_info=True)


async def function_for_finish_post(chat_id, state):
    try:
        await delete_old_message(chat_id, state, bot)
    except:
        pass
    try:
        data = await state.get_data()
        CHANNEL_ID = data.get('channel_id')
        photo = data.get('photo')
        video = data.get('video')
        document = data.get('document')
        animation = data.get('animation')
        publish_now = data.get('publish_now')
        if publish_now:
            time_only = (datetime.now(moscow_tz) + timedelta(minutes=1)).time()
            date_only = datetime.now(moscow_tz).date()
        else:
            date_only = data.get('date_start')
            time_only = data.get('time_start')
        time_finish = data.get('time')
        date_finish = data.get('date')
        winners_number = data.get('winners_data')
        prizes_list = data.get('prizes_list')
        pin_or_not = data.get('pin')
        remove_past_non_repeating_jobs()
        year = month = day = hour = minute = start_datetime = finish_datetime = 0
        finish_datetime_str = ''

        if date_only and time_only:
            start_datetime = datetime.combine(date_only, time_only)
            start_datetime = moscow_tz.localize(start_datetime)
            start_datetime_str = start_datetime.strftime("%d_%m_%Y_%H_%M")

            if start_datetime < datetime.now(moscow_tz):
                await bot.send_message(chat_id, "Время публикации уже прошло, сформируйте пост заново командой /prepare_new_post")
                await state.clear()
            else:
                if time_finish and date_finish:
                    finish_datetime = datetime.combine(
                        date_finish, time_finish)
                    finish_datetime = moscow_tz.localize(finish_datetime)
                    finish_datetime_str = finish_datetime.strftime(
                        "%d_%m_%Y_%H_%M")
                    if publish_now and finish_datetime <= start_datetime:
                        finish_datetime = start_datetime + timedelta(minutes=1)
                if date_only:
                    year = int(date_only.year)
                    month = int(date_only.month)
                    day = int(date_only.day)
                if time_only:
                    hour = int(time_only.hour)
                    minute = int(time_only.minute)
                if ('photo' in data and photo and CHANNEL_ID) or ('video' in data and video and CHANNEL_ID) or ('document' in data and document and CHANNEL_ID) or ('animation' in data and animation and CHANNEL_ID):
                    # Отправляем фото с подписью
                    # await bot.send_photo(CHANNEL_ID, photo=data['photo'], caption=data['text'], reply_markup=keyboard)
                    databases.add_prepared_text_for_post(
                        chat_id, data['text'], winners_number)
                    if photo:
                        databases.add_prepared_photo_for_post(
                            chat_id, photo_id=photo)
                    elif video:
                        databases.add_prepared_video_for_post(
                            chat_id, video_id=video)
                    elif document:
                        databases.add_prepared_document_for_post(
                            chat_id, document_id=document)
                    elif animation:
                        databases.add_prepared_animation_for_post(
                            chat_id, animation_id=animation)
                    if year and month and day and hour and minute and start_datetime and finish_datetime:
                        try:
                            scheduler.add_job(send_post, 'date', args=[chat_id, CHANNEL_ID, start_datetime, finish_datetime, 0, prizes_list, pin_or_not], run_date=datetime(
                                year, month, day, hour, minute), id=str(chat_id)+'_'+str(CHANNEL_ID)+'_'+start_datetime_str+'-'+finish_datetime_str+'_start')
                        except Exception as e:
                            logging.error(str(e), exc_info=True)
                    else:
                        logging.info(
                            'Строка 727, job не добавлен потому что не получил времени', exc_info=True)
                elif 'text' in data and CHANNEL_ID:
                    databases.add_prepared_text_for_post(
                        chat_id, data['text'], winners_number)
                    databases.add_prepared_photo_for_post(
                        chat_id, photo_id='')
                    if year and month and day and hour and minute and start_datetime and finish_datetime:
                        try:
                            scheduler.add_job(send_post, 'date', args=[chat_id, CHANNEL_ID, start_datetime, finish_datetime, 0, prizes_list, pin_or_not], run_date=datetime(
                                year, month, day, hour, minute), id=str(chat_id)+'_'+str(CHANNEL_ID)+'_'+start_datetime_str+'-'+finish_datetime_str+'_start')
                        except Exception as e:
                            logging.error(str(e), exc_info=True)
                    else:
                        logging.info(
                            'Строка 742, job не добавлен потому что не получил времени', exc_info=True)
                else:
                    await bot.send_message(chat_id, 'You have not provided any content!')
                await state.clear()
                try:
                    chat_id = chat_id
                    await delete_old_message(chat_id, state, bot)
                except:
                    pass
                if start_datetime_str and finish_datetime_str:
                    chat = await bot.get_chat(CHANNEL_ID)
                    start_datetime_str = replace_symbols_for_datetime(start_datetime_str)
                    finish_datetime_str = replace_symbols_for_datetime(finish_datetime_str)
                    await bot.send_message(chat_id, text=f'Канал: {chat.title}\nВремя начала: {start_datetime_str}\nВремя итогов: {finish_datetime_str}')
                await bot.send_message(chat_id, "Пост успешно принят к публикации", reply_markup=keyboard10)
    except Exception as e:
        logging.error(f"Произошла ошибка: {str(e)}", exc_info=True)


@dp.message(Command('post'))
@dp.callback_query(lambda c: c.data == 'post')
async def finish_competition_post(event: Union[types.Message, types.CallbackQuery], state: FSMContext):
    if isinstance(event, types.Message):
        chat_id = event.chat.id
    elif isinstance(event, types.CallbackQuery):
        chat_id = event.from_user.id
        await event.answer()
    await function_for_finish_post(chat_id, state)


@dp.callback_query(lambda c: c.data == 'stop_repeated_job')
async def stop_repeated_jobs(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.from_user.id
    await delete_old_message(chat_id, state, bot)
    result_of_function = await form_string_with_started_competitions(str(chat_id), '_repeat', state, bot)
    new_string = result_of_function[0]
    if new_string:
        message = await bot.send_message(chat_id, f'Вы уверены, что хотите остановить повторяющийся конкурс?\n{new_string}', reply_markup=keyboard17, disable_web_page_preview=True)
    else:
        message = await bot.send_message(chat_id, 'Повторяющиеся конкурсы не обнаружены', reply_markup=keyboard13)
    await state.update_data(old_message_id=message.message_id)


@dp.callback_query(lambda c: c.data == 'yes_stop_repeated_job')
@dp.callback_query(lambda c: c.data == 'dont_stop_repeated_job')
async def yes_no_stop_repeated_jobs(callback_query: types.CallbackQuery, state: FSMContext):
    message = ''
    chat_id = callback_query.from_user.id
    await delete_old_message(chat_id, state, bot)
    if callback_query.data == 'yes_stop_repeated_job':
        user_data = await state.get_data()
        job_id = user_data.get('repeat_job_id')
        if job_id:
            try:
                scheduler.remove_job(job_id)
                message = await bot.send_message(chat_id, 'Удаление повторяющегося конкурса выполнено')
            except Exception as e:
                message = await bot.send_message(chat_id, 'Удаление не выполнилось, возможно у вас нет повторяющегося конкурса')
        else:
            message = await bot.send_message(chat_id, 'Удаление не выполнилось, возможно у вас нет повторяющегося конкурса')
    if callback_query.data == 'dont_stop_repeated_job':
        await show_main_menu_function(chat_id, state, bot)
    if message:
        await state.update_data(old_message_id=message.message_id)


@dp.callback_query(lambda c: c.data == 'add_channel')
@dp.message(Command('start'))
@dp.message(Command('add_channel'))
@dp.message(F.text == "Добавить канал")
@dp.callback_query(lambda c: c.data == 'add_channel')
async def add_new_channel(event: Union[types.Message, types.CallbackQuery], state: FSMContext):
    if isinstance(event, types.Message):
        chat_id = event.chat.id
        await delete_old_message(chat_id, state, bot)
        await state.update_data(old_message_id=event.message_id)
    elif isinstance(event, types.CallbackQuery):
        chat_id = event.from_user.id
        await delete_old_message(chat_id, state, bot)
        if event.message:
            await state.update_data(old_message_id=event.message.message_id)
        await event.answer()
    await delete_old_message(chat_id, state, bot)
    message = await bot.send_message(chat_id, '''Для корректной работы бота и запуска конкурсов необходимо добавить канал: \n1. Добавьте этого бота @Leadgramcontestsbot в администраторы канала с правом на публикацию сообщений и созданием ссылок-приглашений.
2. Перешлите любой пост из канала в бот.''', reply_markup=keyboard13)
    await state.set_state(Channel.adding_channel)
    await state.update_data(old_message_id=message.message_id)


@dp.message(Command('show_all_jobs'))
@dp.message(F.text == "Посмотреть запущенные")
@dp.callback_query(lambda c: c.data == 'show_all_jobs')
async def show_jobs(event: Union[types.Message, types.CallbackQuery], state: FSMContext):
    if isinstance(event, types.Message):
        chat_id = event.chat.id
        try:
            await delete_old_message(chat_id, state, bot)
            await state.update_data(old_message_id=event.message_id)
        except:
            pass
    elif isinstance(event, types.CallbackQuery):
        chat_id = event.from_user.id
        try:
            await delete_old_message(chat_id, state, bot)
            if event.message:
                await state.update_data(old_message_id=event.message.message_id)
        except:
            pass
        await event.answer()
    await show_all_jobs(chat_id, bot, state)


@dp.callback_query(lambda c: c.data == 'start_new_competition')
async def process_new_competition(callback_query: CallbackQuery, state: FSMContext):
    chat_id = callback_query.from_user.id
    message = callback_query.message
    try:
        if callback_query.message:
            await state.update_data(old_message_id=callback_query.message.message_id)
    except:
        pass
    await choosing_channels(chat_id, message, bot)
    await state.set_state(Channel.channel_chosed)
    await callback_query.answer()


@router.message(Channel.adding_channel)
async def adding_channel(message: types.Message, state: FSMContext):
    try:
        if message.text:
            channel_id = int(message.text)
            await adding_new_channel(channel_id, message, state, bot)
    except Exception as e:
        logging.error(f"Произошла ошибка: {str(e)}", exc_info=True)


async def edit_message(chat_id, channel_id, message_id, photo, prizes_list):
    winners_number = databases.get_winners_number_from_post(chat_id)
    winners_list = await get_just_winners(winners_number, channel_id, bot)
    if not winners_list:
        await bot.send_message(chat_id, "Количество победителей которых вы хотите набрать превышает количество зарегистрировавшихся участников, перезапустите конкурс")
    try:
        text = databases.get_message_text_from_publication(message_id)
        winners_with_prizes = get_winners_with_prizes(
            winners_list, prizes_list)
        if text:
            text = text + \
                f'''\n\nКонкурс завершен! Победители: \n{winners_with_prizes}'''
        # Редактирование сообщения в канале
            if photo:
                await bot.edit_message_caption(chat_id=channel_id, message_id=message_id, caption=text, reply_markup=None)
            else:
                await bot.edit_message_text(chat_id=channel_id, message_id=message_id, text=text, reply_markup=None)
            await bot.send_message(chat_id, "Сообщение успешно отредактировано.")
            if not databases.is_repeat_needed(message_id):
                databases.delete_post_from_post_table(message_id)
        if winners_list:
            databases.delete_all_participants(channel_id)
    except Exception as e:
        logging.error(str(e), exc_info=True)


async def send_post(chat_id: int, channel_id, date_start, date_finish, repeat_or_not: bool, prizes_list, pin_or_not):
    try:
        photo = databases.get_photo_id_from_post(chat_id)
        video = databases.get_video_id_from_post(chat_id)
        document = databases.get_document_id_from_post(chat_id)
        animation = databases.get_animation_id_from_post(chat_id)
        text = databases.get_text_from_post(chat_id)
        text = hide_links_into_words(text)
        date = date_finish.date()
        time = date_finish.time()
        day = date.day
        month = date.month
        year = date.year
        hour = time.hour
        minute = time.minute
        if date_finish < date_start:
            date_finish = date_start + timedelta(minutes=1)
            time = date_finish.time()
            minute = time.minute
        start_datetime_str = date_start.strftime("%d_%m_%Y_%H_%M")
        finish_datetime_str = date_finish.strftime("%d_%m_%Y_%H_%M")
        message = ''
        if photo and text:
            # Отправляем фото с подписью
            message = await bot.send_photo(channel_id, photo=photo, caption=text, reply_markup=keyboard, parse_mode='HTML')
        elif video and text:
            # Отправляем видео с подписью
            message = await bot.send_video(channel_id, video=video, caption=text, reply_markup=keyboard, parse_mode='HTML')
        elif animation and text:
            # Отправляем видео с подписью
            message = await bot.send_animation(channel_id, animation=animation, caption=text, reply_markup=keyboard, parse_mode='HTML')
        elif document and text:
            # Отправляем видео с подписью
            message = await bot.send_document(channel_id, document=document, caption=text, reply_markup=keyboard, parse_mode='HTML')
        if message and text:
            message_id = message.message_id
            if repeat_or_not and pin_or_not:
                await bot.unpin_chat_message(channel_id)
            if pin_or_not:
                await bot.pin_chat_message(channel_id, message_id)
            databases.add_post_to_publish(
                message_id, channel_id, date_start, date_finish, repeat_or_not, text)
            scheduler.add_job(edit_message, args=[chat_id, channel_id, message_id, 1, prizes_list], run_date=datetime(
                year, month, day, hour, minute), id=str(chat_id)+'_'+str(channel_id)+'_'+start_datetime_str+'-'+finish_datetime_str+'_finish')
        elif text:
            # Отправляем только текст
            message = await bot.send_message(channel_id, text, reply_markup=keyboard, parse_mode='HTML')
            message_id = message.message_id
            if repeat_or_not and pin_or_not:
                await bot.unpin_chat_message(channel_id)
            if pin_or_not:
                await bot.pin_chat_message(channel_id, message_id)
            databases.add_post_to_publish(
                message_id, channel_id, date_start, date_finish, repeat_or_not, text)
            scheduler.add_job(edit_message, args=[chat_id, channel_id, message_id, 0, prizes_list], run_date=datetime(
                year, month, day, hour, minute), id=str(chat_id)+'_'+str(channel_id)+'_'+start_datetime_str+'-'+finish_datetime_str+'_finish')
        else:
            await bot.send_message(chat_id, "Не получен текст для поста")
        if databases.check_user_has_cron_task(chat_id):
            day_week_month = databases.get_day_week_or_month(
                chat_id)
            try:
                date_start = date_finish + timedelta(minutes=5)
                date_finish = date_finish + timedelta(minutes=5)
                date = date_finish.date()
                time = date_finish.time()
                day = date.day
                month = date.month
                year = date.year
                hour = time.hour
                minute = time.minute
                if day_week_month == 1 and date_start and date_finish:
                    date_finish = date_finish + timedelta(days=1)
                    scheduler.add_job(send_post, 'date', args=[chat_id, channel_id, date_start, date_finish, 0, prizes_list, pin_or_not], run_date=datetime(
                        year, month, day, hour, minute), id=str(chat_id)+'_'+str(channel_id)+'_'+start_datetime_str+'-'+finish_datetime_str+'_repeat')
                elif day_week_month == 2 and date_start and date_finish:
                    date_finish = date_finish + timedelta(weeks=1)
                    scheduler.add_job(send_post, 'date', args=[chat_id, channel_id, date_start, date_finish, 0, prizes_list, pin_or_not], run_date=datetime(
                        year, month, day, hour, minute), id=str(chat_id)+'_'+str(channel_id)+'_'+start_datetime_str+'-'+finish_datetime_str+'_repeat')
                elif day_week_month == 3 and date_start and date_finish:
                    date_finish = date_finish + relativedelta(months=1)
                    scheduler.add_job(send_post, 'date', args=[chat_id, channel_id, date_start, date_finish, 0, prizes_list, pin_or_not], run_date=datetime(
                        year, month, day, hour, minute), id=str(chat_id)+'_'+str(channel_id)+'_'+start_datetime_str+'-'+finish_datetime_str+'_repeat')
            except Exception as e:
                logging.error(str(e), exc_info=True)
    except Exception as e:
        logging.error(f"Произошла ошибка: {str(e)}", exc_info=True)


async def main():
    # Запуск polling
    try:
        scheduler.start()
        jobs = scheduler.get_jobs()
        for job in jobs:
            print(f"Job ID: {job.id}, Next Run Time: {job.next_run_time}")
        dp.chat_join_request.register(approve_request)
        commands = [
            BotCommand(command="/main_menu",
                       description="Главное меню")
        ]
        await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logging.error(f"Произошла ошибка: {str(e)}", exc_info=True)

if __name__ == '__main__':
    asyncio.run(main())
