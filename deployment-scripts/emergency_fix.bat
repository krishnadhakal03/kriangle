@echo off
echo ==================================================
echo Kriangle Website - EMERGENCY DATABASE FIX
echo ==================================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate 2>nul

echo Installing Pillow required for image handling...
pip install Pillow

echo Adding missing tables and columns to database using direct SQL...

echo import sqlite3; > fix_sql.py
echo conn = sqlite3.connect('db.sqlite3'); >> fix_sql.py
echo cursor = conn.cursor(); >> fix_sql.py
echo. >> fix_sql.py
echo print("Checking if BlogPost table exists..."); >> fix_sql.py
echo cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kriangle_app_blogpost'"); >> fix_sql.py
echo if not cursor.fetchone(): >> fix_sql.py
echo     print("BlogPost table does not exist! Creating it..."); >> fix_sql.py
echo     cursor.execute("CREATE TABLE kriangle_app_blogpost (id INTEGER PRIMARY KEY, title TEXT, slug TEXT UNIQUE, summary TEXT, content TEXT, meta_title TEXT, meta_description TEXT, created_at TIMESTAMP, updated_at TIMESTAMP, is_published BOOLEAN, published_at TIMESTAMP, view_count INTEGER, category_id INTEGER, author_id INTEGER)"); >> fix_sql.py
echo     cursor.execute("INSERT INTO kriangle_app_blogpost (title, slug, summary, content, is_published, view_count) VALUES ('Welcome to Kriangle Blog', 'welcome-to-kriangle', 'This is our first blog post.', '<h2>Welcome to Kriangle</h2><p>We are excited to launch our blog.</p>', 1, 0)"); >> fix_sql.py
echo     print("Created sample blog post"); >> fix_sql.py
echo else: >> fix_sql.py
echo     print("Table exists, checking columns..."); >> fix_sql.py
echo     cursor.execute("PRAGMA table_info(kriangle_app_blogpost)"); >> fix_sql.py
echo     columns = [col[1] for col in cursor.fetchall()]; >> fix_sql.py
echo     if "slug" not in columns: >> fix_sql.py
echo         print("Adding slug column..."); >> fix_sql.py
echo         cursor.execute("ALTER TABLE kriangle_app_blogpost ADD COLUMN slug TEXT UNIQUE"); >> fix_sql.py
echo         cursor.execute("UPDATE kriangle_app_blogpost SET slug = 'post-' || id WHERE slug IS NULL"); >> fix_sql.py
echo         print("Added slug column and set default values"); >> fix_sql.py
echo     else: >> fix_sql.py
echo         print("Slug column already exists"); >> fix_sql.py
echo. >> fix_sql.py

echo print("Checking if OldBlogPost table exists..."); >> fix_sql.py
echo cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kriangle_app_oldblogpost'"); >> fix_sql.py
echo if not cursor.fetchone(): >> fix_sql.py
echo     print("OldBlogPost table does not exist! Creating it..."); >> fix_sql.py
echo     cursor.execute("CREATE TABLE kriangle_app_oldblogpost (id INTEGER PRIMARY KEY, title TEXT, content TEXT, url TEXT, created_at TIMESTAMP, job_id INTEGER, FOREIGN KEY (job_id) REFERENCES kriangle_app_seojob(id))"); >> fix_sql.py
echo     print("Created OldBlogPost table"); >> fix_sql.py
echo else: >> fix_sql.py
echo     print("OldBlogPost table already exists"); >> fix_sql.py
echo. >> fix_sql.py

echo print("Checking if SEOJob table exists..."); >> fix_sql.py
echo cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kriangle_app_seojob'"); >> fix_sql.py
echo if not cursor.fetchone(): >> fix_sql.py
echo     print("SEOJob table does not exist! Creating it..."); >> fix_sql.py
echo     cursor.execute("CREATE TABLE kriangle_app_seojob (id INTEGER PRIMARY KEY, url TEXT, keywords TEXT, created_at TIMESTAMP, status TEXT)"); >> fix_sql.py
echo     print("Created SEOJob table"); >> fix_sql.py
echo else: >> fix_sql.py
echo     print("SEOJob table already exists"); >> fix_sql.py
echo. >> fix_sql.py

echo print("Checking if SEOResult table exists..."); >> fix_sql.py
echo cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kriangle_app_seoresult'"); >> fix_sql.py
echo if not cursor.fetchone(): >> fix_sql.py
echo     print("SEOResult table does not exist! Creating it..."); >> fix_sql.py
echo     cursor.execute("CREATE TABLE kriangle_app_seoresult (id INTEGER PRIMARY KEY, step TEXT, result_data TEXT, status TEXT, created_at TIMESTAMP, job_id INTEGER, FOREIGN KEY (job_id) REFERENCES kriangle_app_seojob(id))"); >> fix_sql.py
echo     print("Created SEOResult table"); >> fix_sql.py
echo else: >> fix_sql.py
echo     print("SEOResult table already exists"); >> fix_sql.py
echo. >> fix_sql.py

