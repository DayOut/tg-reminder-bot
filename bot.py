import json
import logging
import asyncio
from datetime import datetime, time
from telegram import Bot, Update, helpers
from telegram.error import Forbidden, NetworkError
import schedule
from variables import bot_token, chat_id, events_json, daily_report, time_delta, is_start_message
import os
from typing import NoReturn

# Налаштування логування
logging.basicConfig(format='%(asctime)s - %(name)s -%(message)s', level=logging.INFO)


# Завантаження та парсинг подій
events = json.loads(events_json)
bot = Bot(token=bot_token)


# Асинхронна функція для відправлення повідомлення
async def send_message(message, disable_notification=False):
    logging.info(f"Sending message: {message} with disable_notification={disable_notification}")
    # await bot.send_message(chat_id=chat_id, text=message, disable_notification=disable_notification, parse_mode='MarkdownV2')
    await bot.send_message(chat_id=chat_id, text=message, disable_notification=disable_notification, parse_mode='MarkdownV2')
    logging.info(f"Sent message: {message} with disable_notification={disable_notification}")


def create_send_message_task(message, disable_notification=False):
    return asyncio.create_task(send_message(message, disable_notification=disable_notification))


# Налаштування розкладу нагадувань
def schedule_tasks():
    for event in events:
        logging.info(f"Schedule message: {event['message']} at {event['timeUTC']}")
        message = helpers.escape_markdown(event['message'], version=2)
        schedule.every().day.at(event['timeUTC']).do(create_send_message_task, message)
    #schedule.every().day.at(daily_report).do(create_send_message_task, 'Daily Report\n' + get_scheduled_tasks(),
                                       #disable_notification=True)


def get_scheduled_tasks() -> str:
    message = '>Events processed: \n> \n'
    for event in events:
        hours, minutes = event['timeUTC'].split(':')
        # local_time = convert_time_to_local(event['time'], tz)
        message += f'>`time: {int(hours) + int(time_delta)}:{minutes} \(UTC: {event['timeUTC']}\) \- {event['message']}`\n'
    hours, minutes = daily_report.split(':')
    message += f'>`time: {int(hours) + int(time_delta)}:{minutes} \(UTC: {daily_report}\) \- Daily report`\n'
    return message


async def scheduler():
    try:
        update_id = (await bot.get_updates())[0].update_id
    except IndexError:
        update_id = None

    logging.info("listening for new messages...")
    while True:
        schedule.run_pending()
        try:
            update_id = await echo(bot, update_id)
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
    schedule_tasks()
    start_message += "\n\n" + get_scheduled_tasks()
    if eval(is_start_message):
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
                await update.message.reply_text(f"```{str(update.message.chat_id)}```\n\n", parse_mode='MarkdownV2')
            if update.message.text == '/stats':
                current_time = datetime.now().strftime("%Y\-%m\-%d %H:%M:%S")
                message = f"Поточний час: ```{current_time}```\n"
                message += get_scheduled_tasks()
                await update.message.reply_text(message, parse_mode='MarkdownV2')
        return next_update_id
    return update_id


if __name__ == '__main__':
    asyncio.run(main())
