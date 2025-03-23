@echo off
echo ======================================================
echo Creating Django Admin Superuser
echo ======================================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate

echo Creating superuser...
python manage.py createsuperuser

echo.
echo If successful, use these credentials to log in at:
echo http://127.0.0.1:8000/admin/
echo ======================================================
pause 