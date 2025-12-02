# Project Name: AI Quiz Master Web (GenQuiz Web)

## 1. Project Goal
Django 프레임워크와 Gemini API를 활용하여 사용자가 입력한 주제에 맞는 퀴즈 웹사이트를 구축하고, Google Cloud Platform(GCP) 환경에 배포할 수 있는 구조로 개발한다.

## 2. Tech Stack
- **Language:** Python 3.10+
- **Framework:** Django 5.x
- **AI Model:** Google Gemini Pro (`google-generativeai`)
- **Frontend:** Django Templates (HTML/CSS), JavaScript (Simple interaction)
- **Deployment:** Google Cloud Platform (Cloud Run or App Engine)
- **Environment Management:** `python-dotenv` (For handling API Keys securely)

## 3. Functional Requirements

### A. Page Structure (URLs)
1. **Main Page (`/`)**:
   - 퀴즈 주제를 입력받는 폼(Form)이 중앙에 위치.
   - "퀴즈 생성하기" 버튼 포함.
2. **Quiz Page (`/quiz/`)**:
   - Gemini가 생성한 5개의 객관식 문제가 표시됨.
   - 사용자는 라디오 버튼으로 답을 선택.
   - "제출 및 채점" 버튼 포함.
3. **Result Page (`/result/`)**:
   - 사용자의 점수와 맞은 개수 표시 (예: 80점, 4/5).
   - "다시 하기" 버튼 (메인으로 이동).

### B. Backend Logic (Views)
- **Quiz Generator Service:**
  - Gemini API를 호출하여 JSON 데이터를 받아오는 별도의 유틸리티 함수 작성 (`services/ai_service.py`).
  - **Prompt Engineering:** "반드시 순수 JSON List 포맷으로 리턴할 것. Markdown backticks(\`\`\`) 제외." 조건 명시 필수.
  - API 호출 실패 시 예외 처리 및 사용자에게 "다시 시도해주세요" 메시지 전달.
- **Session Management:**
  - 퀴즈 데이터와 정답을 `request.session`에 임시 저장하여 페이지 간 데이터 유지 (DB 사용 최소화).

### C. GCP Deployment Preparation
- **Security:** API Key는 코드에 하드코딩하지 않고 `os.environ.get('GOOGLE_API_KEY')`로 호출.
- **Requirements:** 사용된 라이브러리들을 `requirements.txt`에 명시.
- **WSGI:** 프로덕션 배포를 위해 `gunicorn` 설정 준비.

## 4. Coding Conventions
- **Clean Code:** 뷰(View) 로직과 비즈니스 로직(AI 호출)을 분리할 것.
- **Styling:** CSS는 가독성 위주로 깔끔하게 작성 (Bootstrap CDN 활용 가능).
- **Comments:** 주요 함수 및 클래스에 한글 독스트링(Docstring) 작성.

## 5. Specific Prompt for AI Assistant
"이 명세서를 바탕으로 Django 프로젝트 구조를 잡아주고, 핵심이 되는 `views.py`, `urls.py`, `ai_service.py`, 그리고 템플릿 파일(`home.html`, `quiz.html`)의 코드를 작성해줘. 특히 Gemini가 준 텍스트에서 JSON만 추출하는 로직을 꼼꼼하게 짜줘."