# Ajeer Dashboard - Complete Setup Guide

This guide will help you set up MongoDB and Qdrant vector database for the Ajeer Dashboard.

## Quick Start (Using Docker)

The easiest way to get started is using Docker Compose, which sets up both MongoDB and Qdrant automatically.

### Prerequisites
- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))
- Docker Compose (comes with Docker Desktop)
- 4GB RAM available
- Ports 27017, 6333, 8081 available (you can change them in docker-compose.yml)

### Step 1: Start Services with Docker Compose

```bash
# From the project root directory
docker-compose up -d
```

This will start:
- **MongoDB** on `mongodb://localhost:27017`
- **Qdrant** on `http://localhost:6333`
- **Mongo Express** (GUI) on `http://localhost:8081` (optional)

To check status:
```bash
docker-compose ps
```

To view logs:
```bash
docker-compose logs -f
```

### Step 2: Verify Services

**Check MongoDB connection:**
```bash
mongosh "mongodb://admin:admin123@localhost:27017"
```

**Check Qdrant health:**
```bash
curl http://localhost:6333/health
```

You should see:
```json
{"title":"Qdrant","version":"..."}
```

### Step 3: Update .env File

Create or update `.env` file:

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret-key-generate-one-here

# MongoDB Configuration (Docker default)
MONGODB_URI=mongodb://admin:admin123@localhost:27017/ajeer_dashboard

# Qdrant Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# Google API Configuration
GOOGLE_API_KEY=your-google-api-key-here
```

### Step 4: Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Initialize Database with FAQs

```bash
python scripts/init_db.py
```

You should see output like:
```
[v0] Starting Ajeer Dashboard initialization...
[v0] ✓ MongoDB connected successfully
[v0] ✓ RAG System initialized successfully
[v0] Added FAQ metadata 1/12
...
[v0] ✓ Initialization complete!
```

### Step 6: Run Flask Application

```bash
python app.py
```

Visit: **http://localhost:5000**

---

## Manual Setup (Without Docker)

If you prefer to install MongoDB and Qdrant manually:

### MongoDB Installation

**macOS:**
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# Or manually
mongod --dbpath /path/to/data
```

