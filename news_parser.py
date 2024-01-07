
import requests
from bs4 import BeautifulSoup

def parse_news(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    for article in soup.find_all('article'):
        title = article.find('h2').text.strip()
        summary = article.find('p').text.strip()
        image_url = article.find('img')['src']

        articles.append({'title': title, 'summary': summary, 'image_url': image_url})

    return articles