echo print("Checking if OffPageSEOAction table exists..."); >> fix_sql.py
echo cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kriangle_app_offpageseoaction'"); >> fix_sql.py
echo if not cursor.fetchone(): >> fix_sql.py
echo     print("OffPageSEOAction table does not exist! Creating it..."); >> fix_sql.py
echo     cursor.execute("CREATE TABLE kriangle_app_offpageseoaction (id INTEGER PRIMARY KEY, action_type TEXT, platform TEXT, url TEXT, status TEXT, created_at TIMESTAMP, job_id INTEGER, FOREIGN KEY (job_id) REFERENCES kriangle_app_seojob(id))"); >> fix_sql.py
echo     print("Created OffPageSEOAction table"); >> fix_sql.py
echo else: >> fix_sql.py
echo     print("OffPageSEOAction table already exists"); >> fix_sql.py
echo. >> fix_sql.py

echo conn.commit(); >> fix_sql.py
echo conn.close(); >> fix_sql.py
echo print("Database fix complete!"); >> fix_sql.py

python fix_sql.py

echo.
echo ==================================================
echo Creating sample blog entries for testing...
echo ==================================================

echo import django >> create_sample_blog.py
echo import os >> create_sample_blog.py
echo from django.utils import timezone >> create_sample_blog.py
echo os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kriangle.settings') >> create_sample_blog.py
echo django.setup() >> create_sample_blog.py
echo. >> create_sample_blog.py
echo from django.contrib.auth.models import User >> create_sample_blog.py
echo from kriangle_app.models import BlogCategory, Tag, BlogPost >> create_sample_blog.py
echo. >> create_sample_blog.py
echo print("Creating sample blog data...") >> create_sample_blog.py
echo. >> create_sample_blog.py
echo # Create a default category if none exists >> create_sample_blog.py
echo if not BlogCategory.objects.exists(): >> create_sample_blog.py
echo     default_category = BlogCategory.objects.create(name='Website Development', slug='website-development', description='Articles about website development and best practices') >> create_sample_blog.py
echo     print('Created default blog category') >> create_sample_blog.py
echo else: >> create_sample_blog.py
echo     default_category = BlogCategory.objects.first() >> create_sample_blog.py
echo     print('Using existing category:', default_category) >> create_sample_blog.py
echo. >> create_sample_blog.py
echo # Create some tags if none exist >> create_sample_blog.py
echo if not Tag.objects.exists(): >> create_sample_blog.py
echo     tags = ['SEO', 'Web Development', 'Python', 'Django'] >> create_sample_blog.py
echo     for tag_name in tags: >> create_sample_blog.py
echo         Tag.objects.create(name=tag_name) >> create_sample_blog.py
echo     print('Created default tags') >> create_sample_blog.py
echo. >> create_sample_blog.py
echo # Get or create admin user >> create_sample_blog.py
echo admin_user = User.objects.filter(is_superuser=True).first() >> create_sample_blog.py
echo if not admin_user: >> create_sample_blog.py
echo     admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123') >> create_sample_blog.py
echo     print('Created admin user') >> create_sample_blog.py
echo. >> create_sample_blog.py
echo # Create a sample blog post if none exists >> create_sample_blog.py
echo if BlogPost.objects.count() < 3: >> create_sample_blog.py
echo     for i in range(1, 4): >> create_sample_blog.py
echo         if not BlogPost.objects.filter(title=f'Sample Blog Post {i}').exists(): >> create_sample_blog.py
echo             post = BlogPost.objects.create( >> create_sample_blog.py
echo                 title=f'Sample Blog Post {i}', >> create_sample_blog.py
echo                 slug=f'sample-blog-post-{i}', >> create_sample_blog.py
echo                 category=default_category, >> create_sample_blog.py
echo                 summary=f'This is sample blog post {i} for testing.', >> create_sample_blog.py
echo                 content=f'<h2>Sample Post {i}</h2><p>This is a sample post created for testing the blog functionality. It includes some basic content to demonstrate how posts are displayed.</p>', >> create_sample_blog.py
echo                 author=admin_user, >> create_sample_blog.py
echo                 is_published=True, >> create_sample_blog.py
echo                 published_at=timezone.now(), >> create_sample_blog.py
echo                 view_count=i*10 >> create_sample_blog.py
echo             ) >> create_sample_blog.py
echo             # Add tags to the post >> create_sample_blog.py
echo             for tag in Tag.objects.all()[:2]: >> create_sample_blog.py
echo                 post.tags.add(tag) >> create_sample_blog.py
echo             print(f'Created sample blog post {i}') >> create_sample_blog.py
echo print('Done creating sample blog content!') >> create_sample_blog.py

python create_sample_blog.py

echo.
echo ==================================================
echo Fix completed! Now run the website with:
echo python manage.py runserver
echo ================================================== 