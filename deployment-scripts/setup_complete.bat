@echo off
echo ==================================================
echo Kriangle Website Setup - Complete Installation
echo ==================================================
echo.

REM Delete existing database files 
echo Cleaning up existing database files...
del db.sqlite3 2>nul
del celery.sqlite 2>nul
del celery-results.sqlite 2>nul
rmdir /s /q kriangle_app\migrations\__pycache__ 2>nul
del kriangle_app\migrations\0*.py 2>nul

REM Keep only __init__.py in migrations folder
if not exist kriangle_app\migrations\__init__.py (
    echo # > kriangle_app\migrations\__init__.py
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pillow
python -m pip install reportlab

REM Create necessary directories
echo Creating media directories...
mkdir media 2>nul
mkdir media\blog 2>nul
mkdir media\blog\featured_images 2>nul
mkdir media\uploads 2>nul
mkdir staticfiles 2>nul

REM Make and apply migrations
echo Running database migrations...
python manage.py makemigrations kriangle_app
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Migrations creation may have issues.
)

python manage.py migrate
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Migration application may have issues.
)

REM Create a superuser if one doesn't exist
echo Checking for superuser...
python -c "from django.contrib.auth.models import User; print('Superuser exists') if User.objects.filter(is_superuser=True).exists() else exit(1)" > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Creating a default superuser (admin/admin123)...
    python -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else print('Admin already exists')"
)

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Static files collection may have issues.
)

REM Create sample blog data
echo Creating sample blog data...
python -c "
from django.contrib.auth.models import User;
from kriangle_app.models import BlogCategory, Tag, BlogPost;
from django.utils import timezone;

# Create a default category if none exists
if not BlogCategory.objects.exists():
    default_category = BlogCategory.objects.create(name='Website Development', slug='website-development', description='Articles about website development and best practices')
    print('Created default blog category')

# Create some tags if none exist
if not Tag.objects.exists():
    tags = ['SEO', 'Web Development', 'Python', 'Django']
    for tag_name in tags:
        Tag.objects.create(name=tag_name)
    print('Created default tags')

# Create a sample blog post if none exists
if not BlogPost.objects.exists():
    admin = User.objects.filter(is_superuser=True).first()
    category = BlogCategory.objects.first()
    post = BlogPost.objects.create(
        title='Welcome to Kriangle Blog',
        slug='welcome-to-kriangle-blog',
        category=category,
        summary='This is our first blog post introducing Kriangle services and features.',
        content='<h2>Welcome to Kriangle</h2><p>We are excited to launch our blog where we will share insights about website development, SEO strategies, and tips to improve your online presence.</p><p>Stay tuned for regular updates and valuable information that can help your business grow.</p>',
        author=admin,
        is_published=True,
        published_at=timezone.now()
    )
    # Add tags to the post
    post.tags.add(*Tag.objects.all()[:3])
    print('Created sample blog post')
"

echo.
echo ==================================================
echo Setup complete! Starting the development server...
echo ==================================================
echo.
echo Access the site at: http://127.0.0.1:8000/
echo Admin panel at: http://127.0.0.1:8000/admin/
echo Login with: admin / admin123
echo.
echo Press Ctrl+C to stop the server when finished.
echo.

REM Start the development server
python manage.py runserver 