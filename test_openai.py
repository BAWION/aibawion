import openai
import os

def test_openai_connection():
    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')

        # Используйте модель gpt-3.5-turbo-0613 с конечной точкой для чата
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",  # Используйте модель gpt-3.5-turbo-0613
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, world!"}
            ]
        )
        print(response.choices[0].message['content'].strip())
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    test_openai_connection()
