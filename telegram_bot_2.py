import os
import openai
import logging
from datetime import datetime
from functools import partial
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
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

# Функция для генерации экспертного комментария
def generate_expert_commentary(news_title):
  try:
    openai.api_key = os.getenv('OPENAI_API_KEY')

    prompt = f"Напишите краткий экспертный комментарий на русском языке к новости с заголовком '{news_title}'."

    response = openai.Completion.create(
      engine="davinci-002", 
      prompt=prompt,
      max_tokens=150
    )
    return response.choices[0].text.strip()
  except Exception as e:
    print(f"Ошибка при генерации экспертного комментария: {str(e)}")
    return "Произошла ошибка при генерации комментария."

# Функция для ручного добавления комментария к новости  
def add_comment(update, context):
  context.user_data['current_article'] = update.message.text
  update.message.reply_text("Введите ваш экспертный комментарий:")

# Функция для обработки введенного комментария
def handle_comment(update, context):
  user_comment = update.message.text
  context.user_data['comment'] = user_comment
  update.message.reply_text("Комментарий сохранен. Используйте команду /publish для публикации.")
  
# Функция для публикации новости с комментарием в канале
def publish_news(update, context):
  article_data = context.user_data.get('current_article')
  comment = context.user_data.get('comment')
  if not article_data or not comment:
    update.message.reply_text("Ошибка: Не найдены данные статьи или комментарий для публикации.")
    return

  message = f"{article_data}\n\nЭкспертный комментарий:\n{comment}"
  context.bot.send_message(chat_id='@bawion', text=message, parse_mode='Markdown')
  update.message.reply_text("Статья с комментарием опубликована.")

  del context.user_data['current_article'] 
  del context.user_data['comment']
  
# Функции для отправки новостей и проверки новых статей  
def send_news(context: CallbackContext):
  # Ваш код для отправки новостей
  
def is_new_article(article_date, last_published_article_file):
  # Ваш код для проверки новых статей
  
def update_last_published_article(article_date, last_published_article_file):
  # Ваш код для обновления последней статьи

# Функция main
def main():
  try:
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
      logger.error("Токен Telegram BOT не найден. Проверьте переменные окружения.")
      return
    
    updater = Updater(token)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('sendnews', send_news))
    dp.add_handler(CommandHandler('addcomment', add_comment)) 
    dp.add_handler(CommandHandler('publish', publish_news))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_comment))

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
