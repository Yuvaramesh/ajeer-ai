# Ajeer Dashboard - Architecture Documentation

Comprehensive overview of the Ajeer Dashboard system architecture, components, and data flow.

## System Overview

Ajeer Dashboard is a Flask-based web application that provides intelligent currency conversion and RAG-powered chatbot assistance using LangGraph multi-agent orchestration.

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (HTML/CSS/JS)                   │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐         │
│  │   Login      │  │  Dashboard  │  │  Chatbot UI  │         │
│  └──────────────┘  └─────────────┘  └──────────────┘         │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/JSON
┌──────────────────────────▼──────────────────────────────────┐
│                    Flask Web Server                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Route Handlers (app.py)                   │ │
│  │  /register, /login, /dashboard, /chatbot, /api/*      │ │
│  └────────────────────────────────────────────────────────┘ │
└──────┬──────────────┬──────────────┬────────────────────────┘
       │              │              │
   ┌───▼───┐      ┌───▼───┐      ┌──▼────┐
   │   DB  │      │  RAG  │      │Helpers│
   │Models │      │Agents │      │Utils  │
   └───┬───┘      └───┬───┘      └──┬────┘
       │              │              │
   ┌───▼──────────────▼──────────────▼────┐
   │    Database Layer & External APIs    │
   │ ┌──────────────┐  ┌──────────────┐  │
   │ │   MongoDB    │  │   Qdrant     │  │
   │ │              │  │              │  │
   │ │ • Users      │  │ • FAQ        │  │
   │ │ • Chats      │  │   Embeddings │  │
   │ │ • Sessions   │  │              │  │
   │ └──────────────┘  └──────────────┘  │
   │                                      │
   │ ┌──────────────┐  ┌──────────────┐  │
   │ │ Google API   │  │ Exchange     │  │
   │ │              │  │ Rate API     │  │
   │ │ • Gemini LLM │  │              │  │
   │ │ • Embeddings │  │ • Currency   │  │
   │ └──────────────┘  └──────────────┘  │
   └────────────────────────────────────┘
```

## Component Architecture

### 1. Flask Application Layer

**File: `app.py`**

Main entry point for the Flask application with route handlers organized into sections:

#### Authentication Routes
- `POST /register` - User registration with validation
- `POST /login` - User login with session management
- `GET /logout` - Session cleanup

#### Dashboard Routes
- `GET /dashboard` - Main dashboard (login required)
- `GET /` - Redirect to dashboard

#### Currency Routes
- `POST /api/convert-currency` - Real-time currency conversion
- `GET /api/exchange-rate` - Get exchange rates

#### Chatbot Routes
- `POST /api/chat` - Process user queries through RAG system
- `GET /chatbot` - Chatbot interface page
- `GET /api/chatbot-page` - Chatbot redirect

#### User Profile Routes
- `GET /api/user-profile` - Retrieve user information
- `PUT /api/user-profile` - Update user preferences

### 2. Database Layer

#### MongoDB Models (`models.py`)

**Database Class**
- Connection management
- Collection initialization
- Index creation

**UserModel**
- `create_user()` - Create new user with hashed password
- `find_by_email()` - Email-based lookup
- `find_by_username()` - Username-based lookup
- `find_by_id()` - ObjectId-based lookup
- `update_user()` - Update user data (currency preferences)

**ConversationModel**
- `create_conversation()` - Store chat interactions
- `get_user_conversations()` - Retrieve chat history (limited to 50 most recent)
- `get_conversation()` - Get specific conversation

**FAQModel**
- `create_faq_record()` - Store FAQ metadata
- `get_all_faqs()` - Retrieve all FAQ records
- `get_faq_by_qdrant_id()` - Look up FAQ by vector DB ID

#### MongoDB Collections Schema

```javascript
// users collection
{
  _id: ObjectId,
  username: String (unique, 3-20 chars),
  email: String (unique),
  password_hash: String (PBKDF2-HMAC-SHA256),
  country: String (2-letter country code),
  preferred_currency: String (3-letter currency code),
  created_at: DateTime,
  updated_at: DateTime
}

// conversations collection
{
  _id: ObjectId,
  user_id: ObjectId (reference to users),
  agent_type: String ('faq_search' | 'general_response'),
  query: String,
  response: String,
  created_at: DateTime
}

// faqs collection
{
  _id: ObjectId,
  qdrant_id: Integer (reference to Qdrant vector ID),
  question: String,
  answer: String,
  category: String,
  created_at: DateTime,
  updated_at: DateTime
}
```

### 3. RAG Agent System

**File: `agents/rag_agents.py`**

Multi-agent system using LangGraph for intelligent query routing and response generation.

#### VectorDBManager
Handles all Qdrant operations:
- `init_collection()` - Create/verify FAQ collection
- `add_faq()` - Insert FAQ with embeddings
- `search_similar_faqs()` - Vector similarity search

#### RAGAgentSystem

**Graph Structure:**
```
router -> faq_agent -> [decision] -> general_agent -> response_formatter -> END
```

**Nodes:**

1. **Router Node**
   - Receives user query
   - Prepares state for processing
   - Routes to FAQ Agent

2. **FAQ Agent**
   - Generates query embedding using Gemini API
   - Searches Qdrant for similar FAQs (cosine similarity)
   - Filters results by threshold (0.7)
   - Returns top 3 matching FAQs

3. **Response Formatter**
   - Checks if FAQ results exist
   - Formats FAQ response with confidence score
   - Returns final response

4. **General Agent** (fallback)
   - Uses conversation history as context
   - Calls Gemini 2.5-flash-lite LLM
   - Generates contextual response
   - Handles unknown questions

#### Agent Flow Logic

```
if faq_results.length > 0:
  return formatted_faq_response
else:
  return llm_generated_response
```

### 4. Utility Functions

**File: `utils/helpers.py`**

#### AuthHelper
```python
- hash_password(password)      # PBKDF2-HMAC-SHA256
- verify_password(pwd, hash)   # Constant-time comparison
- login_required(f)             # Route decorator
```

#### CountryHelper
```python
- get_country_from_ip(ip)       # ipapi.co API
- get_currency_for_country(cc)  # Country->Currency mapping
```

**Supported Countries:**
- 40+ countries with automatic currency assignment
- Fallback to USD if country not recognized
- Hardcoded mapping for reliability

#### CurrencyConverter
```python
- convert_currency(amount, from, to)  # Exchange rate API
- get_exchange_rate(from, to)         # Rate lookup
```

**API Used:** exchangerate-api.com (free tier)
- Real-time rates (updated daily)
- 1500 requests/month free
- Fallback to 1:1 rate on failure

#### ValidationHelper
```python
- validate_email(email)         # RFC pattern matching
- validate_password(pwd)        # 8+ chars, uppercase, digit
- validate_username(username)   # 3-20 chars, alphanumeric+_-
```

### 5. Configuration

**File: `config.py`**

Three configuration classes:
- `DevelopmentConfig` - Debug mode enabled
- `ProductionConfig` - Production settings
- `TestingConfig` - Test database

Key settings:
```python
MONGODB_URI = MongoDB connection string
QDRANT_URL = Qdrant server URL
GOOGLE_API_KEY = Gemini API key
SIMILARITY_THRESHOLD = 0.7 (FAQ matching)
LLM_MODEL = 'gemini-2.5-flash-lite'
```

## Data Flow Diagrams

### 1. User Registration Flow

```
User Input
   ↓
Validation (email, password, username)
   ↓
Check duplicates (MongoDB)
   ↓
Hash password (PBKDF2)
   ↓
Detect country (IP geolocation)
   ↓
Assign currency (country mapping)
   ↓
Create user (MongoDB)
   ↓
Success response
```

### 2. Currency Conversion Flow

```
User Input (amount, from, to)
   ↓
Validation
   ↓
Call Exchange Rate API
   ↓
Calculate: amount * rate
   ↓
Return result with metadata
```

### 3. Chatbot Query Flow

```
User Query (authenticated)
   ↓
Get conversation history (MongoDB, limit 50)
   ↓
Generate embedding (Gemini API)
   ↓
Vector search (Qdrant)
   ↓
Similarity threshold check (>= 0.7)
   ↓
Decision:
  ├─ FAQ found → Use FAQ Agent
  │  └─ Return FAQ answer with score
  │
  └─ No match → Use General Agent
     ├─ Build prompt with history
     ├─ Call Gemini LLM
     └─ Return generated response
   ↓
Store in MongoDB conversations
   ↓
Return to user
```

## Security Architecture

### Authentication
- **Session Management:** Flask-Login with HTTP-only cookies
- **Password Security:** PBKDF2-HMAC-SHA256 with 100k iterations
- **Input Validation:** Regex patterns for email/username/password

### Database Security
- **Parameterized Queries:** PyMongo automatic escaping
- **MongoDB Indexes:** Unique constraints on email/username
- **Session Isolation:** Per-user data filtering

### API Security
- **Login Required Decorators:** Protect sensitive endpoints
- **Session Validation:** Check user_id in session
- **Error Handling:** Generic error messages (no sensitive data leaks)

## Performance Optimization

### Database Optimization
- **MongoDB Indexes:**
  - Unique indexes on email and username (fast login)
  - Indexes on user_id and created_at (conversation queries)
  
- **Query Patterns:**
  - Conversations limited to 50 most recent (memory efficient)
  - FAQs loaded once at initialization

### Vector Search Optimization
- **Qdrant Indexing:** Automatic HNSW indexing for 768-dim vectors
- **Similarity Threshold:** 0.7 to balance precision/recall
- **Top-K Results:** Limited to 3 for response latency

### Caching
- **Session Caching:** User preferences cached in session
- **Static Files:** CSS/JS served with browser caching headers

## Scalability Considerations

### Current Limits
- Single Flask instance (development)
- Single MongoDB instance
- Single Qdrant instance
- In-memory session storage

### Scaling Strategy

**Horizontal Scaling:**
1. Load balancer in front of Flask instances
2. MongoDB replica set with sharding
3. Qdrant cluster with replication
4. Redis for distributed session store

**Vertical Scaling:**
1. Increase MongoDB memory for indexes
2. Increase Qdrant resources for vector operations
3. Optimize Gemini API calls with caching

## Technology Stack

### Backend
- **Framework:** Flask 3.0.0
- **ORM/Driver:** PyMongo 4.6.0 (no ORM)
- **Vector DB:** Qdrant 1.7.1
- **LLM Orchestration:** LangGraph 0.0.63
- **LLM Provider:** Google Gemini API
- **Authentication:** Built-in (Flask-Login)

### Frontend
- **Template Engine:** Jinja2
- **Styling:** Custom CSS (responsive)
- **Scripting:** Vanilla JavaScript (no framework)

### Infrastructure
- **Database:** MongoDB (NoSQL document store)
- **Vector Store:** Qdrant (vector similarity search)
- **APIs:** Google Gemini, exchangerate-api

## Deployment Architecture

```
┌─────────────────────────────────────┐
│     Load Balancer (Nginx/HAProxy)   │
└─────────────────────────────────────┘
            ↓ ↓ ↓
┌─────────┬─────────┬─────────┐
│ Flask   │ Flask   │ Flask   │
│ App 1   │ App 2   │ App N   │
└────┬────┴────┬────┴────┬────┘
     │         │         │
     └─────────┼─────────┘
               ↓
     ┌─────────────────────┐
     │    MongoDB          │
     │  (Replica Set)      │
     └─────────────────────┘
               ↓
     ┌─────────────────────┐
     │  Qdrant Cluster     │
     └─────────────────────┘
               ↓
     ┌─────────────────────┐
     │  Google API Gateway │
     └─────────────────────┘
```

## File Structure

```
ajeer-dashboard/
├── app.py                         # Flask application
├── config.py                      # Configuration classes
├── models.py                      # MongoDB models
├── requirements.txt               # Python dependencies
├── docker-compose.yml             # Docker services
├── .env.example                   # Environment template
│
├── agents/
│   ├── __init__.py
│   └── rag_agents.py             # LangGraph agents
│
├── utils/
│   ├── __init__.py
│   └── helpers.py                # Helper functions
│
├── templates/
│   ├── base.html                 # Base template
│   ├── login.html                # Login page
│   ├── register.html             # Registration page
│   ├── dashboard.html            # Main dashboard
│   └── chatbot.html              # Chatbot interface
│
├── static/
│   ├── css/
│   │   └── style.css             # Stylesheet
│   └── js/
│       └── main.js               # JavaScript
│
├── scripts/
│   └── init_db.py                # Database initialization
│
└── docs/
    ├── README.md                 # Main documentation
    ├── SETUP.md                  # Setup instructions
    ├── QUICKSTART.md             # Quick start guide
    ├── TESTING.md                # Testing guide
    └── ARCHITECTURE.md           # This file
```

## Future Enhancements

### Planned Features
1. **Advanced Analytics:** Transaction patterns, spending trends
2. **Mobile App:** React Native/Flutter mobile client
3. **Payment Integration:** Stripe for fund transfers
4. **Real-time Updates:** WebSocket for price alerts
5. **Multi-language Support:** i18n for global users
6. **Two-Factor Authentication:** OTP/TOTP for security
7. **API for Third-Parties:** OAuth2 endpoints
8. **Advanced RAG:** Document ingestion, fine-tuning

### Performance Improvements
1. **Caching Layer:** Redis for FAQ cache
2. **Async Tasks:** Celery for background jobs
3. **Query Optimization:** MongoDB aggregation pipelines
4. **Vector Index Tuning:** HNSW parameter optimization

### Monitoring & Observability
1. **Logging:** Structured logging with ELK stack
2. **Metrics:** Prometheus for system metrics
3. **Tracing:** Jaeger for distributed tracing
4. **Alerting:** Alert on errors/latency spikes

---

For detailed setup and usage, refer to [README.md](README.md) and [SETUP.md](SETUP.md).
