from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.cache import cache
from datetime import date, datetime, time
from .services.ai_service import generate_quiz_questions

# Define the maximum number of quizzes that can be generated per day
MAX_QUIZZES_PER_DAY = 50

def home(request):
    """
    Renders the home page with a form to input the quiz topic.
    Handles the form submission to generate quiz questions.
    """
    if request.method == 'POST':
        topic = request.POST.get('topic')
        if topic:
            # Implement rate limiting
            today_str = date.today().isoformat()
            cache_key = f'quiz_generation_count_{today_str}'
            
            # Increment the counter for today. If it doesn't exist, set to 1.
            # The timeout for the cache entry should be the end of the day.
            # Calculate seconds remaining until the end of today.
            now = datetime.now()
            midnight = datetime.combine(now.date(), time.max)
            seconds_until_midnight = (midnight - now).total_seconds()

            current_count = cache.get(cache_key, 0)
            
            if current_count >= MAX_QUIZZES_PER_DAY:
                error_message = f"You have reached the daily limit of {MAX_QUIZZES_PER_DAY} quiz generations. Please try again tomorrow."
                return render(request, 'home.html', {'error_message': error_message})
            
            cache.set(cache_key, current_count + 1, timeout=seconds_until_midnight)

            # Generate quiz questions using AI service
            quiz_questions = generate_quiz_questions(topic)
            if quiz_questions:
                request.session['quiz_questions'] = quiz_questions
                request.session['quiz_topic'] = topic
                request.session['current_question_index'] = 0
                request.session['user_answers'] = []
                return redirect('quiz_app:quiz')
            else:
                # Handle case where no questions were generated
                error_message = "Failed to generate quiz questions. Please try a different topic."
                return render(request, 'home.html', {'error_message': error_message})
        else:
            error_message = "Please enter a quiz topic."
            return render(request, 'home.html', {'error_message': error_message})
    return render(request, 'home.html')

def quiz(request):
    quiz_questions = request.session.get('quiz_questions')
    current_question_index = request.session.get('current_question_index', 0)
    user_answers = request.session.get('user_answers', [])

    if not quiz_questions:
        return redirect('quiz_app:home')

    if request.method == 'POST':
        selected_option = request.POST.get('option')
        if selected_option:
            user_answers.append(selected_option)
            request.session['user_answers'] = user_answers
            request.session['current_question_index'] += 1
            current_question_index += 1

            if current_question_index < len(quiz_questions):
                return redirect('quiz_app:quiz') # Redirect to load next question
            else:
                return redirect('quiz_app:result') # Redirect to results if all questions answered
        else:
            # If no option is selected, re-render the current question with an error
            question = quiz_questions[current_question_index]
            context = {
                'question_number': current_question_index + 1,
                'question': question['question'],
                'options': question['options'],
                'error_message': "Please select an answer."
            }
            return render(request, 'quiz.html', context)

    if current_question_index < len(quiz_questions):
        question = quiz_questions[current_question_index]
        context = {
            'question_number': current_question_index + 1,
            'question': question['question'],
            'options': question['options']
        }
        return render(request, 'quiz.html', context)
    else:
        return redirect('quiz_app:result')

def result(request):
    quiz_questions = request.session.get('quiz_questions')
    user_answers = request.session.get('user_answers')
    quiz_topic = request.session.get('quiz_topic')

    if not quiz_questions or not user_answers:
        return redirect('quiz_app:home')

    score = 0
    correct_answers_count = 0
    total_questions = len(quiz_questions)

    for i, question in enumerate(quiz_questions):
        if i < len(user_answers):
            if user_answers[i] == question['answer']:
                score += 100 / total_questions # Assuming equal weight for each question
                correct_answers_count += 1
    
    score = round(score) # Round the score to a whole number

    context = {
        'quiz_topic': quiz_topic,
        'score': score,
        'correct_answers_count': correct_answers_count,
        'total_questions': total_questions
    }

    # Clear session data related to the quiz after results are displayed
    # del request.session['quiz_questions']
    # del request.session['quiz_topic']
    # del request.session['current_question_index']
    # del request.session['user_answers']
    # Keeping session data for now so user can potentially review if needed or "play again"

    return render(request, 'result.html', context)