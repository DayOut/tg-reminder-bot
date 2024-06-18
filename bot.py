import json
import logging
import asyncio
from datetime import datetime
from telegram import Bot
import schedule
import os

# Налаштування логування
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelень)-%(message)s', level=logging.INFO)

# Отримання змінних оточення
bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')
events_json = os.environ.get('EVENTS')


# Асинхронна функція для відправлення повідомлення
async def send_message(message, disable_notification=False):
    await bot.send_message(chat_id=chat_id, text=message, disable_notification=disable_notification)
    logging.info(f"Sent message: {message} with disable_notification={disable_notification}")


# Налаштування розкладу нагадувань
def schedule_tasks():
    for event in events:
        schedule.every().day.at(event['time']).do(asyncio.create_task, send_message(event['message']))


async def scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


# Основна функція
async def main():
    # Отримання поточної дати та часу
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Відправлення повідомлення при старті програми без сповіщення
    await send_message(f"Програма запущена! Нагадування активні. Поточний час: {current_time}",
                       disable_notification=True)

    schedule_tasks()
    await scheduler()


if __name__ == '__main__':
    events = json.loads(events_json)
    bot = Bot(token=bot_token)
    asyncio.run(main())
