import openai
import os

def test_openai_connection():
    try:
        # Установите ваш API ключ здесь или убедитесь, что он установлен в переменных окружения
        openai.api_key = os.getenv('OPENAI_API_KEY')

        # Простой тестовый запрос
        response = openai.Completion.create(
            engine="text-davinci-003",  # Замените на актуальную модель
            prompt="Hello, world!",
            max_tokens=5
        )
        print(response.choices[0].text.strip())
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    test_openai_connection()

