from aiogram import types

button20 = types.InlineKeyboardButton(
    text="<<Назад", callback_data="back0")
button = types.InlineKeyboardButton(
    text="Участвую", callback_data="button_pressed")
button2 = types.InlineKeyboardButton(text="Да", callback_data="repeat_yes")
button3 = types.InlineKeyboardButton(text="Нет", callback_data="repeat_no")
button4 = types.InlineKeyboardButton(
    text="Без медиа", callback_data="no_photo")
button5 = types.InlineKeyboardButton(
    text="Каждый день", callback_data="every_day")
button6 = types.InlineKeyboardButton(
    text="Каждую неделю", callback_data="every_week")
button7 = types.InlineKeyboardButton(
    text="Каждый месяц", callback_data="every_month")
button8 = types.InlineKeyboardButton(
    text="Изменить шаблон текста", callback_data="change_text")
keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button]])
keyboard2 = types.InlineKeyboardMarkup(
    inline_keyboard=[[button2], [button3], [button20]])
keyboard3 = types.InlineKeyboardMarkup(inline_keyboard=[[button4], [button20]])
keyboard4 = types.InlineKeyboardMarkup(
    inline_keyboard=[[button5], [button6], [button7]])

button9 = types.InlineKeyboardButton(text="Да", callback_data="pin_yes")
button10 = types.InlineKeyboardButton(text="Нет", callback_data="pin_no")
keyboard6 = types.InlineKeyboardMarkup(
    inline_keyboard=[[button9], [button10], [button20]])
button11 = types.InlineKeyboardButton(
    text="Опубликовать пост после настроек (через минуту)", callback_data="date_start_now")
button12 = types.InlineKeyboardButton(
    text="Подготовить конкурс", callback_data="start_new_competition")
button13 = types.InlineKeyboardButton(
    text="Завтра", callback_data="tomorrow_finish_competition")
button14 = types.InlineKeyboardButton(
    text="Через неделю", callback_data="week_finish_competition")
button15 = types.InlineKeyboardButton(
    text="Через месяц", callback_data="month_finish_competition")
button16 = types.InlineKeyboardButton(
    text="Посмотреть запущенные конкурсы", callback_data="show_all_jobs")
button17 = types.InlineKeyboardButton(
    text="Запустить конкурс", callback_data="post_command")
button18 = types.InlineKeyboardButton(
    text="Применить шаблон", callback_data="accept_template")
button19 = types.InlineKeyboardButton(
    text="Изменить шаблон", callback_data="change_template")
# button21 = types.KeyboardButton(
#     text="/prepare_new_post")
# button22 = types.KeyboardButton(
#     text="/add_channel")
# button23 = types.KeyboardButton(
#     text="/show_all_jobs")
# button21 = types.KeyboardButton(
#     text="Запустить конкурс")
# button22 = types.KeyboardButton(
#     text="Добавить канал")
# button23 = types.KeyboardButton(
#     text="Посмотреть запущенные")
button24 = types.InlineKeyboardButton(
    text="Запустить конкурс", callback_data="post")
button25 = types.InlineKeyboardButton(
    text="Запустить конкурс", callback_data="prepare_new_post")
button26 = types.InlineKeyboardButton(
    text="Добавить канал", callback_data="add_channel")
button27 = types.InlineKeyboardButton(
    text="Посмотреть запущенные", callback_data="show_all_jobs")
button28 = types.InlineKeyboardButton(
    text="Остановить повторяющийся конкурс", callback_data="stop_repeated_job")
button29 = types.InlineKeyboardButton(
    text="Да, остановить", callback_data="yes_stop_repeated_job")
button30 = types.InlineKeyboardButton(
    text="Нет, вернуться в главное меню", callback_data="dont_stop_repeated_job")

keyboard5 = types.InlineKeyboardMarkup(
    inline_keyboard=[[button24], [button8], [button20]])
keyboard7 = types.InlineKeyboardMarkup(
    inline_keyboard=[[button11], [button20]])
keyboard8 = types.InlineKeyboardMarkup(inline_keyboard=[[button12]])
keyboard9 = types.InlineKeyboardMarkup(
    inline_keyboard=[[button13], [button14], [button15], [button20]])
keyboard10 = types.InlineKeyboardMarkup(inline_keyboard=[[button16]])
keyboard11 = types.InlineKeyboardMarkup(inline_keyboard=[[button17]])
keyboard12 = types.InlineKeyboardMarkup(
    inline_keyboard=[[button18], [button19]])
keyboard13 = types.InlineKeyboardMarkup(inline_keyboard=[[button20]])
# keyboard14 = types.ReplyKeyboardMarkup(
#     keyboard=[[button21], [button22], [button23]], resize_keyboard=True, one_time_keyboard=True)
keyboard15 = types.InlineKeyboardMarkup(
    inline_keyboard=[[button25], [button26], [button27]])
keyboard16 = types.InlineKeyboardMarkup(
    inline_keyboard=[[button28], [button20]])
keyboard17 = types.InlineKeyboardMarkup(
    inline_keyboard=[[button29], [button30]])
