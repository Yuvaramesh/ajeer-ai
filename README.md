# Ajeer Dashboard - RAG Chatbot with Multi-Agent System

A comprehensive Flask-based financial dashboard with intelligent RAG chatbot powered by LangGraph multi-agent system.

## Features

- **User Authentication**: Secure login/registration with password hashing
- **Country-Based Setup**: Automatic country detection and currency assignment
- **Currency Converter**: Real-time currency conversion using exchange rate APIs
- **RAG Chatbot**: Intelligent multi-agent chatbot with:
  - FAQ Agent: Semantic search through vector database
  - General Agent: LLM-powered responses for unknown queries
  - LangGraph orchestration for intelligent routing

## Architecture

### Backend
- **Framework**: Flask 3.x
- **Database**: MongoDB for user data and conversations
- **Vector Database**: Qdrant for FAQ embeddings
- **LLM**: Google Gemini 2.5-flash-lite
- **Multi-Agent System**: LangGraph

### Frontend
- **Template Engine**: Jinja2 with HTML
- **Styling**: Custom CSS with responsive design
- **JavaScript**: Vanilla JS for API interactions

## Prerequisites

- Python 3.8+
- MongoDB (running locally or connection string)
- Qdrant Vector Database (running locally or cloud instance)
- Google API Key (for Gemini LLM)

## Installation

### 1. Clone and Setup Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` with your configuration:

```bash
# Required
GOOGLE_API_KEY=your-google-api-key-here
MONGODB_URI=mongodb://localhost:27017/ajeer_dashboard
QDRANT_URL=http://localhost:6333
FLASK_SECRET_KEY=your-secret-key-here
```

### 3. Start Services

**MongoDB** (if running locally):
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or if installed locally
mongod
```

**Qdrant Vector Database** (if running locally):
```bash
# Using Docker
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant:latest

# Or using Python
python -m qdrant_client.server
```

### 4. Initialize Database

```bash
python scripts/init_db.py
```

This script will:
- Create MongoDB collections
- Initialize Qdrant vector store
- Seed 12 sample FAQs with embeddings

### 5. Run Flask Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
ajeer-dashboard/
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── models.py              # MongoDB models
├── requirements.txt       # Python dependencies
│
├── agents/
│   └── rag_agents.py     # LangGraph agents and RAG system
│
├── utils/
│   └── helpers.py         # Utility functions (auth, currency, validation)
│
├── templates/
│   ├── base.html          # Base template
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── dashboard.html     # Main dashboard
│   └── chatbot.html       # Chatbot interface
│
├── static/
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   └── js/
│       └── main.js        # Main JavaScript
│
└── scripts/
    └── init_db.py         # Database initialization
```

## Usage

### User Registration & Login

1. Navigate to the application
2. Click "Register" to create a new account
3. Your country will be detected from your IP address
4. Your preferred currency will be automatically set
5. Login with your credentials

### Currency Converter

1. Go to Dashboard
2. Enter amount in the Currency Converter card
3. Select source and target currencies
4. Click "Convert" to see real-time exchange rates

### Chatbot

1. Click "Open Chatbot" from dashboard or use the navigation menu
2. Ask questions about Ajeer or general queries
3. The chatbot will:
   - First search FAQs using semantic search (FAQ Agent)
   - If no match found, generate response using LLM (General Agent)

## API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - User login
- `GET /logout` - User logout

### Dashboard
- `GET /dashboard` - Main dashboard (requires login)
- `GET /` - Redirect to dashboard

### Currency
- `POST /api/convert-currency` - Convert between currencies
- `GET /api/exchange-rate` - Get exchange rate

### Chatbot
- `POST /api/chat` - Process user query
- `GET /chatbot` - Chatbot interface
- `GET /api/chatbot-page` - Redirect to chatbot

### User Profile
- `GET /api/user-profile` - Get user profile
- `PUT /api/user-profile` - Update user profile

## RAG Agent System

### Router Node
- Routes incoming queries to appropriate agents

### FAQ Agent
1. Generates embedding for user query using Gemini API
2. Searches Qdrant vector database for similar FAQs
3. Returns matching FAQ with similarity score

### General Agent
1. Uses conversation history as context
2. Generates response using Gemini 2.5-flash-lite LLM
3. Provides helpful responses for unknown queries

### Response Formatter
- Formats final response with metadata
- Adds confidence scores for FAQ matches

## Database Schema

### MongoDB Collections

**users**
```json
{
  "_id": ObjectId,
  "username": "string",
  "email": "string",
  "password_hash": "string",
  "country": "string",
  "preferred_currency": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**conversations**
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "agent_type": "faq_search|general_response",
  "query": "string",
  "response": "string",
  "created_at": "datetime"
}
```

**faqs**
```json
{
  "_id": ObjectId,
  "qdrant_id": "integer",
  "question": "string",
  "answer": "string",
  "category": "string",
  "created_at": "datetime"
}
```

### Qdrant Vector Store

**faqs_collection**
- Vector size: 768 (from Gemini embeddings)
- Distance metric: Cosine similarity
- Payload: question, answer, type

## Supported Countries & Currencies

The system automatically detects country from IP and assigns appropriate currency:
- US → USD
- UK → GBP
- EU countries → EUR
- India → INR
- Middle East → AED/SAR
- Japan → JPY
- And 20+ more countries...

## Security Features

- Password hashing with PBKDF2-HMAC-SHA256
- HTTP-only session cookies
- CSRF protection (Flask-Login)
- SQL injection prevention (MongoDB parameterization)
- Input validation and sanitization
- Secure password requirements

## Performance Optimization

- Vector similarity search for FAQ matching (O(log n) with Qdrant indexing)
- Session-based caching for user preferences
- Lazy loading of conversation history (limited to 50 most recent)
- Optimized database indexes on frequently queried fields

## Troubleshooting

### MongoDB Connection Error
```
Check if MongoDB is running:
mongosh
```

### Qdrant Connection Error
```
Check if Qdrant is running on http://localhost:6333
```

### Google API Key Error
```
Ensure GOOGLE_API_KEY is set in .env
Get API key from: https://makersuite.google.com/app/apikey
```

### FAQ Search Not Working
```
Run: python scripts/init_db.py
to reinitialize the FAQ embeddings
```

## Future Enhancements

- [ ] User profile customization
- [ ] Transaction history export (CSV/PDF)
- [ ] Real-time price alerts
- [ ] Multiple language support
- [ ] Advanced analytics dashboard
- [ ] Email notifications
- [ ] Two-factor authentication
- [ ] API for third-party integrations

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or feature requests, please create an issue in the repository.

## Changelog

### Version 1.0.0 (Initial Release)
- User authentication system
- Country-based currency assignment
- Real-time currency converter
- RAG chatbot with multi-agent system
- FAQ knowledge base with vector embeddings
- Responsive dashboard interface

---

**Built with Flask, MongoDB, Qdrant, and Google Gemini**
