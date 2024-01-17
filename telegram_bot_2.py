import os
import logging
from datetime import datetime
from functools import partial
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext, ReplyKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import requests
from bs4 import BeautifulSoup
from translator import translate_text_deepl

# Настройка логирования
logging.basicConfig(
    filename='bot.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Глобальные переменные для хранения состояния бота
SELECTING_NEWS, ADDING_COMMENT = range(2)
news_to_comment = {}

# Функция для парсинга новостей
def parse_news(url):
    try:
        logger.info(f"Запрос к URL: {url}")
        response = requests.get(url)
        response.raise_for_status()  # Убедитесь, что запрос прошел успешно
        soup = BeautifulSoup(response.content, 'html.parser')

        articles = []
        for article in soup.find_all('div', class_='collection-item-6'):
            # Найти дату новости
            date_div = article.find('div', class_='text-block-30')
            date_text = date_div.text.strip() if date_div else 'Дата отсутствует'

            # Найти заголовок новости
            title_div = article.find('div', class_='text-block-27')
            title_text = title_div.text.strip() if title_div else 'Нет заголовка'

            # Найти домен источника новости
            source_div = article.find('div', class_='text-block-28')
            source_text = source_div.text.strip() if source_div else 'Нет источника'

            # Найти URL изображения
            image = article.find('img')
            image_url = image['src'] if image and 'src' in image.attrs else 'URL изображения отсутствует'

            # Собрать URL новости
            news_url = article.a['href'] if article.a and 'href' in article.a.attrs else 'URL новости отсутствует'

            articles.append({
                'date': date_text,
                'title': title_text,
                'source': source_text,
                'image_url': image_url,
                'news_url': news_url
            })

        logger.info(f"Найдено {len(articles)} новостей")
        return articles
    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        return []

# Функция для отправки новостей и комментариев в Telegram
def send_news(context: CallbackContext):
    try:
        channel_name = os.getenv('TELEGRAM_CHANNEL_NAME', '@your_default_channel_name')
        logger.info(f"Начало отправки новостей в канал {channel_name}")
        url = 'https://www.futuretools.io/news'
        articles = parse_news(url)
        
        if not articles:
            logger.info("Новостей для отправки нет.")
            return

        last_published_article_file = 'last_published_article.txt'
        latest_article_date = datetime.min

        for article in articles:
            article_date = datetime.strptime(article['date'], '%B %d, %Y')
            if is_new_article(article_date, last_published_article_file):
                original_title = article['title']
                target_language = 'ru'  # Устанавливаем русский язык как целевой для перевода

                translated_title = translate_text_deepl(original_title, target_language)

                source = article['source']
                news_url = article['news_url']
                image_url = article['image_url']

                news_text = f"{translated_title}\nИсточник: {source}\n[Читать далее]({news_url})\n![image]({image_url})"
                logger.info(f"Обнаружена новая статья для отправки: {translated_title}")

                message = news_text

                try:
                    context.bot.send_message(chat_id=channel_name, text=message, parse_mode='Markdown')
                    logger.info(f"Новость отправлена: {translated_title}")
                    latest_article_date = max(latest_article_date, article_date)
                except Exception as e:
                    logger.error(f"Ошибка при отправке новости {translated_title}: {e}")
            else:
                logger.info("Статья не прошла проверку is_new_article и не будет отправлена.")

        if latest_article_date > datetime.min:
            update_last_published_article(latest_article_date, last_published_article_file)
            logger.info(f"Дата последней опубликованной новости обновлена: {latest_article_date.strftime('%B %d, %Y')}")

        logger.info("Завершение отправки новостей")
    except Exception as e:
        logger.error(f"Произошла ошибка при отправке новостей: {str(e)}")


# Функция для обработки команды /start
def start(update, context):
    user_id = update.message.from_user.id
    if user_id == YOUR_ADMIN_USER_ID:
        context.bot.send_message(chat_id=user_id, text="Вы администратор бота.")
    else:
        context.bot.send_message(chat_id=user_id, text="Привет! Я бот для управления функциями.")

# Создание объекта Updater и Dispatcher
def main():
    try:
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            logger.error("Токен Telegram BOT не найден. Проверьте переменные окружения.")
            return

        updater = Updater(token)
        dp = updater.dispatcher

        dp.add_handler(CommandHandler('start', start))

        # Создание ConversationHandler для управления состояниями бота
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                SELECTING_NEWS: [MessageHandler(Filters.text, select_news)],
                ADDING_COMMENT: [MessageHandler(Filters.text, add_comment)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        dp.add_handler(conv_handler)

        # Настройка планировщика для регулярной отправки новостей
        scheduler = BackgroundScheduler(timezone=pytz.utc)
        job = partial(send_news, context=updater.job_queue)
        scheduler.add_job(job, 'interval', minutes=150)
        scheduler.start()

        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(f"Произошла ошибка при запуске бота: {str(e)}")

if __name__ == '__main__':
    main()
