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

# Определение состояний для ConversationHandler
SELECTING_NEWS, ADDING_COMMENT = range(2)

# Настройка логирования
logging.basicConfig(
    filename='bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Установка ключа API для OpenAI из переменной окружения
openai.api_key = os.getenv('OPENAI_API_KEY')

# Функция для парсинга новостей
def parse_news(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = []
        for article in soup.find_all('article'):
            title = article.h2.text
            url = article.a['href']
            image = article.img['src']
            
            date_str = article.find('time')['datetime']
            date = datetime.strptime(date_str, '%Y-%m-%d')
            
            articles.append({'title': title, 'url': url, 'img': image, 'date': date})

        return articles
    
    except Exception as e:
        print('Error parsing news:', e)
        return []
        
# Функция для начала добавления комментария к новости
def start_add_comment(update, context):
    news = context.user_data['news']
    
    keyboard = [[i] for i in range(len(news))]
    update.message.reply_text('Choose news to comment:', 
                              reply_markup=ReplyKeyboardMarkup(keyboard))
                              
    return SELECTING_NEWS

# Функция для выбора новости для добавления комментария  
def select_news(update, context):
    selected = int(update.message.text)
    if 0 <= selected < len(context.user_data['news']):
        context.user_data['selected'] = selected
        update.message.reply_text('Enter your comment:')
        return ADDING_COMMENT
    else:
        update.message.reply_text('Invalid choice')
        return ConversationHandler.END
        
# Функция для добавления комментария к выбранной новости
def add_comment(update, context):
    comment = update.message.text
    selected = context.user_data['selected']
    
    context.user_data['news'][selected]['comment'] = comment 
    update.message.reply_text('Comment added!')

    return ConversationHandler.END
    
# Функция для публикации новостей с комментариями в канале  
def publish_news(update, context):
    news = context.user_data['news']
    
    for n in news:
        text = '{}\n{}\n\nComment: {}'.format(n['title'], n['url'], n.get('comment'))
        context.bot.send_message(chat_id='@channel', text=text)

    update.message.reply_text('News published!')
      
# Функция для отправки новостей в Telegram
def send_news(context):
    news = parse_news('https://example.com')
    context.user_data['news'] = news

    if news:
        context.bot.send_message(chat_id='@me', text='Got {} news'.format(len(news)))
    else:
        context.bot.send_message(chat_id='@me', text='No news')
        
def main():
    updater = Updater('TOKEN')
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start_add_comment)) 
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('comment', start_add_comment)],
        states={
            SELECTING_NEWS: [MessageHandler(Filters.text, select_news)],
            ADDING_COMMENT: [MessageHandler(Filters.text, add_comment)]
        },
        fallbacks=[]
    ))
    
    dispatcher.add_handler(CommandHandler('publish', publish_news))
    dispatcher.add_handler(CommandHandler('send', send_news))

    scheduler = BackgroundScheduler()
    scheduler.add_job(send_news, 'interval', minutes=5)
    scheduler.start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
