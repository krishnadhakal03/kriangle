@echo off
echo Setting up Kriangle site...

REM Create necessary directories
mkdir media 2>nul
mkdir media\blog 2>nul
mkdir media\blog\featured_images 2>nul
mkdir media\uploads 2>nul

REM Apply migrations
python manage.py makemigrations
python manage.py migrate

REM Start the development server
echo Starting Django development server...
echo Access the site at http://127.0.0.1:8000/
python manage.py runserver 