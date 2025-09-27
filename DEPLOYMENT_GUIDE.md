# SmartBiz360 Deployment Guide

## 🚀 Production Deployment

This guide covers deploying SmartBiz360 to production using Docker and Docker Compose.

## 📋 Prerequisites

- Docker and Docker Compose installed
- PostgreSQL database (or use the included Docker setup)
- Domain name (optional, for production)

## 🐳 Quick Start with Docker

### 1. Clone and Setup

```bash
git clone <your-repo>
cd SmartBiz360
```

### 2. Backend Setup

```bash
cd backend

# Copy environment file
cp env.example .env

# Edit .env with your production values
nano .env
```

**Important Environment Variables:**
```env
DATABASE_URL=postgresql://username:password@localhost:5432/smartbiz360
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
CORS_ORIGINS=https://yourdomain.com
FLASK_ENV=production
```

### 3. Frontend Setup

```bash
cd ../frontend

# Copy environment file
cp env.example .env

# Edit .env with your API URL
nano .env
```

```env
REACT_APP_API_BASE_URL=https://api.yourdomain.com/api/v1
NODE_ENV=production
```

### 4. Deploy with Docker Compose

```bash
# From the root directory
docker-compose up -d
```

This will start:
- PostgreSQL database
- Backend API server
- Frontend web application

## 🔧 Manual Deployment

### Backend Deployment

1. **Install Dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Setup Database:**
```bash
# Create database
createdb smartbiz360

# Run migrations
flask db upgrade

# Initialize with sample data
python init_db.py
```

3. **Start Server:**
```bash
# Development
python app.py

# Production with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

### Frontend Deployment

1. **Install Dependencies:**
```bash
cd frontend
npm install
```

2. **Build for Production:**
```bash
npm run build
```

3. **Serve with Nginx:**
```bash
# Copy build files to nginx directory
sudo cp -r build/* /var/www/html/

# Configure nginx (see nginx.conf example)
```

## 🌐 Production Configuration

### Backend Security

1. **Environment Variables:**
```env
SECRET_KEY=<generate-strong-secret>
JWT_SECRET_KEY=<generate-strong-jwt-secret>
FLASK_ENV=production
FLASK_DEBUG=False
```

2. **Database Security:**
- Use strong passwords
- Enable SSL connections
- Regular backups
- Access restrictions

3. **File Upload Security:**
- Validate file types
- Limit file sizes
- Scan for malware
- Store outside web root

### Frontend Security

1. **HTTPS Configuration:**
```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

2. **API Security:**
- CORS configuration
- Rate limiting
- Input validation
- Authentication tokens

## 📊 Monitoring and Logging

### Backend Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Health Checks

```bash
# Backend health check
curl http://localhost:5000/health

# Database health check
curl http://localhost:5000/api/v1/dashboard/stats
```

## 🔄 Backup and Recovery

### Database Backup

```bash
# Create backup
pg_dump smartbiz360 > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql smartbiz360 < backup_file.sql
```

### File Backup

```bash
# Backup uploads directory
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz uploads/
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed:**
   - Check database credentials
   - Verify database is running
   - Check network connectivity

2. **CORS Errors:**
   - Update CORS_ORIGINS in backend .env
   - Ensure frontend URL is included

3. **File Upload Issues:**
   - Check upload directory permissions
   - Verify file size limits
   - Check disk space

4. **Authentication Issues:**
   - Verify JWT_SECRET_KEY is set
   - Check token expiration
   - Clear browser storage

### Logs

```bash
# View backend logs
docker-compose logs backend

# View database logs
docker-compose logs db

# View frontend logs
docker-compose logs frontend
```

## 📈 Performance Optimization

### Backend Optimization

1. **Database:**
   - Add indexes for frequently queried columns
   - Use connection pooling
   - Optimize queries

2. **Caching:**
   - Implement Redis for session storage
   - Cache frequently accessed data
   - Use CDN for static files

3. **Server:**
   - Use multiple workers (Gunicorn)
   - Enable compression
   - Optimize images

### Frontend Optimization

1. **Build Optimization:**
   - Enable code splitting
   - Minify CSS/JS
   - Optimize images
   - Use CDN

2. **Runtime Optimization:**
   - Implement lazy loading
   - Use React.memo for components
   - Optimize bundle size

## 🔐 Security Checklist

- [ ] Strong secret keys generated
- [ ] HTTPS enabled
- [ ] Database access restricted
- [ ] File upload validation
- [ ] CORS properly configured
- [ ] Security headers set
- [ ] Regular security updates
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] Error handling implemented

## 📞 Support

For deployment issues:
1. Check logs for error messages
2. Verify environment variables
3. Test database connectivity
4. Check file permissions
5. Review security configuration

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] Database setup and migrated
- [ ] SSL certificates installed
- [ ] Domain configured
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] Security measures applied
- [ ] Performance optimized
- [ ] Documentation updated
- [ ] Team trained on deployment
