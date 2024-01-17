import os
import logging 
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import requests
from bs4 import BeautifulSoup

# Определение состояний для ConversationHandler
SELECTING_NEWS, ADDING_COMMENT = range(2)

# Настройка логирования
logging.basicConfig(
    filename='bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функция для парсинга новостей
def parse_news(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = []
        for article in soup.find_all('article'):
            title = article.h2.text
            news_url = article.a['href']
            image_url = article.img['src'] if article.img else None
            
            date_str = article.find('time')['datetime'] if article.find('time') else None
            date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else None
            
            articles.append({'title': title, 'url': news_url, 'image': image_url, 'date': date})

        return articles
    
    except Exception as e:
        logger.error(f'Error parsing news: {e}')
        return []

# Функция для проверки, является ли статья новой
def is_new_article(article_date, last_published_article_file):
    try:
        with open(last_published_article_file, 'r') as file:
            last_published_date_str = file.read().strip()
            last_published_date = datetime.strptime(last_published_date_str, '%B %d, %Y') if last_published_date_str else datetime.min
        return article_date > last_published_date
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {last_published_article_file}: {e}")
        return False

# Функция для обновления даты последней опубликованной статьи
def update_last_published_article(article_date, last_published_article_file):
    try:
        with open(last_published_article_file, 'w') as file:
            file.write(article_date.strftime('%B %d, %Y'))
    except Exception as e:
        logger.error(f"Ошибка при обновлении файла {last_published_article_file}: {e}")

# Функция для автоматической отправки новостей в Telegram бот
def send_news(context: CallbackContext):
    try:
        url = 'https://www.futuretools.io/news'
        articles = parse_news(url)

        if not articles:
            logger.info("Новостей для отправки нет.")
            return

        last_published_article_file = 'last_published_article.txt'
        for article in articles:
            article_date = article['date']
            if is_new_article(article_date, last_published_article_file):
                news_text = f"{article['title']}\n[Читать далее]({article['url']})"
                context.bot.send_message(chat_id='@channel_bawion_bot', text=news_text)
                update_last_published_article(article_date, last_published_article_file)
    except Exception as e:
        logger.error(f"Произошла ошибка при отправке новостей: {str(e)}")

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    # Обработчик команды для начала добавления комментария к новости
    dp.add_handler(CommandHandler('start', start_add_comment))
    
    # Обработчики для добавления комментария и публикации новости
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('comment', start_add_comment)],
        states={
            SELECTING_NEWS: [MessageHandler(Filters.text, select_news)],
            ADDING_COMMENT: [MessageHandler(Filters.text, add_comment)]
        },
        fallbacks=[]
    )
    dp.add_handler(conv_handler)

    # Обработчик команды для публикации новостей с комментариями в канале
    dp.add_handler(CommandHandler('publish', publish_news))

    # Обработчик команды для отправки новостей в бот
    dp.add_handler(CommandHandler('sendnews', send_news))

    # Настройка планировщика для регулярной отправки новостей
    scheduler = BackgroundScheduler(timezone=pytz.utc)
    scheduler.add_job(send_news, 'interval', minutes=60, args=[updater])
    scheduler.start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
