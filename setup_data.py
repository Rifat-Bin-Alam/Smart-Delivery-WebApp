#!/usr/bin/env python
"""
Standalone script to setup SwiftDrop development database and seed accounts.
Usage: python setup_data.py
"""
import os
import sys
import django

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Nagaribashi_express.settings')
    django.setup()

    from django.core.management import call_command
    print("Applying pending database migrations...")
    call_command('migrate')

    print("Seeding SwiftDrop demo accounts & catalog data...")
    call_command('setup_data')
    print("Setup completed successfully!")

if __name__ == '__main__':
    main()
