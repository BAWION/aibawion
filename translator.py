import requests
import os

def translate_text_deepl(text, target_language='RU'):
    api_key = os.getenv('DEEPL_API_KEY')
    if not api_key:
        raise ValueError("DeepL API ключ не найден. Убедитесь, что он задан в переменных окружения.")

    # Измененный URL для бесплатной версии DeepL API
    url = "https://api-free.deepl.com/v2/translate"
    data = {
        'auth_key': api_key,
        'text': text,
        'target_lang': target_language
    }

    response = requests.post(url, data=data)
    if response.status_code != 200:
        raise Exception(f"Ошибка DeepL API: {response.status_code} {response.text}")

    translated_text = response.json().get('translations', [{}])[0].get('text', '')
    return translated_text

if __name__ == "__main__":
    original_text = "Hello, world!"
    translated_text = translate_text_deepl(original_text)
    print(f"Translated text: {translated_text}")
