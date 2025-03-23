@echo off
echo Making migrations for model changes...
python manage.py makemigrations

echo Applying migrations...
python manage.py migrate

echo Migration complete!
pause 