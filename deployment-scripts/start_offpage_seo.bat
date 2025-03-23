@echo off
echo ======================================================
echo Starting Celery Worker for Off-page SEO Processing
echo ======================================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate

echo Starting Celery worker...
celery -A kriangle worker --loglevel=info

echo.
echo If there are any errors, make sure you have run setup_complete.bat first
echo ====================================================== 