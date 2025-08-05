#!/bin/bash

# Script to start Django development server
# This script will activate the virtual environment and start Django

echo "🚀 Starting AI Report Writer Django Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements if needed
if [ ! -f "venv/lib/python*/site-packages/django" ]; then
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
fi

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser if needed
if [ ! -f "superuser_created" ]; then
    echo "👤 Creating superuser..."
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell
    touch superuser_created
    echo "✅ Superuser created: admin/admin123"
fi

# Start Django development server
echo "🌐 Starting Django development server..."
echo "📍 Server will be available at: http://127.0.0.1:8000"
echo "👤 Admin login: admin/admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python manage.py runserver 127.0.0.1:8000 