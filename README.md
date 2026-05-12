# Ajeer Dashboard — Flask + MongoDB + Gemini AI

A full-stack workforce management platform with:

- 🔐 Login with country selection → auto currency detection
- 💱 Live currency converter (ExchangeRate-API)
- 🤖 AI chatbot powered by Gemini 2.5 Flash Lite
- 🧠 RAG Chatbot page (scaffolded, Qdrant ready)
- 🗄️ MongoDB for users, jobs, tasks, logs

## Project Structure

```
ajeer/
├── app.py               # Main Flask app
├── rag_engine.py        # Qdrant RAG engine (future dev)
├── init_db.py           # MongoDB seed script
├── requirements.txt
├── .env.example
└── templates/
    ├── login.html
    ├── register.html
    ├── dashboard.html
    └── chatbot.html
```

---

## Setup

### 1. Clone & install dependencies

```bash
cd ajeer
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

**.env keys:**
| Key | Value |
|-----|-------|
| `SECRET_KEY` | Any random string |
| `MONGO_URI` | `mongodb://localhost:27017/ajeer_db` |
| `GEMINI_API_KEY` | Get from https://aistudio.google.com |
| `EXCHANGE_API_KEY` | Get from https://www.exchangerate-api.com (free tier) |

### 3. Start MongoDB

```bash
# Local
mongod --dbpath /data/db

# Or Docker
docker run -d -p 27017:27017 mongo:latest
```

### 4. Initialize Database

```bash
python init_db.py
# Creates indexes + seeds admin user + sample data
# Admin: admin@ajeer.com / admin123
```

### 5. Run the app

```bash
python app.py
# Visit http://localhost:5000
```

---

## Features

### Login with Country

- User selects their country on login
- Currency is automatically detected (e.g., India → INR ₹)
- Currency saved to session + MongoDB

### Dashboard

- Stats: Jobs, Workers, Tasks, Revenue (in user's currency)
- **Currency Converter** with live ExchangeRate-API rates
- **Feature Cards**: Chatbot, Jobs, Analytics
- Quick AI chat widget

### Currency Converter

- Powered by `https://api.exchangerate-api.com` (Google-sourced rates)
- Live conversion between 19+ currencies
- Swap button to reverse conversion
- Quick rates ticker showing rates vs your local currency

### Chatbot Card → RAG Page

- Clicking "AI Chatbot" card redirects to `/chatbot`
- Currently uses Gemini 2.5 Flash Lite for Q&A
- RAG mode (Qdrant) scaffolded in `rag_engine.py`

### RAG Engine (Future)

```python
from rag_engine import get_rag_engine

engine = get_rag_engine()
engine.index_document("doc-001", "Your document text here")
answer = engine.rag_answer("What documents do I need to apply?")
```

---

## API Endpoints

| Endpoint                | Method   | Description        |
| ----------------------- | -------- | ------------------ |
| `/login`                | GET/POST | Login with country |
| `/register`             | GET/POST | Register new user  |
| `/dashboard`            | GET      | Main dashboard     |
| `/chatbot`              | GET      | RAG chatbot page   |
| `/api/currency/convert` | POST     | Convert currency   |
| `/api/currency/rates`   | GET      | Get live rates     |
| `/api/chat`             | POST     | Gemini AI chat     |
| `/logout`               | GET      | Log out            |

---

## Tech Stack

- **Backend**: Python Flask 3.0
- **Database**: MongoDB (via Flask-PyMongo)
- **Vector DB**: Qdrant (for RAG — future)
- **AI**: Google Gemini 2.5 Flash Lite
- **Currency**: ExchangeRate-API (free tier: 1500 req/month)
- **Frontend**: Pure HTML/CSS/JS (no framework)
