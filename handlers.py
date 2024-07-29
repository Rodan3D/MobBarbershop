"""
Этот модуль определяет обработчики для Telegram-бота, который позволяет пользователям записываться на услуги, просматривать и отменять записи.

Функции:
- setup_handlers: Настраивает все обработчики для взаимодействия с ботом.

Внутренние функции:
- main_menu: Отправляет главное меню пользователю.
- start_message: Обрабатывает команду /start и отображает главное меню.
- book_service: Обрабатывает команду "Записаться на услугу" и запускает выбор сотрудника.
- choose_employee: Отправляет пользователю список сотрудников для выбора.
- process_employee_choice: Обрабатывает выбор сотрудника и запускает выбор услуги.
- choose_service: Отправляет пользователю список услуг для выбора.
- process_service_choice: Обрабатывает выбор услуги и запускает выбор даты.
- choose_datetime: Отправляет пользователю календарь для выбора даты.
- process_calendar: Обрабатывает выбор даты или навигацию по календарю.
- process_time_choice: Обрабатывает выбор времени и подтверждает запись.
- back_to_main_menu: Возвращает пользователя в главное меню.
- back_to_choose_employee: Возвращает пользователя к выбору сотрудника.
- back_to_choose_date: Возвращает пользователя к выбору даты.
- view_appointments: Обрабатывает команду "Просмотреть записи" и отображает текущие записи пользователя.
- cancel: Обрабатывает команду "Отменить запись" и отменяет текущие записи пользователя.
"""

from calendar_utils import (create_calendar, create_time_markup,
                            get_available_times, process_calendar_selection)
from config import EMPLOYEES, SERVICES
from telebot import types


appointments = {}


