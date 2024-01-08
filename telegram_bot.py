import os
from telegram.ext import Updater, CommandHandler
from news_parser import parse_news
from translator import translate_text

def send_news(update, context):
    channel_name = os.getenv('TELEGRAM_CHANNEL_NAME', '@your_default_channel_name')
    url = 'https://www.futuretools.io/news'
    articles = parse_news(url)

    for article in articles:
        title = translate_text(article['title'])
        source = article['source']
        news_url = article['news_url']
        image_url = article['image_url']

        message = f"{title}\nИсточник: {source}\n[Читать далее]({news_url})\n![image]({image_url})"
        context.bot.send_message(chat_id=channel_name, text=message, parse_mode='Markdown')

def send_latest_news(update, context):
    channel_name = os.getenv('TELEGRAM_CHANNEL_NAME', '@your_default_channel_name')
    url = 'https://www.futuretools.io/news'
    articles = parse_news(url)

    if articles:
        article = articles[0]  # Берем первую новость из списка
        title = translate_text(article['title'])
        source = article['source']
        news_url = article['news_url']
        image_url = article['image_url']

        message = f"{title}\nИсточник: {source}\n[Читать далее]({news_url})\n![image]({image_url})"
        context.bot.send_message(chat_id=channel_name, text=message, parse_mode='Markdown')
    else:
        context.bot.send_message(chat_id=channel_name, text="Новости отсутствуют.")

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')  # Получение токена из переменных окружения
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('sendnews', send_news))
    dp.add_handler(CommandHandler('latestnews', send_latest_news))  # Команда для отправки последней новости
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
