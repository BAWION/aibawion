import openai

def translate_text(api_key, text, target_language='en'):
    try:
        openai.api_key = api_key
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Translate the following text to {target_language}: {text}",
            max_tokens=50
        )
        translation = response.choices[0].text.strip()
        return translation
    except Exception as e:
        print(f"Ошибка при переводе текста: {str(e)}")
        return text

