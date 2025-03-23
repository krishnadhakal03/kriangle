@echo off
echo ==================================================
echo Kriangle Website - Test Mode
echo ==================================================
echo.

echo Running emergency database fix...
call emergency_fix.bat

echo.
echo ==================================================
echo Starting Django development server...
echo ==================================================
start cmd /k "call venv\Scripts\activate && python manage.py runserver"

echo.
echo ==================================================
echo Starting Celery worker for background tasks...
echo ==================================================
start cmd /k "call venv\Scripts\activate && celery -A kriangle worker --loglevel=info"

echo.
echo ==================================================
echo Kriangle website is now running!
echo.
echo * Website: http://127.0.0.1:8000/
echo * Admin: http://127.0.0.1:8000/admin/ (admin/admin123)
echo * Blog: http://127.0.0.1:8000/blog/
echo * Off-Page SEO: http://127.0.0.1:8000/offpageseo/
echo ================================================== 