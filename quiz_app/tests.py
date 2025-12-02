import os
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from quiz_app.services.ai_service import generate_quiz_questions, configure_gemini, get_gemini_api_key

# Mock data for Gemini API response
MOCK_QUIZ_QUESTIONS = [
    {
        "question": "What is the capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Rome"],
        "answer": 2 # Paris is at index 2
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Venus"],
        "answer": 1 # Mars is at index 1
    }
]

class AIServiceTest(TestCase):

    @patch('quiz_app.services.ai_service.genai')
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_api_key'})
    def test_generate_quiz_questions_success(self, mock_genai):
        """
        Tests successful quiz question generation and JSON parsing.
        """
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_QUIZ_QUESTIONS)
        mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response

        questions = generate_quiz_questions("Test Topic")
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0]['question'], "What is the capital of France?")
        self.assertEqual(questions[1]['answer'], 1)

    @patch('quiz_app.services.ai_service.genai')
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_api_key'})
    def test_generate_quiz_questions_json_error(self, mock_genai):
        """
        Tests error handling when Gemini returns malformed JSON.
        """
        mock_response = MagicMock()
        mock_response.text = "This is not valid JSON"
        mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response

        questions = generate_quiz_questions("Test Topic")
        self.assertEqual(questions, [])

    @patch.dict(os.environ, {}, clear=True) # Ensure GOOGLE_API_KEY is not set
    def test_get_gemini_api_key_missing(self):
        """
        Tests that ValueError is raised when GOOGLE_API_KEY is missing.
        """
        with self.assertRaises(ValueError):
            get_gemini_api_key()

class QuizAppViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('quiz_app:home')
        self.quiz_url = reverse('quiz_app:quiz')
        self.result_url = reverse('quiz_app:result')

    def test_home_page_get(self):
        """
        Tests that the home page loads correctly.
        """
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, "AI Quiz Master")

    @patch('quiz_app.views.generate_quiz_questions', return_value=MOCK_QUIZ_QUESTIONS)
    def test_home_page_post_success(self, mock_generate_quiz_questions):
        """
        Tests successful quiz generation and redirection to quiz page.
        """
        response = self.client.post(self.home_url, {'topic': 'Test Topic'})
        self.assertRedirects(response, self.quiz_url)
        self.assertIn('quiz_questions', self.client.session)
        self.assertEqual(len(self.client.session['quiz_questions']), 2)
        self.assertEqual(self.client.session['quiz_topic'], 'Test Topic')
        self.assertEqual(self.client.session['current_question_index'], 0)
        self.assertEqual(self.client.session['user_answers'], [])


    @patch('quiz_app.views.generate_quiz_questions', return_value=[])
    def test_home_page_post_no_questions(self, mock_generate_quiz_questions):
        """
        Tests handling of no questions generated scenario.
        """
        response = self.client.post(self.home_url, {'topic': 'Empty Topic'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, "퀴즈 생성에 실패했습니다. 다른 주제로 시도해주세요.")

    def test_home_page_post_no_topic(self):
        """
        Tests handling of empty topic submission.
        """
        response = self.client.post(self.home_url, {'topic': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, "퀴즈 주제를 입력해주세요.")

    def test_quiz_page_redirect_if_no_quiz_data(self):
        """
        Tests redirection to home page if no quiz data in session.
        """
        response = self.client.get(self.quiz_url)
        self.assertRedirects(response, self.home_url)

    def test_quiz_page_get_first_question(self):
        """
        Tests that the first quiz question is displayed correctly.
        """
        session = self.client.session
        session['quiz_questions'] = MOCK_QUIZ_QUESTIONS
        session['quiz_topic'] = 'Test Topic'
        session['current_question_index'] = 0
        session['user_answers'] = []
        session.save()

        response = self.client.get(self.quiz_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz.html')
        self.assertContains(response, "What is the capital of France?")
        self.assertContains(response, "Paris")

    @patch('quiz_app.views.generate_quiz_questions', return_value=MOCK_QUIZ_QUESTIONS)
    def test_quiz_page_post_answer_and_next_question(self, mock_generate_quiz_questions):
        """
        Tests submitting an answer and moving to the next question.
        """
        # Initialize session through a post to the home view
        self.client.post(self.home_url, {'topic': 'Test Topic'})

        response = self.client.post(self.quiz_url, {'option': '2'}, follow=True) # Select Paris (index 2)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz.html')
        self.assertContains(response, "Which planet is known as the Red Planet?") 

        self.assertEqual(self.client.session['current_question_index'], 1)
        self.assertEqual(self.client.session['user_answers'], ['2'])

    @patch('quiz_app.views.generate_quiz_questions', return_value=MOCK_QUIZ_QUESTIONS)
    def test_quiz_page_post_all_answers_and_redirect_to_results(self, mock_generate_quiz_questions):
        """
        Tests submitting all answers and redirection to the result page.
        """
        # Initialize session through a post to the home view
        self.client.post(self.home_url, {'topic': 'Test Topic'})

        # Submit first answer
        self.client.post(self.quiz_url, {'option': '2'}, follow=True) # Paris
        # Submit second answer
        response = self.client.post(self.quiz_url, {'option': '1'}, follow=True) # Mars
        
        self.assertEqual(response.status_code, 200) # The final response should be 200 for the result page
        self.assertTemplateUsed(response, 'result.html')
        self.assertContains(response, "퀴즈 결과") # Assert something from the result page

        self.assertEqual(self.client.session['current_question_index'], 2)
        self.assertEqual(self.client.session['user_answers'], ['2', '1'])

    def test_quiz_page_post_no_option_selected(self):
        """
        Tests that an error message is displayed if no option is selected.
        """
        session = self.client.session
        session['quiz_questions'] = MOCK_QUIZ_QUESTIONS
        session['quiz_topic'] = 'Test Topic'
        session['current_question_index'] = 0
        session['user_answers'] = []
        session.save()

        response = self.client.post(self.quiz_url, {}) # No option selected
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz.html')
        self.assertContains(response, "답을 선택해주세요.")
        self.assertEqual(self.client.session['current_question_index'], 0) # Should not advance

    def test_result_page_redirect_if_no_quiz_data(self):
        """
        Tests redirection to home page if no quiz data in session.
        """
        response = self.client.get(self.result_url)
        self.assertRedirects(response, self.home_url)

    def test_result_page_displays_correct_score(self):
        """
        Tests that the result page calculates and displays the correct score.
        """
        session = self.client.session
        session['quiz_questions'] = MOCK_QUIZ_QUESTIONS
        session['quiz_topic'] = 'Test Topic'
        session['user_answers'] = ['2', '1'] # Both correct indices
        session.save()

        response = self.client.get(self.result_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'result.html')
        # Note: The assertions below might depend on how your template renders the score.
        # If you changed the template text, update these assertions.
        self.assertContains(response, "100") 
        self.assertContains(response, "2") # Correct count
        self.assertContains(response, "Test Topic")

    def test_result_page_displays_partial_score(self):
        """
        Tests that the result page calculates and displays a partial score.
        """
        session = self.client.session
        session['quiz_questions'] = MOCK_QUIZ_QUESTIONS
        session['quiz_topic'] = 'Test Topic'
        session['user_answers'] = ['3', '1'] # One wrong (3 is Rome), one correct
        session.save()

        response = self.client.get(self.result_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'result.html')
        self.assertContains(response, "50")
        self.assertContains(response, "1") # Correct count

    def test_result_page_play_again_button(self):
        """
        Tests that the 'Play Again' button links to the home page.
        """
        session = self.client.session
        session['quiz_questions'] = MOCK_QUIZ_QUESTIONS
        session['quiz_topic'] = 'Test Topic'
        session['user_answers'] = ['2', '1']
        session.save()

        response = self.client.get(self.result_url)
        self.assertContains(response, f'href="{self.home_url}"')