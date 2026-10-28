#!/usr/bin/env python
"""
Deployment script for SwiftDrop
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Nagaribashi_express.settings_production')
    django.setup()
    
    print("Starting SwiftDrop deployment process...")
    
    # Collect static files
    print("Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    # Run migrations
    print("Running database migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Verify/create default admin account
    print("Checking superuser account...")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(email='rifatadmin@gmail.com').exists() and not User.objects.filter(username='rifatadmin').exists():
            admin_user = User.objects.create_superuser('rifatadmin', 'rifatadmin@gmail.com', '123456')
            admin_user.first_name = 'Rifat'
            admin_user.last_name = 'Admin'
            admin_user.user_type = 'admin'
            admin_user.is_verified = True
            admin_user.save()
            print("Superuser created: rifatadmin@gmail.com / 123456")
        else:
            print("Superuser account already exists")
    except Exception as e:
        print(f"Superuser check failed: {e}")
    
    print("Deployment completed successfully!")
    print("SwiftDrop is ready for production serving.")
