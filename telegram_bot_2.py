import os
import logging
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import requests
from bs4 import BeautifulSoup
from translator import translate_text_deepl
import openai

# Настройка логирования
logging.basicConfig(
    filename='bot.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Установка ключа API для OpenAI из переменной окружения
openai.api_key = os.getenv('OPENAI_API_KEY')

# Функция для парсинга новостей
def parse_news(url):
    try:
        logger.info(f"Запрос к URL: {url}")
        response = requests.get(url)
        response.raise_for_status()  # проверить, что запрос прошел успешно

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

# Функция для начала добавления комментария к новости
def start_add_comment(update, context):
    update.message.reply_text("Выберите новость, к которой хотите добавить комментарий:")
    news_list = context.user_data.get('news_list')
    if not news_list:
        update.message.reply_text("Ошибка: Список новостей пуст.")
        return ConversationHandler.END

    context.user_data['news_list'] = news_list
    context.user_data['commented_news'] = {}
    context.user_data['selected_news'] = None

    news_choices = [f"{i + 1}. {news['title']}" for i, news in enumerate(news_list)]
    update.message.reply_text("\n".join(news_choices))

    return SELECTING_NEWS

# Функция для выбора новости для добавления комментария
def select_news(update, context):
    selected_index = int(update.message.text.split(".")[0]) - 1
    news_list = context.user_data['news_list']

    if 0 <= selected_index < len(news_list):
        selected_news = news_list[selected_index]
        context.user_data['selected_news'] = selected_news
        update.message.reply_text(f"Вы выбрали новость: {selected_news['title']}. Теперь введите ваш комментарий:")
        return ADDING_COMMENT
    else:
        update.message.reply_text("Ошибка: Выбранная новость не найдена.")
        return ConversationHandler.END

# Функция для добавления комментария к выбранной новости
def add_comment(update, context):
    comment = update.message.text
    selected_news = context.user_data['selected_news']

    if selected_news:
        selected_news['comment'] = comment
        commented_news = context.user_data.get('commented_news', {})
        commented_news[selected_news['title']] = selected_news
        context.user_data['commented_news'] = commented_news

        update.message.reply_text("Комментарий сохранен. Вы можете продолжить добавлять комментарии или отправить /publish, чтобы опубликовать новости в канале.")
    else:
        update.message.reply_text("Ошибка: Новость не выбрана.")

    return SELECTING_NEWS

# Функция для публикации новостей с комментариями в канале
def publish_news(update, context):
    commented_news = context.user_data.get('commented_news', {})

    if not commented_news:
        update.message.reply_text("Ошибка: Нет новостей с комментариями для публикации.")
    else:
        channel_name = os.getenv('TELEGRAM_CHANNEL_NAME', '@your_default_channel_name')
        logger.info(f"Начало отправки новостей в канал {channel_name}")

        for title, news in commented_news.items():
            translated_title = translate_text_deepl(news['title'], 'ru')

            source = news['source']
            news_url = news['news_url']
            image_url = news['image_url']
            comment = news['comment']

            news_text = f"{translated_title}\nИсточник: {source}\n[Читать далее]({news_url})\n![image]({image_url})"
            logger.info(f"Обнаружена новая статья для отправки: {translated_title}")

            message = f"{news_text}\n\nЭкспертный комментарий:\n{comment}"
            context.bot.send_message(chat_id=channel_name, text=message, parse_mode='Markdown')
            logger.info(f"Новость отправлена: {translated_title}")

        update.message.reply_text("Все новости с комментариями опубликованы.")

    context.user_data.clear()
    return ConversationHandler.END

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

                expert_commentary = generate_expert_commentary(translated_title)  # Используем переведенный заголовок
                if expert_commentary:
                    message = f"{news_text}\n\nЭкспертный комментарий:\n{expert_commentary}"
                else:
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

# Функция для проверки, является ли статья новой
def is_new_article(article_date, last_published_article_file):
    try:
        with open(last_published_article_file, 'r') as file:
            last_published_date_str = file.read().strip()
            last_published_date = datetime.strptime(last_published_date_str, '%B %d, %Y') if last_published_date_str else datetime.min
        logger.info(f"Последняя опубликованная дата: {last_published_date}")
        logger.info(f"Дата статьи: {article_date}")
        return article_date > last_published_date
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {last_published_article_file}: {e}")
        return False

# Функция для обновления даты последней опубликованной статьи
def update_last_published_article(article_date, last_published_article_file):
    try:
        with open(last_published_article_file, 'w') as file:
            logger.info(f"Обновление файла {last_published_article_file} с датой {article_date.strftime('%B %d, %Y')}")
            file.write(article_date.strftime('%B %d, %Y'))
            logger.info(f"Файл {last_published_article_file} обновлен с датой {article_date.strftime('%B %d, %Y')}")
    except Exception as e:
        logger.error(f"Ошибка при обновлении файла {last_published_article_file}: {e}")

# Функция main
def main():
    try:
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            logger.error("Токен Telegram BOT не найден. Проверьте переменные окружения.")
            return

        updater = Updater(token)
        dp = updater.dispatcher

        dp.add_handler(CommandHandler('publish', publish_news))
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('addcomment', start_add_comment)],
            states={
                SELECTING_NEWS: [MessageHandler(Filters.text & ~Filters.command, select_news)],
                ADDING_COMMENT: [MessageHandler(Filters.text & ~Filters.command, add_comment)],
            },
            fallbacks=[],
        )
        dp.add_handler(conv_handler)

        # Остальной код остается без изменений

        updater.start_polling()
        updater.idle()

    except Exception as e:
        logger.error(f"Произошла ошибка при запуске бота: {str(e)}")

if __name__ == '__main__':
    main()


