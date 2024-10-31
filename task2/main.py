import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure, ConfigurationError

BASE_URL = "http://quotes.toscrape.com/"

def parse_data():
    """
    Витягує цитати та інформацію про авторів з веб-сайту, 
    зберігає їх у JSON файлах.

    Виконує запит до базового URL, парсить HTML, 
    отримує цитати, авторів та їх атрибути, 
    а потім зберігає дані у файли 'quotes.json' та 'authors.json'.
    """
    response = requests.get(BASE_URL)

    if response.status_code == 200:

        quotes = []
        authors = []

        soup = BeautifulSoup(response.text, 'lxml')

        quotes_data = soup.select("div.quote")

        for quote_data in quotes_data:
            quote = quote_data.find("span", class_="text").text

            quote_author = quote_data.find("small", class_="author").text

            tags = quote_data.select("div.tags a")
            tags_for_quote = [tag.text for tag in tags]

            quotes.append(
                {
                    "quote": quote,
                    "author": quote_author,
                    "tags": tags_for_quote
                }
            )

            author_link = quote_data.select_one('span a')["href"]
            author_url = BASE_URL[:-1] + author_link
            author_response = requests.get(author_url)

            if author_response.status_code == 200:
                author_soup = BeautifulSoup(author_response.text, 'lxml')

                fullname = author_soup.find("h3", class_="author-title").text

                born_date = author_soup.find("span", class_="author-born-date").text
                born_date = datetime.strptime(born_date, "%B %d, %Y").isoformat()

                born_location = author_soup.find("span", class_="author-born-location").text
                if born_location.startswith("in "):
                    born_location = born_location[3:]

                description = author_soup.find("div", class_="author-description").text.strip()

                authors.append(
                    {
                        "fullname": fullname,
                        "born_date": born_date,
                        "born_location": born_location,
                        "description": description
                    }
                )

        with open("quotes.json", "w", encoding="utf-8") as f:
            json.dump(quotes, f, ensure_ascii=False, indent=4)

        with open("authors.json", "w", encoding="utf-8") as f:
            json.dump(authors, f, ensure_ascii=False, indent=4)

def load_json(file_path):
    """
    Завантажує дані з JSON файлу.

    Параметри:
    file_path (str): Шлях до файлу JSON, з якого потрібно завантажити дані.

    Повертає:
    dict або list: Дані, завантажені з файлу.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_mongo_client():
    """
    Підключається до MongoDB та повертає об'єкт клієнта.

    Повертає:
    MongoClient: Об'єкт клієнта MongoDB.

    Винятки:
    ConfigurationError: Якщо виникає помилка конфігурації.
    ServerSelectionTimeoutError: Якщо не вдається підключитися до сервера.
    """
    try:
        return MongoClient(
            "mongodb://localhost:27017/",
            server_api=ServerApi('1')
        )
    except ConfigurationError as e:
        raise ConfigurationError("Помилка конфігурації.") from e
    except ServerSelectionTimeoutError as e:
        raise ServerSelectionTimeoutError("Помилка підключення до сервера.") from e

def insert_data():
    """
    Вставляє дані авторів та цитат з JSON файлів у базу даних MongoDB, 
    але перед цим видаляє колекції, якщо вони вже існують.

    Використовує функцію `load_json` для завантаження даних з 
    'authors.json' та 'quotes.json', а потім вставляє їх у 
    відповідні колекції в базі даних.
    """
    client = get_mongo_client()
    db = client.task2

    db.authors.drop()
    db.quotes.drop()

    authors = load_json('authors.json')
    quotes = load_json('quotes.json')

    db.authors.insert_many(authors)
    db.quotes.insert_many(quotes)


if __name__ == "__main__":
    parse_data()
    insert_data()
