import openai

# Установите ваш API ключ от OpenAI
openai.api_key = 'ВАШ_API_КЛЮЧ'

def test_translation():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a highly skilled translator."},
                {"role": "user", "content": "Translate 'Hello, world!' to Russian."}
            ]
        )
        translation = response['choices'][0]['message']['content']
        return translation.strip()
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    result = test_translation()
    print("Translation result:", result)
