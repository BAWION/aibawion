import openai
import os
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def translate_text(text, target_language='ru'):
    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')

        prompt = f"Переведите этот новостной заголовок на {target_language} язык: {text}"

        response = openai.Completion.create(
            model="davinci-002",
            prompt=prompt,
            max_tokens=60
        )
        translation = response.choices[0].text.strip()

        # Логирование ответа от API
        logger.info(f"API request prompt: {prompt}")
        logger.info(f"API response: {translation}")

        return translation
    except Exception as e:
        logger.error(f"Error in text translation: {str(e)}")
        return text

if __name__ == "__main__":
    original_text = "Hello, world!"
    translated_text = translate_text(original_text)
    print(f"Translated text: {translated_text}")

