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

        # Распечатать содержимое soup для отладки
        print(soup.prettify())

        articles = []
        for article in soup.find_all('div', class_='news-item'):
            date_element = article.find('div', class_='date')
            date_text = date_element.text.strip() if date_element else 'Дата отсутствует'

            title_element = article.find('div', class_='title')
            title_text = title_element.text.strip() if title_element else 'Нет заголовка'

            source_element = article.find('div', class_='source')
            source_text = source_element.text.strip() if source_element else 'Нет источника'

            image_element = article.find('img', class_='thumbnail')
            image_url = image_element['src'] if image_element and 'src' in image_element.attrs else 'URL изображения отсутствует'

            news_url_element = article.find('a', class_='news-link')
            news_url = news_url_element['href'] if news_url_element and 'href' in news_url_element.attrs else 'URL новости отсутствует'

            articles.append({
                'date': date_text,
                'title': title_text,
                'source': source_text,
                'image_url': image_url,
                'news_url': news_url
            })

        if not articles:
            logger.info("Не найдено новостей на странице")
        else:
            logger.info(f"Найдено {len(articles)} новостей")

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
