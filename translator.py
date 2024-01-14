import openai
import os

def translate_text(text, target_language='ru'):
    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')

        response = openai.Completion.create(
            model="davinci-002",  # Используйте модель davinci-002
            prompt=f"Translate the following text to {target_language}: {text}",
            max_tokens=60  # Вы можете настроить это значение в зависимости от длины текста
        )
        translation = response.choices[0].text.strip()
        return translation
    except Exception as e:
        print(f"Error in text translation: {str(e)}")
        return text

if __name__ == "__main__":
    # Пример использования
    original_text = "Hello, world!"
    translated_text = translate_text(original_text)
    print(f"Translated text: {translated_text}")
