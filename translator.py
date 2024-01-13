import openai
import os

def translate_text(text, target_language='ru'):
    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Новая модель, замените на актуальную, если доступна другая
            messages=[
                {"role": "system", "content": "You are a highly skilled translator."},
                {"role": "user", "content": f"Translate the following text to {target_language}: {text}"}
            ]
        )
        translation = response['choices'][0]['message']['content']
        return translation.strip()
    except Exception as e:
        print(f"Error in text translation: {str(e)}")
        return text
