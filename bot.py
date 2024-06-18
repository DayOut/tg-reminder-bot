import json
import logging
import asyncio
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
async def send_message(message):
    await bot.send_message(chat_id=chat_id, text=message)
    logging.info(f"Sent message: {message}")

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
    schedule_tasks()
    await scheduler()

if __name__ == '__main__':
    events = json.loads(events_json)

    bot = Bot(token=bot_token)
    asyncio.run(main())
