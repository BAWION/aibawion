import openai
import os

def test_translation():
    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="Translate 'Hello, world!' to Russian.",
            max_tokens=60
        )
        translation = response.choices[0].text.strip()
        return translation
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    result = test_translation()
    print("Translation result:", result)
