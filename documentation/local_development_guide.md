# Kriangle: Local Development Setup Guide

## Initial Setup

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd kriangle-master

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Apply migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser
```

## Setting Up Celery

### Option 1: Using Redis (Recommended)
1. Install Redis:
   - **Windows**: Download and install from [Redis for Windows](https://github.com/tporadowski/redis/releases)
   - **macOS**: `brew install redis && brew services start redis`
   - **Linux**: `sudo apt install redis-server && sudo systemctl start redis-server`

2. Run Redis server:
   - **Windows**: `redis-server`
   - **macOS/Linux**: Redis should be running as a service

3. Configure Celery in settings.py:
```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
```

### Option 2: Using SQLite (Alternative for local development)
1. Install required packages:
```bash
pip install sqlalchemy psycopg2-binary
```

2. Configure Celery in settings.py:
```python
CELERY_BROKER_URL = 'sqla+sqlite:///celery.sqlite'
CELERY_RESULT_BACKEND = 'db+sqlite:///celery-results.sqlite'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
```

### Option 3: Using Django ORM (Simplest option)
1. Install required packages:
```bash
pip install django-celery-results django-celery-beat
```

2. Add to INSTALLED_APPS in settings.py:
```python
INSTALLED_APPS = [
    # ...
    'django_celery_results',
    'django_celery_beat',
]
```

3. Configure Celery in settings.py:
```python
CELERY_BROKER_URL = 'django-db://'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
```

4. Apply migrations:
```bash
python manage.py migrate
```

### Option 4: Running Without Celery (For testing only)
If you're having permission issues or trouble setting up Celery, you can temporarily modify the views to run tasks synchronously:

1. Edit the view (e.g., in `kriangle_app/views.py`):
```python
# Instead of:
# task.delay(parameters)

# Run the task function directly:
from .tasks import task_function
task_function(parameters)
```

## Running the Application

### 1. Start Django Development Server
```bash
python manage.py runserver
```
Access at http://localhost:8000/

### 2. Start Celery Worker (Skip this if using Option 4)
```bash
# In a new terminal window (with virtual environment activated)
celery -A kriangle worker --loglevel=info
```

## Testing

### 1. Test Django Application
```bash
python manage.py test
```

### 2. Test Celery Tasks
```python
# In Django shell: python manage.py shell
from kriangle_app.tasks import your_task_name
result = your_task_name.delay(param1, param2)
print(result.id)  # Task ID
```

### 3. Monitor Celery Tasks (Optional)
```bash
# Install and run Flower
pip install flower
celery -A kriangle flower
```
Access at http://localhost:5555/

## Common Development Commands

### Generate Static Files
```bash
python manage.py collectstatic
```

### Create Migrations
```bash
python manage.py makemigrations
```

### Run Shell
```bash
python manage.py shell
```

### Check for Issues
```bash
python manage.py check
```

## Troubleshooting

### Permission Issues on Windows
If you encounter `PermissionError: [WinError 5] Access is denied` when running Celery:

1. **Run as Administrator**: Try running your command prompt or PowerShell as Administrator

2. **Check File Permissions**: Ensure your user has full permissions to the project directory

3. **Use Process Monitor**: To identify which file is causing permission issues

4. **Disable Anti-virus/Firewall**: Temporarily disable to see if it's blocking the processes

5. **Synchronous Testing**: Use Option 4 above to test without Celery

### Redis Connection Issues
- Verify Redis is running: `redis-cli ping` should return `PONG`
- Check Redis URL in settings
- Try a different port if 6379 is in use

### Celery Worker Issues
- Verify virtual environment is activated
- Check for Django settings module errors
- Verify task discovery is working

### Django Development Server Issues
- Check for error messages in the console
- Verify database connection
- Check port availability 