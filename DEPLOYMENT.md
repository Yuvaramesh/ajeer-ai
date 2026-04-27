# Ajeer Dashboard - Deployment Guide

Production deployment guide for the Ajeer Dashboard on various platforms.

## Pre-Deployment Checklist

- [ ] All tests passing locally
- [ ] `.env` file configured with production values
- [ ] Google API key with proper quotas set
- [ ] MongoDB backup strategy in place
- [ ] SSL/TLS certificates obtained
- [ ] Domain name configured
- [ ] Email service configured (optional)
- [ ] Monitoring and alerting set up
- [ ] Security review completed

## Deployment Options

### Option 1: Vercel (Recommended for Quick Deploy)

Vercel supports Python via serverless functions.

**Steps:**

1. **Create Vercel Project:**
```bash
npm i -g vercel
vercel login
vercel
```

2. **Add `vercel.json`:**
```json
{
  "buildCommand": "pip install -r requirements.txt",
  "devCommand": "python app.py",
  "env": {
    "GOOGLE_API_KEY": "@google_api_key",
    "MONGODB_URI": "@mongodb_uri",
    "QDRANT_URL": "@qdrant_url"
  }
}
```

3. **Deploy:**
```bash
vercel --prod
```

**Limitations:**
- No persistent storage for file uploads
- Maximum 60-second request timeout
- Use serverless databases (MongoDB Atlas, Qdrant Cloud)

### Option 2: Heroku

**Steps:**

1. **Create Heroku App:**
```bash
heroku create ajeer-dashboard
```

2. **Add Procfile:**
```
web: python app.py
```

3. **Add buildpacks:**
```bash
heroku buildpacks:add heroku/python
```

4. **Set environment variables:**
```bash
heroku config:set GOOGLE_API_KEY=your-key
heroku config:set MONGODB_URI=your-uri
heroku config:set QDRANT_URL=your-url
heroku config:set FLASK_SECRET_KEY=your-secret
```

5. **Deploy:**
```bash
git push heroku main
```

**Costs:** Starting at $7/month

### Option 3: Docker + VPS (Full Control)

**Recommended for maximum control and cost-effectiveness.**

1. **Create Production Dockerfile:**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
```

2. **Create `docker-compose.prod.yml`:**

```yaml
version: '3.8'

services:
  web:
    build: .
    container_name: ajeer-web
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      FLASK_ENV: production
      GOOGLE_API_KEY: ${GOOGLE_API_KEY}
      MONGODB_URI: ${MONGODB_URI}
      QDRANT_URL: ${QDRANT_URL}
      FLASK_SECRET_KEY: ${FLASK_SECRET_KEY}
    depends_on:
      - mongodb
      - qdrant
    networks:
      - ajeer-network

  mongodb:
    image: mongo:latest
    container_name: ajeer-mongodb-prod
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    volumes:
      - mongodb_data:/data/db
    networks:
      - ajeer-network
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    container_name: ajeer-qdrant-prod
    restart: unless-stopped
    environment:
      QDRANT_API_KEY: ${QDRANT_API_KEY}
    volumes:
      - qdrant_data:/qdrant/storage
    networks:
      - ajeer-network
    healthcheck:
      test: curl -f http://localhost:6333/health || exit 1
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    container_name: ajeer-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - web
    networks:
      - ajeer-network

volumes:
  mongodb_data:
    driver: local
  qdrant_data:
    driver: local

networks:
  ajeer-network:
    driver: bridge
```

3. **Nginx Configuration:**

```nginx
# nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    gzip on;

    upstream flask {
        server web:5000;
    }

    server {
        listen 80;
        server_name _;

        # Redirect to HTTPS
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/certs/fullchain.pem;
        ssl_certificate_key /etc/nginx/certs/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Frame-Options "DENY" always;
        add_header X-XSS-Protection "1; mode=block" always;

        client_max_body_size 10M;

        location / {
            proxy_pass http://flask;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location /static/ {
            alias /app/static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # Health check endpoint
        location /health {
            proxy_pass http://flask;
            access_log off;
        }
    }
}
```

4. **Deploy on VPS:**

```bash
# 1. SSH into VPS
ssh user@your-vps-ip

# 2. Clone repository
git clone https://github.com/your-repo/ajeer-dashboard.git
cd ajeer-dashboard

# 3. Set environment variables
cat > .env <<EOF
FLASK_ENV=production
GOOGLE_API_KEY=your-key
MONGODB_URI=your-uri
QDRANT_URL=your-url
FLASK_SECRET_KEY=generate-secure-key
MONGO_USER=admin
MONGO_PASSWORD=secure-password
QDRANT_API_KEY=secure-key
EOF

# 4. Get SSL certificates (Let's Encrypt)
sudo certbot certonly --standalone -d yourdomain.com

# 5. Start services
docker-compose -f docker-compose.prod.yml up -d

# 6. Initialize database
docker-compose -f docker-compose.prod.yml exec web python scripts/init_db.py
```

### Option 4: AWS EC2

**Steps:**

1. **Launch EC2 Instance:**
   - Choose Ubuntu 22.04 LTS
   - t3.medium or larger for production
   - Allow ports 80, 443, 22

2. **Install Docker:**
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER
```

3. **Deploy using Docker Compose:**
```bash
# Follow Option 3 steps above
```

4. **Use AWS RDS for MongoDB:**
   - Create DocumentDB (MongoDB-compatible)
   - Update MONGODB_URI in .env

5. **Use AWS Vector DB:**
   - Deploy Qdrant on separate EC2
   - Or use managed Qdrant Cloud

## Environment Configuration for Production

