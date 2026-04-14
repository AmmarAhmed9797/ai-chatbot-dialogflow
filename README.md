# 🤖 AI Chatbot — Google DialogFlow + Python + Django

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![DialogFlow](https://img.shields.io/badge/Dialogflow-FF9800?style=for-the-badge&logo=dialogflow&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)

> A full-stack AI-powered conversational chatbot built with Google DialogFlow API, Python, and Django — deployed as a production-ready web application.

---

## 📌 About This Project

A personal project showcasing AI integration skills. This chatbot uses **Google DialogFlow** for natural language understanding (NLU) and intent detection, with a **Django** backend serving the REST API and a clean web frontend for real-time conversation.

### Key Features
- 🧠 Natural Language Understanding via Google DialogFlow
- 💬 Real-time conversational interface
- 🔗 REST API backend built with Django & Django REST Framework
- 🌐 Full-stack web deployment
- 🔒 Session management & context handling
- 📊 Intent analytics and conversation logging

---

## 🏗️ Architecture

```
ai-chatbot-dialogflow/
├── backend/
│   ├── chatbot/
│   │   ├── views.py          # API endpoints
│   │   ├── dialogflow.py     # DialogFlow integration
│   │   ├── models.py         # Conversation models
│   │   └── urls.py
│   ├── config/
│   │   └── settings.py
│   └── manage.py
├── frontend/
│   ├── templates/
│   │   └── chat.html         # Chat UI
│   └── static/
│       ├── css/style.css
│       └── js/chat.js        # WebSocket client
├── dialogflow/
│   └── intents/              # DialogFlow agent export
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| NLU / AI Engine | Google DialogFlow API |
| Backend | Python, Django, Django REST Framework |
| Frontend | HTML5, CSS3, JavaScript |
| Database | SQLite / PostgreSQL |
| Deployment | Google Cloud / Heroku |
| Version Control | Git, GitHub |

---

## 🚀 Features & Intents

- **Greeting & Farewell** — Contextual conversation starters
- **FAQ Responses** — Pre-trained answers to common questions
- **Fallback Handling** — Graceful responses for unknown inputs
- **Context Management** — Multi-turn conversation flows
- **Entity Extraction** — Recognizes names, dates, and custom entities
- **Webhook Integration** — Dynamic responses from Django backend

---

## ⚙️ Setup & Installation

```bash
# Clone the repository
git clone https://github.com/AmmarAhmed9797/ai-chatbot-dialogflow.git
cd ai-chatbot-dialogflow

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DIALOGFLOW_PROJECT_ID=your-project-id
export GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Run the server
python manage.py migrate
python manage.py runserver
```

---

## 📊 Performance

| Metric | Result |
|---|---|
| Intent Recognition Accuracy | 92%+ |
| Average Response Time | < 500ms |
| Supported Languages | English |
| Concurrent Users | 50+ |

---

## 👨‍💻 Author

**Muhammad Ammar Ahmed** — Senior Test Automation Engineer & Full-Stack Developer
📧 m.ammarahmed97@gmail.com
🔗 [LinkedIn](https://linkedin.com/in/ammarahmed) | [GitHub](https://github.com/AmmarAhmed9797)
