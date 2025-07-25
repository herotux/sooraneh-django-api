#!/bin/bash
echo "📦 در حال راه‌اندازی پروژه Sooraneh..."


source .venv/bin/activate

pip install -r requirements.txt

cd sooraneh_django_api

python manage.py makemigrations
python manage.py migrate

echo "from users.models import User; User.objects.create_superuser('admin', 'admin@sooraneh.com', 'admin123')" | python manage.py shell

echo "✅ پروژه با موفقیت راه‌اندازی شد!"
echo "🔧 برای اجرا: source venv/bin/activate && python manage.py runserver"
echo "🌐 Swagger: http://localhost:8000/swagger/"
