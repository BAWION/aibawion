import openai
import os

def translate_text(text, target_language='en'):
    try:
        # Убедитесь, что API ключ для OpenAI установлен в переменных окружения
        openai.api_key = os.getenv('OPENAI_API_KEY')

        # Используйте новый интерфейс для создания запроса
        response = openai.ChatCompletion.create(
            model="text-davinci-002",
            messages=[
                {"role": "system", "content": "Вы являетесь моделью перевода."},
                {"role": "user", "content": f"Переведите следующий текст на {target_language}: {text}"}
            ]
        )

        # Получаем перевод
        translation = response['choices'][0]['message']['content']
        return translation
    except Exception as e:
        print(f"Ошибка при переводе текста: {str(e)}")
        return text
