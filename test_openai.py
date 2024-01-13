import openai
import os

def test_translation():
    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')

        response = openai.Completion.create(
            model="gpt-3.5-turbo",  # Обновленная модель
            prompt="Translate 'Hello, world!' to Russian.",
            max_tokens=60,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        translation = response.choices[0].text.strip()
        return translation
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    result = test_translation()
    print("Translation result:", result)