**Production .env:**
```bash
FLASK_ENV=production
FLASK_SECRET_KEY=generate-with: python -c "import secrets; print(secrets.token_hex(32))"

# Use managed databases
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/ajeer_dashboard
QDRANT_URL=https://your-qdrant-cloud.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key

GOOGLE_API_KEY=your-google-api-key

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

## Database Configuration for Production

### MongoDB Atlas

1. **Create cluster:**
   - Go to mongodb.com/cloud
   - Create free or paid cluster
   - Create database user
   - Whitelist IP ranges

2. **Connection string:**
```
mongodb+srv://username:password@cluster.mongodb.net/ajeer_dashboard
```

3. **Enable backups:**
   - Automated backups every 6 hours
   - Retention for 7-35 days

### Qdrant Cloud

1. **Sign up:**
   - Go to cloud.qdrant.io
   - Create account

2. **Create cluster:**
   - Choose region closest to users
   - Configure for production load

3. **Connection:**
```
https://your-cluster.qdrant.io:6333
```

## Monitoring & Logging

### Application Monitoring

**Add to app.py:**
```python
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('flask_requests_total', 'Total requests')
request_duration = Histogram('flask_request_duration_seconds', 'Request duration')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    request_count.inc()
    duration = time.time() - request.start_time
    request_duration.observe(duration)
    return response

@app.route('/metrics')
def metrics():
    return generate_latest()
```

### Log Aggregation

Use ELK Stack (Elasticsearch, Logstash, Kibana):

```python
from pythonjsonlogger import jsonlogger

# Configure JSON logging for easier parsing
handler = logging.FileHandler('logs/app.log')
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
app.logger.addHandler(handler)
```

### Uptime Monitoring

Use services like:
- Uptime Robot
- Datadog
- New Relic
- Prometheus + Grafana

## Backup & Disaster Recovery

### MongoDB Backups

```bash
# Automated backups with MongoDB Atlas (recommended)
# Or manual backups:
mongodump --uri "mongodb+srv://..." --out backup/

# Restore:
mongorestore --uri "mongodb+srv://..." backup/
```

### Qdrant Backups

```bash
# Snapshot backup
curl -X POST http://your-qdrant.com/snapshots

# Download snapshot from Qdrant Cloud console
```

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="/backups/ajeer-$DATE"

mkdir -p $BACKUP_DIR

# MongoDB backup
mongodump --uri "$MONGODB_URI" --out "$BACKUP_DIR/mongodb"

# Qdrant backup
curl -X POST "$QDRANT_URL/snapshots" -H "api-key: $QDRANT_API_KEY" \
    | jq '.result.name' > "$BACKUP_DIR/qdrant_snapshot.txt"

# Compress
tar czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"

# Upload to S3
aws s3 cp "$BACKUP_DIR.tar.gz" "s3://your-bucket/backups/"

# Cleanup old backups (keep 30 days)
find /backups -name "ajeer-*.tar.gz" -mtime +30 -delete
```

Schedule with cron:
```bash
0 2 * * * /path/to/backup.sh
```

## Performance Optimization

### Application Optimization

1. **Add caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_exchange_rate(from_curr, to_curr):
    # Cached for 1 hour
    pass
```

2. **Use Gunicorn workers:**
```bash
gunicorn --workers 4 --worker-class gevent app:app
```

3. **Enable gzip compression:**
```python
from flask_compress import Compress
Compress(app)
```

### Database Optimization

1. **MongoDB indexing:**
```javascript
db.users.createIndex({ "email": 1 }, { unique: true })
db.conversations.createIndex({ "user_id": 1, "created_at": -1 })
```

2. **Qdrant indexing:**
```python
# Automatic HNSW indexing with Qdrant
```

## Security Hardening

### SSL/TLS
```bash
# Use Let's Encrypt
sudo certbot certonly --standalone -d yourdomain.com
```

### Firewall
```bash
# UFW on Ubuntu
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Rate Limiting
```python
from flask_limiter import Limiter

limiter = Limiter(app)

@app.route('/api/chat', methods=['POST'])
@limiter.limit("10 per minute")
def chat():
    pass
```

### HTTPS Redirect
```python
@app.before_request
def enforce_https():
    if not request.is_secure and app.env == 'production':
        return redirect(request.url.replace('http://', 'https://'))
```

## CI/CD Pipeline

### GitHub Actions

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run tests
        run: python -m pytest tests/
      
      - name: Build Docker image
        run: docker build -t ajeer-dashboard:latest .
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USER }} --password-stdin
          docker push ajeer-dashboard:latest
      
      - name: Deploy to VPS
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_KEY }}
          script: |
            cd ajeer-dashboard
            docker-compose -f docker-compose.prod.yml pull
            docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting Deployment

### Port Already in Use
```bash
sudo lsof -i :5000
sudo kill -9 <PID>
```

### Database Connection Issues
```bash
# Test MongoDB
mongosh "your-connection-string"

# Test Qdrant
curl http://your-qdrant-url/health
```

### Memory Issues
```bash
# Monitor memory
docker stats

# Increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Maintenance

### Regular Tasks
- Monitor logs for errors
- Check disk space
- Update security patches
- Review database backups
- Monitor API quotas
- Update dependencies monthly

### Health Check Script
```bash
#!/bin/bash
echo "Checking Ajeer Dashboard health..."

# Check web service
curl -f http://localhost:5000/health || echo "Web service down"

# Check MongoDB
mongosh --eval "db.adminCommand('ping')" || echo "MongoDB down"

# Check Qdrant
curl -f http://localhost:6333/health || echo "Qdrant down"

echo "Health check complete"
```

---

Choose the deployment option that best fits your needs:
- **Quick start:** Heroku or Vercel
- **Full control:** Docker + VPS
- **Scalability:** AWS with managed databases
- **Highest availability:** Kubernetes on AWS/GCP/Azure

For more information, see [README.md](README.md) and [SETUP.md](SETUP.md).
