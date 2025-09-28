#!/usr/bin/env python
"""
Deployment script for Nagaribashi Express
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Nagaribashi_express.settings_production')
    django.setup()
    
    print("🚀 Starting deployment process...")
    
    # Collect static files
    print("📁 Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    # Run migrations
    print("🗄️ Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Create superuser if not exists
    print("👤 Creating superuser...")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@nagaribashiexpress.com', 'admin123')
            print("✅ Superuser created: admin/admin123")
        else:
            print("ℹ️ Superuser already exists")
    except Exception as e:
        print(f"⚠️ Superuser creation failed: {e}")
    
    print("✅ Deployment completed!")
    print("🌐 Your website is ready for production!")
