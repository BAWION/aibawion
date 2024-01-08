import requests
from bs4 import BeautifulSoup

def parse_news(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    for article in soup.find_all('a', class_='link-block-8'):
        # Найти дату новости
        date_div = article.find_previous_sibling('div', class_='text-block-30')
        date_text = date_div.text.strip() if date_div else 'Дата отсутствует'

        # Найти заголовок новости
        title = article.find('div', class_='text-block-27')
        title_text = title.text.strip() if title else 'Нет заголовка'

        # Найти домен источника новости
        source = article.find('div', class_='text-block-28')
        source_text = source.text.strip() if source else 'Нет источника'

        # Найти URL изображения
        image = article.find('img')
        image_url = image['src'] if image and 'src' in image.attrs else 'URL изображения отсутствует'

        # Собрать URL новости
        news_url = article['href'] if 'href' in article.attrs else 'URL новости отсутствует'

        articles.append({
            'date': date_text,
            'title': title_text,
            'source': source_text,
            'image_url': image_url,
            'news_url': news_url
        })

    return articles

# Пример использования функции
if __name__ == '__main__':
    url = 'https://www.futuretools.io/news'  # URL сайта для парсинга
    news_articles = parse_news(url)
    for article in news_articles:
        print(f"Дата: {article['date']}")
        print(f"Заголовок: {article['title']}")
        print(f"Источник: {article['source']}")
        print(f"URL изображения: {article['image_url']}")
        print(f"URL новости: {article['news_url']}\n")
