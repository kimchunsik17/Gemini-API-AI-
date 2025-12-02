import os
import json
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv

load_dotenv()

def get_gemini_api_key():
    """Retrieves the Gemini API key from environment variables."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")
    return api_key

def configure_gemini():
    """Configures the Gemini API with the API key."""
    genai.configure(api_key=get_gemini_api_key())

def generate_quiz_questions(topic: str) -> list:
    """
    Generates quiz questions on a given topic using the Gemini API.

    Args:
        topic (str): The topic for which to generate quiz questions.

    Returns:
        list: A list of dictionaries, where each dictionary represents a quiz question.
              Returns an empty list if an error occurs or no valid JSON is found.
    """
    configure_gemini()
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = f"""
    You are a quiz generator. Generate 5 multiple-choice questions about "{topic}" in Korean.
    Each question should have a 'question', 'options' (a list of 4 strings), 'answer' (the 0-based index of the correct option), and an 'explanation' (a brief explanation of the correct answer).
    The response MUST be a pure JSON list format, without any Markdown backticks (```json).
    Example format:
    [
      {{
        "question": "대한민국의 수도는 어디입니까?",
        "options": ["부산", "서울", "인천", "대구"],
        "answer": 1,
        "explanation": "서울은 대한민국의 수도이자 최대 도시입니다."
      }},
      {{
        "question": "태양계에서 가장 큰 행성은 무엇입니까?",
        "options": ["지구", "화성", "목성", "금성"],
        "answer": 2,
        "explanation": "목성은 태양계에서 가장 큰 가스 행성입니다."
      }}
    ]
    """

    try:
        response = model.generate_content(
            prompt,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        # Extract JSON from the response text
        # The prompt explicitly asks for pure JSON, so we expect it directly.
        # However, it's good practice to handle potential malformed responses.
        quiz_json_str = response.text.strip()
        
        # Attempt to parse as JSON
        quiz_data = json.loads(quiz_json_str)
        
        return quiz_data
    except ValueError as e:
        print(f"API Key Error: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        print(f"Received text: {quiz_json_str}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

if __name__ == '__main__':
    # Example usage (for testing purposes)
    # Make sure to set GOOGLE_API_KEY in your environment or a .env file
    # For example, in a .env file: GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    
    # Create a dummy .env file for testing if it doesn't exist
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write('GOOGLE_API_KEY="YOUR_DUMMY_API_KEY_HERE"\n')
        print("Created a dummy .env file. Please replace 'YOUR_DUMMY_API_KEY_HERE' with your actual Gemini API key.")

    load_dotenv() # Load environment variables from .env

    print("Generating quiz questions about 'Python Programming'...")
    questions = generate_quiz_questions("Python Programming")
    if questions:
        for i, q in enumerate(questions):
            print(f"Q{i+1}: {q['question']}")
            for j, option in enumerate(q['options']):
                print(f"  {chr(65+j)}. {option}")
            print(f"  Answer: {q['answer']}\n")
    else:
        print("Failed to generate quiz questions.")
