import openai


def translate_text(text, target_language='en'):
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Translate the following text to {target_language}: {text}",
            max_tokens=50  # Укажите максимальное количество токенов для перевода
        )  # Закрывающая скобка добавлена здесь
        translation = response.choices[0].text.strip()
        return translation
    except Exception as e:
        print(f"Ошибка при переводе текста: {str(e)}")
        return text
