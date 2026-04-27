# Ajeer Dashboard - Testing Guide

Complete guide for testing the Ajeer Dashboard application, including API endpoints, authentication, currency converter, and RAG chatbot.

## Prerequisites

- Flask app running on `http://localhost:5000`
- MongoDB running on `mongodb://localhost:27017`
- Qdrant running on `http://localhost:6333`
- Google API Key configured

## Testing Tools

### Using cURL

```bash
# Basic GET request
curl http://localhost:5000/api/user-profile

# POST request with JSON data
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I convert currency?"}'
```

### Using Python Requests

```python
import requests

response = requests.post('http://localhost:5000/api/chat', json={'query': 'Hello'})
print(response.json())
```

### Using Postman

1. Create a new workspace
2. Import requests to test each endpoint
3. Set cookies for session management

---

## Test Scenarios

### 1. User Registration & Login

#### Test Register New User

**Request:**
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Registration successful. Please login.",
  "redirect": "/login"
}
```

**Test Cases:**
- ✓ Valid registration
- ✓ Duplicate email
- ✓ Duplicate username
- ✓ Password too short
- ✓ Passwords don't match
- ✓ Invalid email format

#### Test Login

**Request:**
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }' \
  -c cookies.txt
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "redirect": "/dashboard"
}
```

**Test Cases:**
- ✓ Valid credentials
- ✓ Wrong password
- ✓ Non-existent email
- ✓ Empty fields

---

### 2. Country Detection & Currency Assignment

**Request (during registration):**

The system automatically detects country from IP and assigns currency. You can verify this by:

```bash
# After login, check user profile
curl http://localhost:5000/api/user-profile \
  -b cookies.txt
```

**Expected Response:**
```json
{
  "success": true,
  "username": "testuser",
  "email": "test@example.com",
  "country": "US",
  "preferred_currency": "USD",
  "created_at": "2024-04-27T10:30:00"
}
```

**Test Cases:**
- ✓ Country correctly detected from IP
- ✓ Correct currency assigned to country
- ✓ User can update preferred currency

---

### 3. Currency Converter

#### Test Convert Currency

**Request:**
```bash
curl -X POST http://localhost:5000/api/convert-currency \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "amount": 100,
    "from_currency": "USD",
    "to_currency": "EUR"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "original_amount": 100,
  "original_currency": "USD",
  "converted_amount": 92.50,
  "target_currency": "EUR"
}
```

**Test Cases:**
- ✓ USD to EUR
- ✓ EUR to INR
- ✓ Same currency (no conversion)
- ✓ Large amounts (1000000)
- ✓ Decimal amounts (12.50)
- ✓ Without login (should fail)

#### Test Get Exchange Rate

**Request:**
```bash
curl "http://localhost:5000/api/exchange-rate?from=USD&to=EUR"
```

**Expected Response:**
```json
{
  "success": true,
  "from": "USD",
  "to": "EUR",
  "rate": 0.925
}
```

---

### 4. RAG Chatbot

#### Test Chat Query (FAQ Match)

**Request:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "query": "How do I convert currencies?"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "response": "Simply navigate to the Currency Converter card...",
  "agent_type": "faq_search",
  "faq_used": true
}
```

#### Test Chat Query (General Question)

**Request:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "query": "What is blockchain?"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "response": "Blockchain is a distributed ledger technology...",
  "agent_type": "general_response",
  "faq_used": false
}
```

**Test Cases:**
- ✓ FAQ question matching
- ✓ General knowledge questions
- ✓ Multi-turn conversation
- ✓ Long context history
- ✓ Without login (should fail)
- ✓ Empty query (should fail)

#### Test Conversation History

**Request:**
```bash
# The conversation history is automatically stored
# Query the database to verify
mongosh "mongodb://admin:admin123@localhost:27017/ajeer_dashboard"
db.conversations.find({ user_id: ObjectId("...") }).pretty()
```

---

### 5. User Profile Management

#### Get User Profile

**Request:**
```bash
curl http://localhost:5000/api/user-profile \
  -b cookies.txt
```

**Expected Response:**
```json
{
  "success": true,
  "username": "testuser",
  "email": "test@example.com",
  "country": "US",
  "preferred_currency": "USD",
  "created_at": "2024-04-27T10:30:00"
}
```

#### Update User Profile

**Request:**
```bash
curl -X PUT http://localhost:5000/api/user-profile \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "preferred_currency": "EUR"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Profile updated"
}
```

---

### 6. Authentication Flow

#### Test Session Management

```bash
# 1. Register/Login (creates session)
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePass123"}' \
  -c cookies.txt

# 2. Access protected route
curl http://localhost:5000/dashboard \
  -b cookies.txt

# 3. Logout (clears session)
curl http://localhost:5000/logout \
  -c cookies.txt

# 4. Try to access protected route again (should fail)
curl http://localhost:5000/dashboard \
  -b cookies.txt
# Should redirect to /login
```

---