def setup_handlers(bot):
    """
    Настраивает все обработчики для взаимодействия с ботом.

    Args:
        bot (telebot.TeleBot): Экземпляр Telegram-бота.
    """

    def main_menu(chat_id):
        """
        Отправляет главное меню пользователю.

        Args:
            chat_id (int): ID чата Telegram.
        """
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Записаться на услугу", "Просмотреть записи", "Отменить запись")
        bot.send_message(chat_id, "Добро пожаловать в Cтудию МОБ! \nВыберите действие:", reply_markup=markup)

    @bot.message_handler(commands=['start'])
    def start_message(message):
        """
        Обрабатывает команду /start и отображает главное меню.

        Args:
            message (telebot.types.Message): Сообщение Telegram.
        """
        main_menu(message.chat.id)

    @bot.message_handler(func=lambda message: message.text == "Записаться на услугу")
    def book_service(message):
        """
        Обрабатывает команду "Записаться на услугу" и запускает выбор сотрудника.

        Args:
            message (telebot.types.Message): Сообщение Telegram.
        """
        choose_employee(message.chat.id)

    def choose_employee(chat_id):
        """
        Отправляет пользователю список сотрудников для выбора.

        Args:
            chat_id (int): ID чата Telegram.
        """
        markup = types.InlineKeyboardMarkup()
        for employee in EMPLOYEES:
            markup.add(types.InlineKeyboardButton(employee, callback_data=f"employee_{employee}"))
        markup.add(types.InlineKeyboardButton("Назад", callback_data="main_menu"))
        bot.send_message(chat_id, "Выберите сотрудника:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('employee_'))
    def process_employee_choice(call):
        """
        Обрабатывает выбор сотрудника и запускает выбор услуги.

        Args:
            call (telebot.types.CallbackQuery): Входящий запрос от пользователя.
        """
        employee = call.data.split('employee_')[1]
        if call.message.chat.id not in appointments:
            appointments[call.message.chat.id] = []
        appointments[call.message.chat.id].append({"employee": employee})
        choose_service(call.message.chat.id, employee)

    def choose_service(chat_id, employee):
        """
        Отправляет пользователю список услуг для выбора.

        Args:
            chat_id (int): ID чата Telegram.
        """
        markup = types.InlineKeyboardMarkup()
        for service, price in SERVICES[employee]:
            markup.add(types.InlineKeyboardButton(f"{service} - {price}", callback_data=f"service_{service}"))
        markup.add(types.InlineKeyboardButton("Назад", callback_data="choose_employee"))
        bot.send_message(chat_id, "Выберите услугу:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('service_'))
    def process_service_choice(call):
        """
        Обрабатывает выбор услуги и запускает выбор даты.

        Args:
            call (telebot.types.CallbackQuery): Входящий запрос от пользователя.
        """
        service = call.data.split('service_')[1]
        if call.message.chat.id in appointments and appointments[call.message.chat.id]:
            appointments[call.message.chat.id][-1]['service'] = service
        choose_datetime(call.message.chat.id)

    def choose_datetime(chat_id, month_offset=0):
        """
        Отправляет пользователю календарь для выбора даты.

        Args:
            chat_id (int): ID чата Telegram.
            month_offset (int): Смещение месяца относительно текущего.
                                Значение по умолчанию - 0 (текущий месяц).
        """
        markup = create_calendar(month_offset)
        bot.send_message(chat_id, "Выберите дату:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('day_') or call.data in ["prev_month", "next_month", "ignore"])
    def process_calendar(call):
        """
        Обрабатывает выбор даты или навигацию по календарю.

        Args:
            call (telebot.types.CallbackQuery): Входящий запрос от пользователя.
        """
        if call.data == "next_month":
            choose_datetime(call.message.chat.id, 1)
        elif call.data == "prev_month":
            choose_datetime(call.message.chat.id, 0)
        else:
            selected_date = process_calendar_selection(call)
            if selected_date == "past_date":
                bot.send_message(call.message.chat.id, "Запись на прошедшую дату невозможна.")
            elif selected_date:
                if call.message.chat.id in appointments and appointments[call.message.chat.id]:
                    appointments[call.message.chat.id][-1]['date'] = selected_date
                available_times = get_available_times(selected_date, appointments)
                markup = create_time_markup(available_times)
                bot.send_message(call.message.chat.id, "Выберите время:", reply_markup=markup)
            else:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                              reply_markup=create_calendar())

    @bot.callback_query_handler(func=lambda call: call.data.startswith('time_'))
    def process_time_choice(call):
        """
        Обрабатывает выбор времени и подтверждает запись.

        Args:
            call (telebot.types.CallbackQuery): Входящий запрос от пользователя.
        """
        time = call.data.split('time_')[1]
        selected_date = appointments[call.message.chat.id][-1].get('date')
        datetime_str = f"{selected_date} {time}"
        if call.message.chat.id in appointments and appointments[call.message.chat.id]:
            appointments[call.message.chat.id][-1]['datetime'] = datetime_str
        appointment = appointments[call.message.chat.id][-1]
        bot.send_message(call.message.chat.id,
                         f"Вы записаны!\nСотрудник: {appointment['employee']}\nУслуга: {appointment['service']}\nДата и время: {appointment['datetime']}")
        main_menu(call.message.chat.id)

    @bot.callback_query_handler(func=lambda call: call.data == "main_menu")
    def back_to_main_menu(call):
        """
        Возвращает пользователя в главное меню.

        Args:
            call (telebot.types.CallbackQuery): Входящий запрос от пользователя.
        """
        main_menu(call.message.chat.id)

    @bot.callback_query_handler(func=lambda call: call.data == "choose_employee")
    def back_to_choose_employee(call):
        """
        Возвращает пользователя к выбору сотрудника.

        Args:
            call (telebot.types.CallbackQuery): Входящий запрос от пользователя.
        """
        choose_employee(call.message.chat.id)

    @bot.callback_query_handler(func=lambda call: call.data == "choose_date")
    def back_to_choose_date(call):
        """
        Возвращает пользователя к выбору даты.

        Args:
            call (telebot.types.CallbackQuery): Входящий запрос от пользователя.
        """
        choose_datetime(call.message.chat.id)

    @bot.message_handler(func=lambda message: message.text == "Просмотреть записи")
    def view_appointments(message):
        """
        Обрабатывает команду "Просмотреть записи" и отображает текущие записи пользователя.

        Args:
            message (telebot.types.Message): Сообщение Telegram.
        """
        user_appointments = appointments.get(message.chat.id, [])
        if user_appointments:
            response = "Ваши записи:\n"
            for i, appointment in enumerate(user_appointments, 1):
                response += f"Запись №{i}\nСотрудник: {appointment['employee']}\nУслуга: {appointment['service']}\nДата и время: {appointment['datetime']}\n"
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "У вас нет записей.")
        main_menu(message.chat.id)

    @bot.message_handler(func=lambda message: message.text == "Отменить запись")
    def cancel(message):
        """
        Обрабатывает команду "Отменить запись" и отменяет текущие записи пользователя.

        Args:
            message (telebot.types.Message): Сообщение Telegram.
        """
        user_appointments = appointments.get(message.chat.id, [])
        if user_appointments:
            markup = types.InlineKeyboardMarkup()
            for i, appointment in enumerate(user_appointments, 1):
                button_text = f"{i}. {appointment['employee']} - {appointment['service']} - {appointment['datetime']}"
                markup.add(types.InlineKeyboardButton(button_text, callback_data=f"cancel_{i}"))
            markup.add(types.InlineKeyboardButton("Назад", callback_data="main_menu"))
            bot.send_message(message.chat.id, "Выберите запись для отмены:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "У вас нет записей для отмены.")
        main_menu(message.chat.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_'))
    def process_cancel_choice(call):
        """
        Обрабатывает выбор отмены записи и удаляет выбранную запись.

        Args:
            call (telebot.types.CallbackQuery): Входящий запрос от пользователя.
        """
        appointment_index = int(call.data.split('cancel_')[1]) - 1
        user_appointments = appointments.get(call.message.chat.id, [])
        if 0 <= appointment_index < len(user_appointments):
            del user_appointments[appointment_index]
            if user_appointments:
                appointments[call.message.chat.id] = user_appointments
            else:
                del appointments[call.message.chat.id]
            bot.send_message(call.message.chat.id, "Запись отменена.")
        else:
            bot.send_message(call.message.chat.id, "Неверный выбор. Попробуйте снова.")
        main_menu(call.message.chat.id)
