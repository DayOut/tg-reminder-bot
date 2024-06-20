import os

# Отримання змінних оточення
bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '7282102903:AAF6Wp4H-kuAho8oPZblM9_PD9W7XVx6EkA')
chat_id = os.environ.get('TELEGRAM_CHAT_ID', '294086745')
events_json = os.environ.get('EVENTS', '[{"message": "Випити Animal Flex)", "timeUTC": "12:00", "type": "daily"},{"message": "TEST", "timeUTC": "11:30", "type": "hourly"}]')
daily_report = os.environ.get('DAILY_REPORT', '08:00')
time_delta = os.environ.get('TIME_DELTA', '3')
is_start_message = os.environ.get('START_MESSAGE', 'True')