## Automated Testing Script

Create `tests/test_api.py`:

```python
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"
session = requests.Session()

def test_registration():
    """Test user registration"""
    print("[TEST] Testing user registration...")
    
    payload = {
        "username": f"testuser_{datetime.now().timestamp()}",
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "password": "SecurePass123",
        "password_confirm": "SecurePass123"
    }
    
    response = session.post(f"{BASE_URL}/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data['success'] == True
    print("✓ Registration successful")

def test_login():
    """Test user login"""
    print("[TEST] Testing user login...")
    
    payload = {
        "email": "test@example.com",
        "password": "SecurePass123"
    }
    
    response = session.post(f"{BASE_URL}/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    print("✓ Login successful")

def test_currency_conversion():
    """Test currency conversion"""
    print("[TEST] Testing currency conversion...")
    
    payload = {
        "amount": 100,
        "from_currency": "USD",
        "to_currency": "EUR"
    }
    
    response = session.post(f"{BASE_URL}/api/convert-currency", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    assert data['converted_amount'] > 0
    print(f"✓ Conversion: 100 USD = {data['converted_amount']} EUR")

def test_chatbot():
    """Test chatbot"""
    print("[TEST] Testing chatbot...")
    
    payload = {
        "query": "How do I convert currencies?"
    }
    
    response = session.post(f"{BASE_URL}/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    assert 'response' in data
    print(f"✓ Chatbot responded with agent type: {data['agent_type']}")

def test_user_profile():
    """Test user profile"""
    print("[TEST] Testing user profile...")
    
    response = session.get(f"{BASE_URL}/api/user-profile")
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    print(f"✓ User: {data['username']} ({data['country']})")

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("Starting Ajeer Dashboard API Tests")
    print("=" * 50)
    
    try:
        test_registration()
        test_login()
        test_currency_conversion()
        test_chatbot()
        test_user_profile()
        
        print("=" * 50)
        print("✓ All tests passed!")
        print("=" * 50)
        return True
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    run_all_tests()
```

Run tests:
```bash
python tests/test_api.py
```

---

## Performance Testing

### Load Test Currency Converter

```python
import time
import requests
from concurrent.futures import ThreadPoolExecutor

def convert_currency():
    response = requests.post(
        'http://localhost:5000/api/convert-currency',
        json={'amount': 100, 'from_currency': 'USD', 'to_currency': 'EUR'},
        cookies={'session': 'your-session-id'}
    )
    return response.status_code == 200

def load_test():
    start = time.time()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda _: convert_currency(), range(100)))
    
    elapsed = time.time() - start
    successful = sum(results)
    
    print(f"100 requests in {elapsed:.2f}s")
    print(f"Successful: {successful}/100")
    print(f"Requests/sec: {100/elapsed:.2f}")

if __name__ == "__main__":
    load_test()
```

---

## Debugging

### Enable Debug Logging

Add to `app.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Database Debugging

```bash
# Check MongoDB collections
mongosh "mongodb://admin:admin123@localhost:27017/ajeer_dashboard"
db.collections()
db.users.findOne()
db.conversations.find().limit(5)

# Check Qdrant collections
curl http://localhost:6333/collections
```

### Browser DevTools

1. Open http://localhost:5000 in browser
2. Press F12 to open DevTools
3. Check:
   - Network tab for API calls
   - Console for JavaScript errors
   - Application tab for cookies/storage

---

## Known Issues & Workarounds

### Issue: FAQ Embedding Failed
**Solution:**
```bash
python scripts/init_db.py
```

### Issue: Currency Conversion Timeout
**Solution:** External API might be slow
```python
# Increase timeout in CurrencyConverter
response = requests.get(..., timeout=10)
```

### Issue: Chatbot Returns Generic Response
**Possible causes:**
- FAQ database not initialized
- Similarity threshold too high (set to 0.7)
- Query doesn't match any FAQs well

---

## Continuous Integration

GitHub Actions workflow example (`.github/workflows/test.yml`):

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:latest
        options: >-
          --health-cmd "mongosh ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 27017:27017
      qdrant:
        image: qdrant/qdrant:latest
        ports:
          - 6333:6333
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python scripts/init_db.py
      - run: python tests/test_api.py
```

---

## Test Checklist

- [ ] User can register with valid data
- [ ] User registration fails with invalid data
- [ ] User can login with correct credentials
- [ ] Login fails with wrong password
- [ ] Country is detected on registration
- [ ] Currency is assigned based on country
- [ ] Currency conversion returns correct result
- [ ] Exchange rates are retrieved successfully
- [ ] Chatbot responds to FAQ questions
- [ ] Chatbot generates responses for unknown queries
- [ ] User profile can be retrieved
- [ ] User profile can be updated
- [ ] Session persists across requests
- [ ] Logout clears session
- [ ] Protected routes require login
- [ ] Error responses are properly formatted

---

For more information, see [README.md](README.md) and [SETUP.md](SETUP.md).
