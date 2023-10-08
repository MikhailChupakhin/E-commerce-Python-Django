import asyncio

from aiogram import Bot
from aiogram.enums import ParseMode
from celery import shared_task
from django.conf import settings


@shared_task
def send_notification_on_create(message_text):
    TOKEN = settings.TELEGRAM_BOT_TOKEN
    AlERT_CHAT_ID = settings.ALERT_CHAT_ID

    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    asyncio.run(send_message_async(bot, AlERT_CHAT_ID, message_text))
    bot.session.close()


# Асинхронная функция для отправки сообщения
async def send_message_async(bot, chat_id, message_text):
    await bot.send_message(chat_id=chat_id, text=message_text)



