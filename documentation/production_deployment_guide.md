# Kriangle: Production Deployment Guide (AWS EC2 Ubuntu)

## EC2 Instance Setup

### 1. Launch EC2 Instance
- **AMI**: Ubuntu Server 22.04 LTS
- **Instance Type**: t2.micro (Free Tier)
- **Security Group**:
  - SSH (Port 22) from your IP
  - HTTP (Port 80) from anywhere
  - HTTPS (Port 443) from anywhere
  - Redis (Port 6379) from your IP only (if using Redis)

### 2. Connect to Instance
```bash
ssh -i your-key.pem ubuntu@your-ec2-public-dns
```

## Server Configuration

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Required Packages
```bash
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential libpq-dev libapache2-mod-wsgi-py3 git redis-server supervisor
```

### 3. Start and Enable Redis
```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify Redis is running
redis-cli ping  # Should return PONG
```

### 4. Secure Redis (Optional but Recommended)
```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf
```

Add the following changes:
- Set a password: `requirepass YourStrongPassword`
- Bind to localhost only: `bind 127.0.0.1`
- Disable protected mode if using password auth: `protected-mode no`

```bash
# Restart Redis
sudo systemctl restart redis-server
```

## Application Deployment

### 1. Clone Repository
```bash
mkdir -p /home/ubuntu/kriangle
cd /home/ubuntu/kriangle
git clone your-repo-url .
```

### 2. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### 3. Configure Production Settings
Create `/home/ubuntu/kriangle/kriangle/.env`:
```
DEBUG=False
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=your-ec2-public-dns,your-domain-name
DATABASE_URL=sqlite:///db.sqlite3
```

Edit `settings.py` to add Redis for Celery:
```python
# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Add password if configured: 'redis://:password@localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
# Additional production settings
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ACKS_LATE = True
```

### 4. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --no-input
```

## Celery Configuration

### 1. Setup Supervisor for Celery Worker
Create `/etc/supervisor/conf.d/kriangle_celery.conf`:
```ini
[program:kriangle_celery]
command=/home/ubuntu/kriangle/venv/bin/celery -A kriangle worker --loglevel=info
directory=/home/ubuntu/kriangle
user=ubuntu
numprocs=1
stdout_logfile=/home/ubuntu/kriangle/logs/celery.log
stderr_logfile=/home/ubuntu/kriangle/logs/celery_error.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
priority=999
```

### 2. Setup Supervisor for Celery Beat (for scheduled tasks)
Create `/etc/supervisor/conf.d/kriangle_celery_beat.conf`:
```ini
[program:kriangle_celery_beat]
command=/home/ubuntu/kriangle/venv/bin/celery -A kriangle beat --loglevel=info
directory=/home/ubuntu/kriangle
user=ubuntu
numprocs=1
stdout_logfile=/home/ubuntu/kriangle/logs/celery_beat.log
stderr_logfile=/home/ubuntu/kriangle/logs/celery_beat_error.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
priority=998
```

### 3. Create Logs Directory
```bash
mkdir -p /home/ubuntu/kriangle/logs
touch /home/ubuntu/kriangle/logs/celery.log
touch /home/ubuntu/kriangle/logs/celery_error.log
touch /home/ubuntu/kriangle/logs/celery_beat.log
touch /home/ubuntu/kriangle/logs/celery_beat_error.log
```

### 4. Start Celery Services
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start kriangle_celery
sudo supervisorctl start kriangle_celery_beat  # Only if you're using scheduled tasks
```

## Apache Configuration

### 1. Create Apache Virtual Host
Create `/etc/apache2/sites-available/kriangle.conf`:
```apache
<VirtualHost *:80>
    ServerName your-ec2-public-dns
    ServerAlias your-domain-name
    
    DocumentRoot /home/ubuntu/kriangle
    
    <Directory /home/ubuntu/kriangle/kriangle>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
    
    WSGIDaemonProcess kriangle python-home=/home/ubuntu/kriangle/venv python-path=/home/ubuntu/kriangle
    WSGIProcessGroup kriangle
    WSGIScriptAlias / /home/ubuntu/kriangle/kriangle/wsgi.py
    
    Alias /static/ /home/ubuntu/kriangle/static/
    <Directory /home/ubuntu/kriangle/static>
        Require all granted
    </Directory>
    
    Alias /media/ /home/ubuntu/kriangle/media/
    <Directory /home/ubuntu/kriangle/media>
        Require all granted
    </Directory>
    
    ErrorLog ${APACHE_LOG_DIR}/kriangle-error.log
    CustomLog ${APACHE_LOG_DIR}/kriangle-access.log combined
</VirtualHost>
```

