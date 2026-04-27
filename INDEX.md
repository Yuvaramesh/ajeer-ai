# Ajeer Dashboard - Documentation Index

Complete guide to all documentation files and how to use them.

## Getting Started

### 1. First Time Setup
Start here if you're setting up the project for the first time:
- **[QUICKSTART.md](QUICKSTART.md)** (5 min read) - Get running in 5 minutes
- **[SETUP.md](SETUP.md)** (30 min read) - Detailed setup with Docker and manual options

### 2. Understanding the Project
Learn what has been built:
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Overview of all components
- **[README.md](README.md)** - Complete feature list and usage guide

### 3. How It Works
Deep dive into the architecture:
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and component details
- **[ARCHITECTURE.md#Data Flow Diagrams](ARCHITECTURE.md#data-flow-diagrams)** - Visual flow diagrams

## Using the Application

### Running Locally
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [SETUP.md#Quick Start (Using Docker)](SETUP.md#quick-start-using-docker) - Docker setup

### Using Features
- [README.md#Usage](README.md#usage) - How to use each feature
- [README.md#API Endpoints](README.md#api-endpoints) - API documentation

### API Reference
- [TESTING.md#Test Scenarios](TESTING.md#test-scenarios) - All API examples
- [README.md#API Endpoints](README.md#api-endpoints) - Endpoint reference

## Development & Testing

### Testing the Application
- **[TESTING.md](TESTING.md)** - Complete testing guide
- [TESTING.md#Test Scenarios](TESTING.md#test-scenarios) - Test cases with cURL
- [TESTING.md#Automated Testing Script](TESTING.md#automated-testing-script) - Python tests

### Debugging
- [SETUP.md#Troubleshooting](SETUP.md#troubleshooting) - Common issues and fixes
- [README.md#Troubleshooting](README.md#troubleshooting) - More troubleshooting
- [TESTING.md#Debugging](TESTING.md#debugging) - Debug techniques

### Database Setup
- [SETUP.md#MongoDB Installation](SETUP.md#mongodb-installation) - MongoDB setup
- [SETUP.md#Qdrant Installation](SETUP.md#qdrant-installation) - Qdrant setup
- [ARCHITECTURE.md#MongoDB Models](ARCHITECTURE.md#mongodb-models) - Schema details

## Production & Deployment

### Deploying to Production
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide
- [DEPLOYMENT.md#Deployment Options](DEPLOYMENT.md#deployment-options) - Choose your platform
- [DEPLOYMENT.md#Docker + VPS](DEPLOYMENT.md#option-3-docker--vps-full-control) - Recommended option

### Specific Platforms
- [DEPLOYMENT.md#Vercel](DEPLOYMENT.md#option-1-vercel-recommended-for-quick-deploy) - Deploy to Vercel
- [DEPLOYMENT.md#Heroku](DEPLOYMENT.md#option-2-heroku) - Deploy to Heroku
- [DEPLOYMENT.md#AWS EC2](DEPLOYMENT.md#option-4-aws-ec2) - Deploy to AWS
- [DEPLOYMENT.md#Docker + VPS](DEPLOYMENT.md#option-3-docker--vps-full-control) - VPS deployment

### Production Considerations
- [DEPLOYMENT.md#Monitoring & Logging](DEPLOYMENT.md#monitoring--logging) - Monitoring setup
- [DEPLOYMENT.md#Backup & Disaster Recovery](DEPLOYMENT.md#backup--disaster-recovery) - Backups
- [DEPLOYMENT.md#Performance Optimization](DEPLOYMENT.md#performance-optimization) - Optimization
- [DEPLOYMENT.md#Security Hardening](DEPLOYMENT.md#security-hardening) - Security

## Architecture & Design

### System Design
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system architecture
- [ARCHITECTURE.md#System Overview](ARCHITECTURE.md#system-overview) - Architecture diagram
- [ARCHITECTURE.md#Component Architecture](ARCHITECTURE.md#component-architecture) - Components explained

### Data Architecture
- [ARCHITECTURE.md#MongoDB Collections Schema](ARCHITECTURE.md#mongodb-collections-schema) - Database schema
- [ARCHITECTURE.md#Data Flow Diagrams](ARCHITECTURE.md#data-flow-diagrams) - Data flow visualization
- [README.md#Database Schema](README.md#database-schema) - Schema overview

### RAG Chatbot Design
- [ARCHITECTURE.md#RAG Agent System](ARCHITECTURE.md#3-rag-agent-system) - How RAG works
- [README.md#RAG Agent System](README.md#rag-agent-system) - RAG explanation
- [ARCHITECTURE.md#Chatbot Query Flow](ARCHITECTURE.md#3-chatbot-query-flow) - Query processing

## Code Reference

### Main Application
- `app.py` - Flask application with route handlers
- `config.py` - Configuration management
- `models.py` - MongoDB models and database operations

### Agents & AI
- `agents/rag_agents.py` - LangGraph multi-agent system
- `utils/helpers.py` - Utility functions (auth, currency, validation)

### Frontend
- `templates/base.html` - Base template
- `templates/login.html` - Login page
- `templates/register.html` - Registration page
- `templates/dashboard.html` - Main dashboard
- `templates/chatbot.html` - Chatbot interface
- `static/css/style.css` - Stylesheet
- `static/js/main.js` - JavaScript utilities

### Configuration & Setup
- `requirements.txt` - Python dependencies
- `.env.example` - Environment template
- `docker-compose.yml` - Docker services
- `scripts/init_db.py` - Database initialization

## Quick Navigation

### By Role

**As a User:**
1. [QUICKSTART.md](QUICKSTART.md) - Set up and start using
2. [README.md#Usage](README.md#usage) - Learn features
3. [SETUP.md#Troubleshooting](SETUP.md#troubleshooting) - Solve problems

**As a Developer:**
1. [QUICKSTART.md](QUICKSTART.md) - Get it running
2. [ARCHITECTURE.md](ARCHITECTURE.md) - Understand the design
3. [TESTING.md](TESTING.md) - Test your changes
4. [README.md#Project Structure](README.md#project-structure) - Find the code

**As a DevOps Engineer:**
1. [SETUP.md](SETUP.md) - Infrastructure setup
2. [DEPLOYMENT.md](DEPLOYMENT.md) - Deploy to production
3. [DEPLOYMENT.md#Monitoring & Logging](DEPLOYMENT.md#monitoring--logging) - Monitor in production

### By Task

**"I want to run it locally"**
→ [QUICKSTART.md](QUICKSTART.md)

**"I want to understand how it works"**
→ [ARCHITECTURE.md](ARCHITECTURE.md)

**"I want to test it"**
→ [TESTING.md](TESTING.md)

**"I want to deploy it"**
→ [DEPLOYMENT.md](DEPLOYMENT.md)

**"I want to fix something"**
→ [SETUP.md#Troubleshooting](SETUP.md#troubleshooting)

**"I want to extend it"**
→ [ARCHITECTURE.md](ARCHITECTURE.md) then code

**"I want to use the API"**
→ [TESTING.md#Test Scenarios](TESTING.md#test-scenarios)

## Documentation Overview

### Beginner Guides
- [QUICKSTART.md](QUICKSTART.md) - Start here!
- [SETUP.md](SETUP.md) - Detailed setup

### Feature Documentation
- [README.md](README.md) - All features explained
- [README.md#API Endpoints](README.md#api-endpoints) - API reference

### Technical Documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [TESTING.md](TESTING.md) - Testing guide

### Operations Documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
- [DEPLOYMENT.md#Monitoring & Logging](DEPLOYMENT.md#monitoring--logging) - Monitoring

### Reference
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project overview
- This file - Documentation index

## File Structure

```
Documentation Files:
├── INDEX.md                    ← You are here
├── QUICKSTART.md              ← Start here (5 min)
├── SETUP.md                   ← Detailed setup (30 min)
├── README.md                  ← Feature guide (20 min)
├── ARCHITECTURE.md            ← System design (30 min)
├── TESTING.md                 ← Testing guide (20 min)
├── DEPLOYMENT.md              ← Deploy to prod (45 min)
└── PROJECT_SUMMARY.md         ← Project overview (10 min)

Application Code:
├── app.py                     ← Main Flask app
├── config.py                  ← Configuration
├── models.py                  ← Database models
├── agents/
│   └── rag_agents.py         ← RAG system
├── utils/
│   └── helpers.py            ← Utility functions
├── templates/                 ← HTML pages
└── static/                    ← CSS & JS

Setup & Deployment:
├── requirements.txt           ← Dependencies
├── .env.example              ← Environment template
├── docker-compose.yml        ← Docker services
└── scripts/
    └── init_db.py            ← Initialize database
```

## Reading Time Estimates

| Document | Time | Best For |
|----------|------|----------|
| QUICKSTART.md | 5 min | Getting started fast |
| README.md | 20 min | Understanding features |
| SETUP.md | 30 min | Detailed setup |
| TESTING.md | 20 min | Testing and debugging |
| ARCHITECTURE.md | 30 min | Understanding design |
| DEPLOYMENT.md | 45 min | Production deployment |
| PROJECT_SUMMARY.md | 10 min | Project overview |

## Need Help?

### Common Questions

**Q: How do I get started?**
A: Read [QUICKSTART.md](QUICKSTART.md) (5 minutes)

**Q: How do I deploy to production?**
A: Read [DEPLOYMENT.md](DEPLOYMENT.md)

**Q: How do I test the API?**
A: Read [TESTING.md](TESTING.md)

**Q: Something is broken, how do I fix it?**
A: Check [SETUP.md#Troubleshooting](SETUP.md#troubleshooting)

**Q: How does the RAG chatbot work?**
A: Read [ARCHITECTURE.md#RAG Agent System](ARCHITECTURE.md#3-rag-agent-system)

**Q: Can I modify the database schema?**
A: See [ARCHITECTURE.md#MongoDB Collections Schema](ARCHITECTURE.md#mongodb-collections-schema)

## Key Information

### Recommended Reading Order

1. **QUICKSTART.md** - Get it running (5 min)
2. **README.md** - Understand features (20 min)
3. **ARCHITECTURE.md** - Learn the design (30 min)
4. **TESTING.md** - Test your changes (20 min)
5. **DEPLOYMENT.md** - Deploy to production (45 min)

### Technologies Used

- **Backend:** Flask, Python 3.8+
- **Databases:** MongoDB (data), Qdrant (vectors)
- **AI/ML:** LangGraph, Google Gemini API
- **Frontend:** HTML, CSS, JavaScript
- **Infrastructure:** Docker, Docker Compose

### Supported Features

✓ User authentication with password hashing
✓ Country-based currency detection
✓ Real-time currency conversion
✓ RAG chatbot with LangGraph
✓ FAQ semantic search
✓ LLM fallback responses
✓ Conversation history
✓ Responsive UI design

---

**Happy exploring! Start with [QUICKSTART.md](QUICKSTART.md) to get running in 5 minutes.**
