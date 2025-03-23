# Kriangle Website - Running Instructions

## Setup Instructions

I've created a comprehensive setup script that will automatically configure everything for you. Just follow these steps:

1. **Run the setup script**:
   - Double-click `setup_complete.bat` in the main project directory
   - This script will:
     - Create/activate the virtual environment
     - Install all required dependencies
     - Create necessary directories
     - Set up the database
     - Create a default admin user
     - Generate sample blog content
     - Start the development server

2. **Access the site**:
   - Open your browser and go to http://127.0.0.1:8000/
   - The admin panel is at http://127.0.0.1:8000/admin/
   - Login with username: `admin` and password: `admin123`

## Using the Off-page SEO Feature

The Off-page SEO feature requires a Celery worker to process tasks in the background. To use this feature:

1. **Start the Django server** (if not already running):
   - Run `python manage.py runserver`

2. **Start the Celery worker**:
   - Open a new command prompt window
   - Run the `start_offpage_seo.bat` script
   - Keep this window open while using the Off-page SEO feature

3. **Use the Off-page SEO feature**:
   - Go to http://127.0.0.1:8000/offpageseo/
   - Enter a website URL and keywords
   - Click "Start Off-Page SEO"
   - View the results on the results page

## Features Implemented

1. **Blog System**:
   - Dynamic blog posts with categories and tags
   - Individual post pages
   - Category and tag filtering
   - Related posts feature
   - View counting

2. **SEO Optimization**:
   - Meta tags for all pages
   - Structured data with JSON-LD
   - SEO-friendly URLs
   - Optimized content structure
   - SEO scanning tool

3. **Responsive Design**:
   - Mobile-friendly layouts
   - Modern UI components
   - Professional styling

## Common Issues and Solutions

If you encounter any issues:

1. **Database migration errors**:
   - Delete the `db.sqlite3` file
   - Run the setup script again
   
   OR
   
   - **If you see the "no such column: kriangle_app_blogpost.slug" error**:
     - Run the `emergency_fix.bat` script which will:
       - Add the missing slug column directly to the database
       - Set default values for existing blog posts
       - Create sample blog content for testing
     - This is the quickest and most reliable fix for database schema issues
   
   - **If you see the "no such table: kriangle_app_oldblogpost" error**:
     - This happens when trying to use the Off-page SEO feature
     - Run the `emergency_fix.bat` script which will also:
       - Create the missing OldBlogPost table
       - Fix other database schema issues

   - **If you see "Reverse for 'offpage_seo' not found" error**:
     - This is fixed in the latest code update
     - Make sure you're using the latest version of the code
     - The correct URL name is 'offpageseo' (with no underscore)
     - The Off-page SEO feature is accessible at http://127.0.0.1:8000/offpageseo/

   - **If the Off-page SEO functionality is not working**:
     - Make sure you're running the Celery worker using `start_offpage_seo.bat`
     - Check that the form action is set to `{% url 'offpageseo' %}` in the template
     - Ensure all database tables are created properly using `emergency_fix.bat`

2. **Missing static files**:
   - Run `python manage.py collectstatic --noinput`

3. **Celery errors**:
   - Start Celery separately with `start_offpage_seo.bat`
   - If you get SQLite errors, try deleting the celery.sqlite file and restarting

## Next Steps

1. **Add more blog content**:
   - Use the admin panel to add categories, tags, and posts
   - Upload featured images for posts

2. **Customize styling**:
   - Edit the CSS in `kriangle_app/static/css/`

3. **Deploy to production**:
   - Configure a proper database (PostgreSQL recommended)
   - Set up proper static file serving
   - Use a production-ready web server (Gunicorn, uWSGI)
   - Set DEBUG=False in settings.py 