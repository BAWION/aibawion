
import os
from telegram.ext import Updater, CommandHandler
from news_parser import parse_news
from translator import translate_text

def send_news(update, context):
    url = 'https://www.futuretools.io/news'
    articles = parse_news(url)

    for article in articles:
        title = translate_text(article['title'])
        summary = translate_text(article['summary'])
        message = f"{title}\n{summary}\n{article['image_url']}"
        context.bot.send_message(chat_id='@your_channel_name', text=message)

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('sendnews', send_news))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
