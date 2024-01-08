import os
import logging
from telegram.ext import Updater, CommandHandler
from news_parser import parse_news
from translator import translate_text

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def is_new_article(article, last_published_article_file):
    with open(last_published_article_file, 'r') as file:
        last_published_article = file.read().strip()
    return article['title'] != last_published_article

def update_last_published_article(article, last_published_article_file):
    with open(last_published_article_file, 'w') as file:
        file.write(article['title'])

def send_news(update, context):
    channel_name = os.getenv('TELEGRAM_CHANNEL_NAME', '@your_default_channel_name')
    url = 'https://www.futuretools.io/news'
    articles = parse_news(url)

    last_published_article_file = 'last_published_article.txt'
    if articles and is_new_article(articles[0], last_published_article_file):
        article = articles[0]
        title = translate_text(article['title'])
        source = article['source']
        news_url = article['news_url']
        image_url = article['image_url']

        message = f"{title}\nИсточник: {source}\n[Читать далее]({news_url})\n![image]({image_url})"
        context.bot.send_message(chat_id=channel_name, text=message, parse_mode='Markdown')
        update_last_published_article(article, last_published_article_file)
        logger.info("Новая новость опубликована")
    else:
        logger.info("Новых новостей нет")

def send_latest_news(update, context):
    # Тело функции send_latest_news
    # (Убедитесь, что здесь используются правильные отступы)


def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('sendnews', send_news))
    dp.add_handler(CommandHandler('latestnews', send_latest_news))
    updater.start_polling()
    updater.idle()




if __name__ == '__main__':
    main()
