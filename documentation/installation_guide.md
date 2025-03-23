# Kriangle Installation Guide

This guide provides comprehensive instructions for installing and deploying the Kriangle SEO platform in both local development and production environments.

## System Requirements

### Local Development
- Python 3.9+
- Django 4.2+
- Node.js 16+ (for front-end assets)
- SQLite (default) or PostgreSQL 13+

### Production
- Linux server (Ubuntu 20.04+ recommended)
- Python 3.9+
- PostgreSQL 13+
- Nginx or Apache web server
- uWSGI or Gunicorn
- SSL certificate for HTTPS

## Local Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/kriangle.git
cd kriangle
```

### 2. Set Up Python Environment
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Apply migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser
```

### 4. Static Files
```bash
# Collect static files
python manage.py collectstatic
```

### 5. Install Additional Packages
For the SEO reporting feature:
```bash
python -m pip install reportlab
```

For the Off-Page SEO Automation system:
```bash
# Install required packages for AI content generation
python -m pip install huggingface_hub requests
```

### 6. Run Development Server
```bash
python manage.py runserver
```

The application will be available at http://127.0.0.1:8000/

## Production Deployment

### 1. Server Preparation
```bash
# Update package lists
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-venv postgresql nginx
```

### 2. Database Setup
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE kriangle;
CREATE USER kriangleuser WITH PASSWORD 'your_secure_password';
ALTER ROLE kriangleuser SET client_encoding TO 'utf8';
ALTER ROLE kriangleuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE kriangleuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE kriangle TO kriangleuser;
\q
```

### 3. Application Setup
```bash
# Clone repository to /var/www
sudo mkdir -p /var/www
cd /var/www
sudo git clone https://github.com/yourusername/kriangle.git
cd kriangle

# Set up virtual environment
sudo python3 -m venv venv
sudo source venv/bin/activate
sudo pip install -r requirements.txt
sudo pip install uwsgi

# Install additional required packages
sudo pip install reportlab huggingface_hub requests

# Configure environment variables
sudo nano .env
# Add the following:
# DATABASE_URL=postgres://kriangleuser:your_secure_password@localhost:5432/kriangle
# DEBUG=False
# SECRET_KEY=your_secret_key
# ALLOWED_HOSTS=yourdomain.com

# Apply migrations
sudo python manage.py migrate
sudo python manage.py createsuperuser
sudo python manage.py collectstatic
```

### 4. uWSGI Configuration
Create a configuration file:
```bash
sudo nano /var/www/kriangle/uwsgi.ini
```

Add the following content:
```ini
[uwsgi]
chdir = /var/www/kriangle
module = kriangle.wsgi:application
home = /var/www/kriangle/venv
master = true
processes = 5
socket = /var/www/kriangle/kriangle.sock
chmod-socket = 666
vacuum = true
die-on-term = true
```

### 5. Nginx Configuration
Create a new Nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/kriangle
```

Add the following content:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/kriangle;
    }

    location /media/ {
        root /var/www/kriangle;
    }

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/var/www/kriangle/kriangle.sock;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/kriangle /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

### 6. SSL Configuration (Optional but Recommended)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 7. Setting Up uWSGI as a Service
Create a systemd service file:
```bash
sudo nano /etc/systemd/system/kriangle.service
```

Add the following content:
```ini
[Unit]
Description=uWSGI instance to serve Kriangle
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/kriangle
Environment="PATH=/var/www/kriangle/venv/bin"
ExecStart=/var/www/kriangle/venv/bin/uwsgi --ini /var/www/kriangle/uwsgi.ini

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable kriangle
sudo systemctl start kriangle
```

## Off-Page SEO Automation System Setup

The Kriangle platform includes an Off-Page SEO Automation system that requires additional configuration.

### 1. Database Configuration

The Off-Page SEO Automation system uses two main models:
- `APICredential`: Stores API keys for various services
- `SEOTask`: Manages off-page SEO tasks and their statuses

These models are automatically created during the standard database migration process.

### 2. API Credentials Setup

For the Off-Page SEO Automation system to connect to external services, you need to configure API credentials:

1. Access the admin interface at `/admin/`
2. Navigate to "API Credentials" section
3. Add credentials for each service you want to integrate with:
   - Email services (SMTP configuration)
   - Social media platforms
   - Web directories
   - Hugging Face API (for content generation)

### 3. Content Generation Setup

The system uses Hugging Face's free models for content generation. To set up:

1. Register for a free account at [Hugging Face](https://huggingface.co/)
2. Generate an API key
3. Add the API key to your environment variables or settings:

```bash
# In your .env file or directly in settings.py
HUGGINGFACE_API_KEY=your_api_key_here
```

### 4. Email Configuration (for Outreach)

Configure email settings for guest post outreach:

```python
# In settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your_smtp_server'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your_email@example.com'
EMAIL_HOST_PASSWORD = 'your_email_password'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'your_email@example.com'
```

### 5. Task Scheduler (Optional)

For automated background processing of SEO tasks:

```bash
# Install Celery
pip install celery redis

# Configure Celery in settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

Create a Celery configuration file and worker process to handle background tasks.

## Verification and Testing

### 1. Access the Application
- Local: http://127.0.0.1:8000/
- Production: https://yourdomain.com/

### 2. Admin Interface
Access the admin interface at `/admin/` to verify all models are properly created and accessible.

### 3. Test Off-Page SEO Features
1. Navigate to `/offpage-automation/` in your browser
2. Enter a test URL and keywords
3. Create a test task of each type to ensure the content generation works
4. Verify task status updates correctly

## Troubleshooting

### Common Issues

1. **Database Migration Errors**:
   ```bash
   python manage.py migrate --fake-initial
   ```

2. **Static Files Not Loading**:
   Check your `STATIC_URL` and `STATIC_ROOT` settings and run:
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Permission Issues**:
   ```bash
   sudo chown -R www-data:www-data /var/www/kriangle
   sudo chmod -R 755 /var/www/kriangle
   ```

4. **API Connection Issues**:
   Verify your API keys are correctly stored in the database or environment variables.

### Logs and Debugging

- Check application logs:
  ```bash
  tail -f /var/log/uwsgi/kriangle.log
  ```

- Check Nginx logs:
  ```bash
  tail -f /var/log/nginx/error.log
  ```

- Enable Django debug mode temporarily in production:
  ```python
  # In settings.py
  DEBUG = True
  ```
  Remember to set it back to False after debugging.

## Maintenance

### Regular Updates
```bash
# Pull latest code
git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Restart services
sudo systemctl restart kriangle
sudo systemctl restart nginx
```

### Database Backups
```bash
# Create a backup
sudo -u postgres pg_dump kriangle > kriangle_backup_$(date +%Y%m%d).sql

# Restore from backup
sudo -u postgres psql kriangle < kriangle_backup_file.sql
```

---

Last updated: March 23, 2025 