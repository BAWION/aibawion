import os
import logging
from datetime import datetime
from telegram.ext import Updater, CommandHandler
from news_parser import parse_news
from translator import translate_text
from apscheduler.schedulers.background import BackgroundScheduler

# Настройка логирования
logging.basicConfig(
    filename='bot.log',  # Логи будут сохраняться в файл bot.log
    filemode='a',  # Добавление к существующему файлу
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def is_new_article(article_date, last_published_article_file):
    try:
        with open(last_published_article_file, 'r') as file:
            last_published_date_str = file.read().strip()
            last_published_date = datetime.strptime(last_published_date_str, '%B %d, %Y') if last_published_date_str else datetime.min
        return article_date > last_published_date
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {last_published_article_file}: {e}")
        return False

def update_last_published_article(article_date, last_published_article_file):
    try:
        with open(last_published_article_file, 'w') as file:
            file.write(article_date.strftime('%B %d, %Y'))
        logger.info(f"Обновлена дата последней новости: {article_date.strftime('%B %d, %Y')}")
    except Exception as e:
        logger.error(f"Ошибка при обновлении файла {last_published_article_file}: {e}")

def send_news(context):
    channel_name = os.getenv('TELEGRAM_CHANNEL_NAME', '@your_default_channel_name')
    url = 'https://www.futuretools.io/news'
    articles = parse_news(url)
    if not articles:
        logger.info("Новостей для отправки нет.")
        return

    last_published_article_file = 'last_published_article.txt'
    latest_article_date = datetime.min

    for article in articles:
        try:
            article_date = datetime.strptime(article['date'], '%B %d, %Y')
            if is_new_article(article_date, last_published_article_file):
                title = translate_text(article['title'])
                source = article['source']
                news_url = article['news_url']
                image_url = article['image_url']

                message = f"{title}\nИсточник: {source}\n[Читать далее]({news_url})\n![image]({image_url})"
                context.bot.send_message(chat_id=channel_name, text=message, parse_mode='Markdown')
                latest_article_date = max(latest_article_date, article_date)
                logger.info(f"Отправляется новость: {title}")
        except Exception as e:
            logger.error(f"Ошибка при обработке новости: {e}")

    if latest_article_date > datetime.min:
        update_last_published_article(latest_article_date, last_published_article_file)

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    updater = Updater(token, use_context=True)
    job_queue = updater.job_queue

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('sendnews', send_news))

    # Настройка планировщика для регулярной отправки новостей
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_news, 'interval', minutes=2, args=(updater.bot,))
    scheduler.start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
