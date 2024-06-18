import json
import logging
import asyncio
from datetime import datetime, time
from telegram import Bot
import schedule
import os
from pytz import timezone, utc

# Налаштування логування
logging.basicConfig(format='%(asctime)s - %(name)s -%(message)s', level=logging.INFO)

# Отримання змінних оточення
bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '7282102903:AAF6Wp4H-kuAho8oPZblM9_PD9W7XVx6EkA')
chat_id = os.environ.get('TELEGRAM_CHAT_ID', '294086745')
events_json = os.environ.get('EVENTS', '[{"message": "Випити Animal Flex)", "time": "14:00"},{"message": "TEST", "time": "13:00"}]')
local_timezone = os.environ.get('LOCAL_TIMEZONE', 'Europe/Kiev')  # Задання часового поясу за замовчуванням

# Завантаження та парсинг подій
events = json.loads(events_json)
bot = Bot(token=bot_token)


# Конвертація часу подій у локальний часовий пояс
def convert_time_to_local(event_time, tz):
    event_time_utc = datetime.strptime(event_time, "%H:%M").time()
    event_time_local = datetime.combine(datetime.today(), event_time_utc).replace(tzinfo=utc).astimezone(tz)
    return event_time_local.strftime("%H:%M")


def convert_time_to_utc(event_time, event_timezone):
    tz_event = timezone(event_timezone)
    event_datetime = datetime.strptime(event_time, "%H:%M")
    event_datetime_tz = tz_event.localize(event_datetime)
    event_datetime_utc = event_datetime_tz.astimezone(utc)
    return event_datetime_utc.strftime("%H:%M")


# Асинхронна функція для відправлення повідомлення
async def send_message(message, disable_notification=False):
    await bot.send_message(chat_id=chat_id, text=message, disable_notification=disable_notification)
    logging.info(f"Sent message: {message} with disable_notification={disable_notification}")


# Налаштування розкладу нагадувань
async def schedule_tasks():
    tz = timezone(local_timezone)
    for event in events:
        # local_time = convert_time_to_local(event['time'], tz)
        local_time = convert_time_to_utc(event['time'], local_timezone)
        schedule.every().day.at(local_time).do(asyncio.create_task, send_message(event['message']))
        await send_message(f"Задано нагадування {event['message']} на час {local_time}",
                           disable_notification=True)


async def scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


# Основна функція
async def main():
    # Отримання поточної дати та часу з врахуванням часового поясу
    tz = timezone(local_timezone)
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    # Відправлення повідомлення при старті програми без сповіщення
    await send_message(f"Програма запущена! Нагадування активні. Поточний час: {current_time}",
                       disable_notification=True)

    await schedule_tasks()
    await scheduler()


if __name__ == '__main__':
    asyncio.run(main())
