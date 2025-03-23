@echo off
echo Testing Password Reset Flow
echo ===========================
echo.
echo This script will start the Django server for testing the password reset flow
echo.
echo 1. Start your server
echo 2. Go to http://localhost:8000/login/
echo 3. Click on "Forgot password?"
echo 4. Complete the password reset process
echo.
echo Press any key to start the server...
pause > nul

python manage.py runserver 