**Windows:**
1. Download from [mongodb.com](https://www.mongodb.com/try/download/community)
2. Run the installer
3. MongoDB will start automatically

**Linux (Ubuntu):**
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

### Qdrant Installation

**Docker (Recommended):**
```bash
docker run -d \
  -p 6333:6333 \
  --name qdrant \
  qdrant/qdrant:latest
```

**From Source:**
```bash
# Clone repository
git clone https://github.com/qdrant/qdrant.git
cd qdrant

# Build and run
cargo build --release
./target/release/qdrant
```

### Update .env for Manual Setup

```bash
MONGODB_URI=mongodb://localhost:27017/ajeer_dashboard
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
```

---

## Getting Google API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the following APIs:
   - Generative Language API
4. Create an API key (in Credentials section)
5. Copy the key to your `.env` file:

```bash
GOOGLE_API_KEY=your-api-key-here
```

### Alternative: Google Makersuite

For development, you can use Google Makersuite:
1. Visit [makersuite.google.com](https://makersuite.google.com)
2. Click "Get API key"
3. Copy the key to your `.env` file

---

## Database Configuration

### MongoDB Collections

The system automatically creates these collections:

- **users** - User accounts with authentication
- **conversations** - Chat history
- **faqs** - FAQ metadata

Indexes are automatically created on:
- `users.email` (unique)
- `users.username` (unique)
- `conversations.user_id`
- `conversations.created_at`
- `faqs.qdrant_id` (unique)

### Qdrant Configuration

Collection: `faqs_collection`
- Vector size: 768 (from Gemini embeddings)
- Distance metric: Cosine similarity
- Auto-indexed for fast retrieval

---

## Stopping Services

### Docker Compose

```bash
# Stop all services
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove all data (careful!)
docker-compose down -v
```

### Manual Services

**MongoDB:**
```bash
brew services stop mongodb-community  # macOS
sudo systemctl stop mongod             # Linux
# Windows: Stop from Services panel
```

**Qdrant:**
```bash
docker stop qdrant  # If using Docker
# Or Ctrl+C if running from source
```

---

## Troubleshooting

### MongoDB Connection Failed

**Error:** `connection refused` or `Unable to connect`

**Solution:**
```bash
# Check if MongoDB is running
ps aux | grep mongod

# Start MongoDB
docker-compose up mongodb -d
# Or: brew services start mongodb-community
# Or: sudo systemctl start mongod
```

### Qdrant Connection Failed

**Error:** `http://localhost:6333: connection refused`

**Solution:**
```bash
# Check if Qdrant is running
curl http://localhost:6333/health

# Start Qdrant
docker-compose up qdrant -d
```

### Google API Key Invalid

**Error:** `403 Forbidden` or `API_KEY_INVALID`

**Solution:**
1. Verify your API key is correct in `.env`
2. Check if the Generative Language API is enabled
3. Make sure the API key has no restrictions on IP or APIs

### FAQ Initialization Failed

**Error:** `Error adding FAQ to Qdrant`

**Solution:**
```bash
# Ensure Qdrant is running
curl http://localhost:6333/health

# Reinitialize
python scripts/init_db.py
```

### Ports Already in Use

**Error:** `Address already in use`

**Solution:** Change ports in `docker-compose.yml`:
```yaml
services:
  mongodb:
    ports:
      - "27018:27017"  # Change 27017 to 27018
  qdrant:
    ports:
      - "6334:6333"    # Change 6333 to 6334
```

Then update `.env`:
```bash
MONGODB_URI=mongodb://localhost:27018/ajeer_dashboard
QDRANT_URL=http://localhost:6334
```

---

## Monitoring and Management

### MongoDB Monitoring

Using Mongo Express (GUI):
1. Visit http://localhost:8081
2. Login with:
   - Username: `admin`
   - Password: `admin123`

Command line:
```bash
mongosh "mongodb://admin:admin123@localhost:27017"
use ajeer_dashboard
db.users.find()
```

### Qdrant Monitoring

Web UI:
1. Visit http://localhost:6333/dashboard (if enabled)

API:
```bash
# Get health status
curl http://localhost:6333/health

# Get collections
curl http://localhost:6333/collections
```

---

## Performance Tips

1. **Increase MongoDB memory**: Adjust in `docker-compose.yml`
2. **Optimize Qdrant indexing**: Configure in initialization script
3. **Use connection pooling**: Enabled by default in PyMongo
4. **Monitor disk space**: Vector embeddings require ~1-2GB for 10k FAQs

---

## Backup and Restore

### Backup MongoDB

```bash
mongodump --uri "mongodb://admin:admin123@localhost:27017/ajeer_dashboard" --out backup/
```

### Restore MongoDB

```bash
mongorestore --uri "mongodb://admin:admin123@localhost:27017/ajeer_dashboard" backup/ajeer_dashboard
```

### Backup Qdrant

```bash
# Using Docker
docker exec ajeer-qdrant tar czf /qdrant/backup.tar.gz /qdrant/storage

# Copy from container
docker cp ajeer-qdrant:/qdrant/backup.tar.gz ./
```

---

## Production Considerations

For production deployment:

1. **MongoDB:**
   - Use MongoDB Atlas (cloud)
   - Enable authentication
   - Use replica sets for redundancy
   - Enable encryption at rest

2. **Qdrant:**
   - Use managed Qdrant Cloud
   - Or self-host with proper backups
   - Enable API key authentication
   - Set up monitoring and alerts

3. **Security:**
   - Use strong database credentials
   - Restrict network access
   - Use VPCs/private networks
   - Enable SSL/TLS encryption

---

## Next Steps

1. ✓ Start MongoDB and Qdrant
2. ✓ Set up environment variables
3. ✓ Install Python dependencies
4. ✓ Initialize database with FAQs
5. Run the Flask application: `python app.py`

For more information, see [README.md](README.md).
