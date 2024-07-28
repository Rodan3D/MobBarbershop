"""
Этот модуль предоставляет функции для создания календаря и управления выбором дат и времени в Telegram-боте.

Функции:
- get_current_datetime: Возвращает текущую дату и время.
- create_calendar: Создает календарь на выбранный месяц с возможностью переключения месяцев.
- process_calendar_selection: Обрабатывает выбор даты из календаря.
- get_available_times: Возвращает доступные временные слоты для выбранной даты, исключая уже занятые.
- create_time_markup: Создает клавиатуру с доступными временными слотами для выбора.
"""

import calendar
from datetime import datetime, timedelta

from telebot import types


def get_current_datetime():
    """
    Возвращает текущую дату и время.

    Returns:
        datetime: Текущая дата и время.
    """
    return datetime.now()


def create_calendar(month_offset=0):
    """
    Создает календарь на выбранный месяц с возможностью переключения месяцев.

    Args:
        month_offset (int): Смещение месяца относительно текущего.
                            Значение по умолчанию - 0 (текущий месяц).

    Returns:
        types.InlineKeyboardMarkup: Разметка клавиатуры с календарем.
    """
    now = get_current_datetime() + timedelta(days=30 * month_offset)
    markup = types.InlineKeyboardMarkup()

    # Добавление месяца и года
    markup.row(
        types.InlineKeyboardButton(f"{now.strftime('%B %Y')}", callback_data="ignore")
    )

    # Добавление дней недели
    week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    markup.row(*[types.InlineKeyboardButton(day, callback_data="ignore") for day in week_days])

    # Добавление дней месяца
    month_calendar = calendar.monthcalendar(now.year, now.month)
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
            else:
                row.append(types.InlineKeyboardButton(str(day), callback_data=f"day_{now.month}_{day}"))
        markup.row(*row)

    # Навигационные кнопки
    if month_offset == 0:
        markup.row(
            types.InlineKeyboardButton(">>", callback_data="next_month")
        )
    else:
        markup.row(
            types.InlineKeyboardButton("<<", callback_data="prev_month"),
            types.InlineKeyboardButton(">>", callback_data="next_month")
        )

    markup.row(types.InlineKeyboardButton("Назад", callback_data="choose_service"))
    return markup


def process_calendar_selection(call):
    """
    Обрабатывает выбор даты из календаря.

    Args:
        call: Входящий вызов от Telegram-бота.

    Returns:
        str или None: Выбранная дата в формате 'dd.mm.yyyy' или "past_date" если выбрана прошлая дата.
                      None, если дата не была выбрана.
    """
    data = call.data
    if data.startswith('day_'):
        _, month, day = data.split('_')
        now = get_current_datetime()
        selected_date = datetime(now.year, int(month), int(day))
        if selected_date < now and selected_date.date() != now.date():
            return "past_date"
        return selected_date.strftime('%d.%m.%Y')
    return None


def get_available_times(selected_date, current_appointments):
    """
    Возвращает доступные временные слоты для выбранной даты, исключая уже занятые.

    Args:
        selected_date (str): Выбранная дата в формате 'dd.mm.yyyy'.
        current_appointments (list): Список текущих назначений.

    Returns:
        list: Список доступных временных слотов в формате 'HH:MM'.
    """
    all_times = [
        "10:00", "10:30", "11:00", "11:30",
        "12:00", "12:30", "13:00", "13:30",
        "14:00", "14:30", "15:00", "15:30",
        "16:00", "16:30", "17:00", "17:30",
        "18:00", "18:30", "19:00", "19:30"
    ]
    available_times = []

    now = get_current_datetime()
    current_date = now.strftime('%d.%m.%Y')

    for time in all_times:
        appointment_datetime = f"{selected_date} {time}"
        appointment_time = datetime.strptime(appointment_datetime, '%d.%m.%Y %H:%M')

        if selected_date == current_date and appointment_time <= now:
            continue

        if appointment_datetime not in current_appointments:
            available_times.append(time)

    return available_times


def create_time_markup(available_times):
    """
    Создает клавиатуру с доступными временными слотами для выбора.

    Args:
        available_times (list): Список доступных временных слотов в формате 'HH:MM'.

    Returns:
        types.InlineKeyboardMarkup: Разметка клавиатуры с временными слотами.
    """
    markup = types.InlineKeyboardMarkup()
    for time in available_times:
        markup.add(types.InlineKeyboardButton(time, callback_data=f"time_{time}"))
    markup.add(types.InlineKeyboardButton("Назад", callback_data="choose_date"))
    return markup
