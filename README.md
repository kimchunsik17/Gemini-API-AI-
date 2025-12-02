# AI Quiz Master Web (GenQuiz Web)

## 1. Project Overview
**AI Quiz Master Web** is a dynamic quiz web application built with Django and Google's Gemini API. Users can input any topic they are interested in, and the AI will instantly generate a custom 5-question multiple-choice quiz. The application evaluates the user's answers and provides a score along with detailed explanations for each question.

This project is designed to demonstrate the integration of Generative AI with a robust web framework, featuring a clean UI and efficient session-based data management.

## 2. Key Features
*   **Custom Quiz Generation:** Generate quizzes on infinite topics using Gemini Pro.
*   **Interactive Quiz Interface:** User-friendly interface for taking quizzes.
*   **Instant Feedback:** Immediate scoring and correct answer explanations.
*   **Rate Limiting:** Built-in protection to limit quiz generation (default: 50 per day) to manage API quotas.
*   **Session Management:** Efficient handling of quiz states using Django sessions, minimizing database overhead.
*   **Responsive Design:** Accessible on various devices (Desktop, Tablet, Mobile).

## 3. Tech Stack
*   **Language:** Python 3.10+
*   **Framework:** Django 5.x
*   **AI Model:** Google Gemini Pro (`google-generativeai` library)
*   **Frontend:** Django Templates (HTML/CSS), JavaScript
*   **Deployment:** Docker, Gunicorn, Google Cloud Platform (Cloud Run/App Engine compatible)
*   **Environment:** `python-dotenv` for secure configuration

## 4. Prerequisites
Before running this project, ensure you have the following installed:
*   Python 3.10 or higher
*   Git
*   A Google Cloud Project with Vertex AI or Gemini API access (for the API Key)

## 5. Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and Activate Virtual Environment**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**
    Create a `.env` file in the root directory and add your Google API Key:
    ```env
    GOOGLE_API_KEY=your_google_gemini_api_key_here
    # Optional: Set DEBUG=False for production
    # DEBUG=True
    ```

5.  **Run Migrations**
    Initialize the database (mainly for session and cache tables).
    ```bash
    python manage.py migrate
    ```

6.  **Run Local Server**
    ```bash
    python manage.py runserver
    ```
    Access the application at `http://127.0.0.1:8000`.

## 6. Project Structure
```
AI Quiz Master/
├── genquiz_web/         # Project configuration settings
├── quiz_app/            # Main application logic
│   ├── services/        # AI service logic (Gemini integration)
│   ├── views.py         # View controllers
│   └── ...
├── templates/           # HTML Templates
├── static/              # Static files (CSS, JS, Images)
├── Dockerfile           # Docker configuration for deployment
├── manage.py            # Django management script
└── requirements.txt     # Python dependencies
```

## 7. Deployment (Docker)
This project is containerized using Docker, making it easy to deploy to platforms like Google Cloud Run.

1.  **Build the Docker Image**
    ```bash
    docker build -t genquiz-web .
    ```

2.  **Run the Container**
    ```bash
    docker run -p 8080:8080 --env-file .env genquiz-web
    ```
