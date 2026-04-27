# Ajeer Dashboard - Quick Start Guide

Get the Ajeer Dashboard up and running in 5 minutes!

## 1. Start the Databases

Using Docker Compose (easiest):
```bash
docker-compose up -d
```

This starts MongoDB and Qdrant automatically.

## 2. Set Up Environment

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Google API Key
# GOOGLE_API_KEY=your-api-key-here
```

Get a free Google API key from: https://makersuite.google.com

## 3. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## 4. Initialize Database

```bash
python scripts/init_db.py
```

This creates the database collections and loads sample FAQs.

## 5. Run the Application

```bash
python app.py
```

## 6. Access the Application

Open your browser and go to: **http://localhost:5000**

---

## First Steps

### Create an Account
1. Click "Register" on the login page
2. Fill in username, email, and password
3. Your country will be auto-detected
4. Your preferred currency will be set automatically

### Try Currency Converter
1. Go to Dashboard
2. Enter an amount
3. Select currencies
4. Click "Convert" to see real-time rates

### Chat with the Chatbot
1. Click "Open Chatbot" or use the Chatbot link in navigation
2. Ask a question like "How do I convert currencies?"
3. The chatbot will search FAQs and/or generate responses

---

## Default Login (if you added test data)

- Email: `test@example.com`
- Password: `TestPass123`

---

## Project Structure

```
ajeer-dashboard/
├── app.py                    # Main Flask app
├── config.py                 # Configuration
├── models.py                 # Database models
├── requirements.txt          # Dependencies
│
├── agents/                   # RAG chatbot agents
│   └── rag_agents.py
│
├── utils/                    # Helper utilities
│   └── helpers.py
│
├── templates/                # HTML templates
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── chatbot.html
│
└── static/                   # CSS and JavaScript
    ├── css/style.css
    └── js/main.js
```

---

## Features

✓ User authentication with password hashing
✓ Country-based currency assignment
✓ Real-time currency converter
✓ RAG chatbot with LangGraph
✓ FAQ knowledge base with vector embeddings
✓ Conversation history storage
✓ Responsive design

---

## Troubleshooting

### Port Already in Use?
Change ports in `docker-compose.yml` or use different port numbers.

### Database Connection Failed?
```bash
# Check if services are running
docker-compose ps

# View logs
docker-compose logs mongodb
docker-compose logs qdrant
```

### Google API Key Error?
```bash
# Verify it's set in .env
cat .env | grep GOOGLE_API_KEY

# Check if API is enabled in Google Cloud Console
# https://console.cloud.google.com
```

### Module Import Error?
```bash
# Activate virtual environment
source venv/bin/activate  # or: venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Stopping Everything

```bash
# Stop Flask app: Press Ctrl+C in the terminal

# Stop databases
docker-compose down
```

---

## Next Steps

- Read [README.md](README.md) for complete documentation
- Check [SETUP.md](SETUP.md) for detailed setup instructions
- Review [TESTING.md](TESTING.md) for API testing guide

---

## Need Help?

- Check the logs: `docker-compose logs -f`
- Review [SETUP.md](SETUP.md) for detailed instructions
- Check [README.md](README.md) for troubleshooting

---

**Enjoy using Ajeer Dashboard!**
