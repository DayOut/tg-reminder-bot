import json
import logging
import asyncio
from datetime import datetime
from telegram import Bot
import schedule

# Налаштування логування
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Читання конфігураційного файлу
with open('cfg.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

bot_token = config['token']
chat_id = config['chat_id']
events = config['events']

bot = Bot(token=bot_token)

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
    logging.info(f"Starting bot at {datetime.now()}")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info(f"Closing bot at {datetime.now()}. Reason: keyboard interrupt")
        exit()
    except Exception as e:
        logging.info(f"Closing bot at {datetime.now()}. Reason: {e}")
        exit()
