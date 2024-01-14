import openai
import os

def test_openai_connection():
    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')

        # Используйте модель gpt-3.5-turbo-0613 с конечной точкой для текстовой генерации
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-0613",  # Используйте модель gpt-3.5-turbo-0613
            prompt="Hello, world!",
            max_tokens=5
        )
        print(response.choices[0].text.strip())
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    test_openai_connection()

