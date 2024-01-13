import openai
import os

def translate_text(text, target_language='ru'):
    try:
        # Убедитесь, что ключ API OpenAI установлен в переменных окружения
        openai.api_key = os.getenv('OPENAI_API_KEY')

        # Использование метода завершения текста для перевода
        response = openai.Completion.create(
            engine="text-davinci-003",  # Использование последней версии модели
            prompt=f"Translate the following text to {target_language}: {text}",
            max_tokens=50  # Указание максимального числа токенов для перевода
        )
        translation = response.choices[0].text.strip()
        return translation
    except Exception as e:
        print(f"Error in text translation: {str(e)}")
        return text


