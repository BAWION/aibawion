import os
from telegram.ext import Updater, CommandHandler
from news_parser import parse_news
from translator import translate_text

def is_new_article(article, last_published_article_file):
    with open(last_published_article_file, 'r') as file:
        last_published_article = file.read().strip()
    return article['title'] != last_published_article

def update_last_published_article(article, last_published_article_file):
    with open(last_published_article_file, 'w') as file:
        file.write(article['title'])

def send_news_if_new():
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
        channel_name = os.getenv('TELEGRAM_CHANNEL_NAME', '@your_channel_name')
        context.bot.send_message(chat_id=channel_name, text=message, parse_mode='Markdown')
        update_last_published_article(article, last_published_article_file)

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('sendnews', send_news_if_new))  # Обновленный обработчик команд
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
