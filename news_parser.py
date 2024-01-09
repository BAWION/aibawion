import requests
from bs4 import BeautifulSoup
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

def parse_news(url):
    try:
        logger.info(f"Запрос к URL: {url}")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        articles = []
        for article in soup.find_all('a', class_='link-block-8'):
            date_div = article.find_previous_sibling('div', class_='text-block-30')
            date_text = date_div.text.strip() if date_div else 'Дата отсутствует'

            title = article.find('div', class_='text-block-27')
            title_text = title.text.strip() if title else 'Нет заголовка'

            source = article.find('div', class_='text-block-28')
            source_text = source.text.strip() if source else 'Нет источника'

            image = article.find('img')
            image_url = image['src'] if image and 'src' in image.attrs else 'URL изображения отсутствует'

            news_url = article['href'] if 'href' in article.attrs else 'URL новости отсутствует'

            articles.append({
                'date': date_text,
                'title': title_text,
                'source': source_text,
                'image_url': image_url,
                'news_url': news_url
            })

        logger.info("Парсинг завершен успешно")
        return articles
    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        return []

# Пример использования функции
if __name__ == '__main__':
    url = 'https://www.futuretools.io/news'
    logger.info("Начало парсинга сайта")
    news_articles = parse_news(url)
    for article in news_articles:
        print(f"Дата: {article['date']}")
        print(f"Заголовок: {article['title']}")
        print(f"Источник: {article['source']}")
        print(f"URL изображения: {article['image_url']}")
        print(f"URL новости: {article['news_url']}\n")
    logger.info("Завершение парсинга сайта")
