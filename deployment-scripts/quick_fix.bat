@echo off
echo ====================================
echo     Off-page SEO Quick Fix Tool
echo ====================================
echo.

echo 1. Starting Django server for testing
echo.
start cmd /k "call venv\Scripts\activate && python manage.py runserver"

echo 2. Opening the Off-page SEO page in your browser
echo.
timeout /t 4
start http://127.0.0.1:8000/offpage-seo/

echo.
echo Instructions:
echo 1. Enter a website URL and keywords in the form
echo 2. Click "Start Off-Page SEO"
echo 3. You should be redirected to the results page
echo.
echo If it doesn't work, check the Django terminal for error messages
echo.
pause 