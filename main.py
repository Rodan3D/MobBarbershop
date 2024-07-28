"""
Этот модуль инициализирует и запускает Telegram-бота.

Он создает экземпляр бота с использованием API токена, настраивает обработчики событий и запускает бота в режиме постоянного опроса Telegram API для получения новых сообщений.
"""

import telebot
from config import API_TOKEN
from handlers import setup_handlers

# Создание экземпляра бота с использованием API токена
bot = telebot.TeleBot(API_TOKEN)

# Настройка обработчиков событий для бота
setup_handlers(bot)

if __name__ == "__main__":
    # Вывод сообщения о запуске бота
    print("Бот запущен...")
    # Запуск процесса опроса Telegram API для получения новых сообщений
    bot.polling(none_stop=True)
