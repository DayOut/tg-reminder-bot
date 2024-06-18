import json
import logging
import asyncio
from datetime import datetime, time
from telegram import Bot, Update
from telegram.error import Forbidden, NetworkError
import schedule
import os
from typing import NoReturn

# Налаштування логування
logging.basicConfig(format='%(asctime)s - %(name)s -%(message)s', level=logging.INFO)

# Отримання змінних оточення
bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '7282102903:AAF6Wp4H-kuAho8oPZblM9_PD9W7XVx6EkA')
chat_id = os.environ.get('TELEGRAM_CHAT_ID', '294086745')
events_json = os.environ.get('EVENTS', '[{"message": "Випити Animal Flex)", "timeUTC": "12:00"},{"message": "TEST", "timeUTC": "11:30"}]')
daily_report = os.environ.get('DAILY_REPORT', '12:08')
# local_timezone = os.environ.get('LOCAL_TIMEZONE', 'Europe/Kiev')  # Задання часового поясу за замовчуванням

# Завантаження та парсинг подій
events = json.loads(events_json)
bot = Bot(token=bot_token)


# Асинхронна функція для відправлення повідомлення
async def send_message(message, disable_notification=False):
    await bot.send_message(chat_id=chat_id, text=message, disable_notification=disable_notification, parse_mode='MarkdownV2')
    logging.info(f"Sent message: {message} with disable_notification={disable_notification}")


# Налаштування розкладу нагадувань
def schedule_tasks():
    for event in events:
        schedule.every().day.at(event['timeUTC']).do(asyncio.create_task, send_message(event['message']))
    schedule.every().day.at(daily_report).do(asyncio.create_task, send_message('Daily Report' + get_scheduled_tasks(), disable_notification=True))

def get_scheduled_tasks() -> str:
    message = '>Events processed: \n> \n'
    for event in events:
        # local_time = convert_time_to_local(event['time'], tz)
        message += f'>`time: {event["timeUTC"]}(+3:00) \- {event['message']}`\n'
    message += f'>`time: {daily_report}(+3:00) \- Daily report`\n'

    message += '> joblist:'
    for job in schedule.get_jobs():
        message += f'`>{job}`\n'
    return message

async def scheduler():
    async with Bot(bot_token) as bot_listener:
        # get the first pending update_id, this is so we can skip over it in case
        # we get a "Forbidden" exception.
        try:
            update_id = (await bot_listener.get_updates())[0].update_id
        except IndexError:
            update_id = None

        logging.info("listening for new messages...")
        while True:
            schedule.run_pending()
            try:
                update_id = await echo(bot_listener, update_id)
            except NetworkError:
                await asyncio.sleep(1)
            except Forbidden:
                # The user has removed or blocked the bot.
                update_id += 1
            await asyncio.sleep(1)


# Основна функція
async def main():
    current_time = datetime.now().strftime("%Y\-%m\-%d %H:%M:%S")
    start_message = f"Бот онлайн\! \nПоточний час: `{current_time}`"
    start_message += "\n\n" + get_scheduled_tasks()
    schedule_tasks()
    await send_message(start_message, disable_notification=True)

    await scheduler()


async def echo(bot: Bot, update_id: int) -> int:
    """Echo the message the user sent."""
    # Request updates after the last update_id
    updates = await bot.get_updates(offset=update_id, timeout=10, allowed_updates=Update.ALL_TYPES)
    for update in updates:
        next_update_id = update.update_id + 1

        # your bot can receive updates without messages
        # and not all messages contain text
        if update.message and update.message.text:
            if update.message.text == '/chat_id':
                await update.message.reply_text(str(update.message.chat_id))
            if update.message.text == '/stats':
                await update.message.reply_text(get_scheduled_tasks())
            # else:
            #     # Reply to the message
            #     logging.info("Found message %s!", update.message.text)
            #     await update.message.reply_text(update.message.text)
        return next_update_id
    return update_id


if __name__ == '__main__':
    asyncio.run(main())