### 2. Enable Site and Restart Apache
```bash
sudo chown -R ubuntu:www-data /home/ubuntu/kriangle
find /home/ubuntu/kriangle -type d -exec chmod 750 {} \;
find /home/ubuntu/kriangle -type f -exec chmod 640 {} \;

sudo a2ensite kriangle.conf
sudo a2dissite 000-default.conf
sudo systemctl restart apache2
```

## Testing in Production

### 1. Test Web Application
- Access through browser: http://your-ec2-public-dns/

### 2. Test Celery Tasks
```bash
# Check Celery worker status
sudo supervisorctl status kriangle_celery

# View Celery logs
tail -f /home/ubuntu/kriangle/logs/celery.log

# View Celery Beat logs (if using scheduled tasks)
tail -f /home/ubuntu/kriangle/logs/celery_beat.log
```

### 3. Test Task Execution via Django Shell
```bash
cd /home/ubuntu/kriangle
source venv/bin/activate
python manage.py shell
```
```python
from kriangle_app.tasks import test_task
result = test_task.delay("test parameter")
print(result.id)
```

## Monitoring and Scaling Celery

### 1. Install Flower for Monitoring (Optional)
```bash
pip install flower
```

Create `/etc/supervisor/conf.d/kriangle_flower.conf`:
```ini
[program:kriangle_flower]
command=/home/ubuntu/kriangle/venv/bin/celery -A kriangle flower --port=5555
directory=/home/ubuntu/kriangle
user=ubuntu
numprocs=1
stdout_logfile=/home/ubuntu/kriangle/logs/flower.log
stderr_logfile=/home/ubuntu/kriangle/logs/flower_error.log
autostart=true
autorestart=true
```

Set up Nginx to proxy Flower (with password protection):
```bash
sudo apt install -y nginx apache2-utils
sudo htpasswd -c /etc/nginx/htpasswd.users admin  # Create password for admin user

# Create Nginx config
sudo nano /etc/nginx/sites-available/flower
```

Add to the file:
```
server {
    listen 80;
    server_name flower.your-domain.com;

    location / {
        auth_basic "Restricted";
        auth_basic_user_file /etc/nginx/htpasswd.users;
        proxy_pass http://localhost:5555;
        proxy_set_header Host $host;
        proxy_redirect off;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/flower /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### 2. Scaling Celery Workers
To add more worker processes:
```bash
# Edit supervisor config
sudo nano /etc/supervisor/conf.d/kriangle_celery.conf
```

Change `numprocs=1` to a higher number, or add concurrency:
```
command=/home/ubuntu/kriangle/venv/bin/celery -A kriangle worker --loglevel=info --concurrency=4
```

Update supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart kriangle_celery
```

## Regular Maintenance

### 1. Code Updates
```bash
cd /home/ubuntu/kriangle
source venv/bin/activate

# Pull latest code
git pull

# Install any new requirements
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Collect static files if changed
python manage.py collectstatic --no-input

# Restart services
sudo systemctl restart apache2
sudo supervisorctl restart kriangle_celery
sudo supervisorctl restart kriangle_celery_beat  # If using scheduled tasks
```

### 2. Backing Up Redis Data
```bash
# Configure Redis to save data to disk
sudo nano /etc/redis/redis.conf
```

Set appropriate save parameters:
```
save 900 1
save 300 10
save 60 10000
```

```bash
# Create backup script
sudo nano /home/ubuntu/backup_redis.sh
```

Add to file:
```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/home/ubuntu/backups/redis
mkdir -p $BACKUP_DIR
redis-cli SAVE
cp /var/lib/redis/dump.rdb $BACKUP_DIR/redis_backup_$TIMESTAMP.rdb
```

Make executable and schedule:
```bash
sudo chmod +x /home/ubuntu/backup_redis.sh
crontab -e
```

Add to crontab:
```
0 2 * * * /home/ubuntu/backup_redis.sh
```

## Security Considerations

1. Set up SSL with Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-apache
sudo certbot --apache -d your-domain-name
```

2. Configure Redis Security:
   - Use strong password
   - Bind to localhost only
   - Use protected mode
   - Consider using Redis ACLs for more granular control

3. Set up regular security updates:
```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

4. Monitor system resources:
```bash
sudo apt install -y htop
```

5. Set up firewall rules:
```bash
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
``` 