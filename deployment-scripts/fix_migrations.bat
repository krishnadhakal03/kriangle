@echo off
echo ==================================================
echo Kriangle Website - Database Migration Fix
echo ==================================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate

echo Cleaning up existing database...
del db.sqlite3
del celery.sqlite
del celery-results.sqlite

echo Cleaning up existing migrations...
rmdir /s /q kriangle_app\migrations\__pycache__ 2>nul
del kriangle_app\migrations\0*.py 2>nul

echo Creating empty __init__.py in migrations folder...
echo # > kriangle_app\migrations\__init__.py

echo Creating fresh migrations...
python manage.py makemigrations kriangle_app

echo Applying migrations...
python manage.py migrate

echo Creating default superuser (admin/admin123)...
python -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else print('Admin already exists')"

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

echo ==================================================
echo Fixed! Now run 'python manage.py runserver' to start
echo ================================================== 