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
        for item in soup.find_all("div", class_="w-dyn-item"):
            # Парсинг даты
            date_element = item.find("div", class_="text-block-30")
            date_text = date_element.text.strip() if date_element else 'Дата отсутствует'

            # Парсинг заголовка и URL новости
            link_element = item.find("a", class_="link-block-8")
            title_element = link_element.find("div", class_="text-block-27")
            title_text = title_element.text.strip() if title_element else 'Нет заголовка'
            news_url = link_element['href'] if link_element and 'href' in link_element.attrs else 'URL новости отсутствует'

            # Парсинг источника
            source_element = item.find("div", class_="text-block-28")
            source_text = source_element.text.strip() if source_element else 'Нет источника'

            # Парсинг URL изображения
            image_element = item.find("img")
            image_url = image_element['src'] if image_element and 'src' in image_element.attrs else 'URL изображения отсутствует'

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
    news_articles = parse_news(url)
    for article in news_articles:
        print(f"Дата: {article['date']}")
        print(f"Заголовок: {article['title']}")
        print(f"Источник: {article['source']}")
        print(f"URL изображения: {article['image_url']}")
        print(f"URL новости: {article['news_url']}\n")
