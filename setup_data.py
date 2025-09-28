#!/usr/bin/env python
"""
Setup script for Nagaribashi Express
This script creates initial data for the application
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Nagaribashi_express.settings')
django.setup()

from django.contrib.auth import get_user_model
from orders.models import ProductService, DeliveryArea
from payments.models import PaymentMethod
from dashboard.models import FAQ

User = get_user_model()


def create_superuser():
    """Create a superuser if it doesn't exist"""
    if not User.objects.filter(is_superuser=True).exists():
        print("Creating superuser...")
        User.objects.create_superuser(
            username='admin',
            email='admin@nagaribashiexpress.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            phone_number='01711234567',
            user_type='admin'
        )
        print("Superuser created successfully!")
        print("Username: admin")
        print("Password: admin123")
    else:
        print("Superuser already exists!")


def create_sample_products():
    """Create sample products"""
    products_data = [
        {
            'name': 'বিরিয়ানি (চিকেন)',
            'description': 'সুস্বাদু চিকেন বিরিয়ানি - বিশেষ মসলা দিয়ে রান্না',
            'category': 'food',
            'price': 250.00,
            'is_available': True,
            'stock_quantity': 50
        },
        {
            'name': 'প্যারাসিটামল ৫০০মিগ্রা',
            'description': 'জ্বর ও ব্যথার ঔষধ - ডাক্তারের পরামর্শ অনুযায়ী সেবন করুন',
            'category': 'medicine',
            'price': 2.00,
            'is_available': True,
            'stock_quantity': 100
        },
        {
            'name': 'এলপিজি গ্যাস (১২ কেজি)',
            'description': 'রান্নার গ্যাস - নিরাপদ ডেলিভারি',
            'category': 'gas',
            'price': 1200.00,
            'is_available': True,
            'stock_quantity': 20
        },
        {
            'name': 'চাল (৫ কেজি)',
            'description': 'উচ্চমানের চাল - দৈনন্দিন রান্নার জন্য',
            'category': 'groceries',
            'price': 300.00,
            'is_available': True,
            'stock_quantity': 30
        },
        {
            'name': 'স্মার্টফোন (স্যামসাং)',
            'description': 'লেটেস্ট স্মার্টফোন - সব ফিচার সহ',
            'category': 'electronics',
            'price': 25000.00,
            'is_available': True,
            'stock_quantity': 5
        },
        {
            'name': 'শার্ট (কটন)',
            'description': 'সুতি শার্ট - আরামদায়ক ও টেকসই',
            'category': 'clothing',
            'price': 800.00,
            'is_available': True,
            'stock_quantity': 25
        },
        {
            'name': 'বাংলা সাহিত্য বই',
            'description': 'ক্লাসিক বাংলা সাহিত্যের সংগ্রহ',
            'category': 'books',
            'price': 150.00,
            'is_available': True,
            'stock_quantity': 40
        },
        {
            'name': 'পিজা (মিডিয়াম)',
            'description': 'চিজ পিজা - গরম গরম ডেলিভারি',
            'category': 'food',
            'price': 400.00,
            'is_available': True,
            'stock_quantity': 15
        },
        {
            'name': 'ভিটামিন সি',
            'description': 'ইমিউনিটি বুস্টার - স্বাস্থ্যের জন্য উপকারী',
            'category': 'medicine',
            'price': 50.00,
            'is_available': True,
            'stock_quantity': 75
        },
        {
            'name': 'ডিম (১২ পিস)',
            'description': 'তাজা ডিম - প্রোটিনের ভালো উৎস',
            'category': 'groceries',
            'price': 120.00,
            'is_available': True,
            'stock_quantity': 60
        }
    ]
    
    print("Creating sample products...")
    for product_data in products_data:
        product, created = ProductService.objects.get_or_create(
            name=product_data['name'],
            defaults=product_data
        )
        if created:
            print(f"Created product: {product.name}")
        else:
            print(f"Product already exists: {product.name}")


def create_delivery_areas():
    """Create delivery areas"""
    areas_data = [
        {
            'name': 'ধানমন্ডি',
            'description': 'ধানমন্ডি এলাকা - কেন্দ্রীয় ঢাকা',
            'delivery_fee': 50.00,
            'estimated_delivery_time': 30,
            'is_active': True
        },
        {
            'name': 'গুলশান',
            'description': 'গুলশান এলাকা - উত্তর ঢাকা',
            'delivery_fee': 60.00,
            'estimated_delivery_time': 35,
            'is_active': True
        },
        {
            'name': 'বনানী',
            'description': 'বনানী এলাকা - উত্তর ঢাকা',
            'delivery_fee': 55.00,
            'estimated_delivery_time': 32,
            'is_active': True
        },
        {
            'name': 'মিরপুর',
            'description': 'মিরপুর এলাকা - পশ্চিম ঢাকা',
            'delivery_fee': 70.00,
            'estimated_delivery_time': 40,
            'is_active': True
        },
        {
            'name': 'মোহাম্মদপুর',
            'description': 'মোহাম্মদপুর এলাকা - দক্ষিণ ঢাকা',
            'delivery_fee': 45.00,
            'estimated_delivery_time': 25,
            'is_active': True
        }
    ]
    
    print("Creating delivery areas...")
    for area_data in areas_data:
        area, created = DeliveryArea.objects.get_or_create(
            name=area_data['name'],
            defaults=area_data
        )
        if created:
            print(f"Created delivery area: {area.name}")
        else:
            print(f"Delivery area already exists: {area.name}")


def create_payment_methods():
    """Create payment methods"""
    methods_data = [
        {
            'name': 'ক্যাশ অন ডেলিভারি',
            'code': 'cash_on_delivery',
            'description': 'ডেলিভারির সময় নগদ পেমেন্ট',
            'is_active': True,
            'processing_fee': 0.00,
            'min_amount': 0.00
        },
        {
            'name': 'bKash',
            'code': 'bkash',
            'description': 'bKash মোবাইল ব্যাংকিং',
            'is_active': True,
            'processing_fee': 5.00,
            'min_amount': 10.00
        },
        {
            'name': 'Nagad',
            'code': 'nagad',
            'description': 'Nagad মোবাইল ব্যাংকিং',
            'is_active': True,
            'processing_fee': 5.00,
            'min_amount': 10.00
        },
        {
            'name': 'Rocket',
            'code': 'rocket',
            'description': 'Rocket মোবাইল ব্যাংকিং',
            'is_active': True,
            'processing_fee': 5.00,
            'min_amount': 10.00
        },
        {
            'name': 'ব্যাংক ট্রান্সফার',
            'code': 'bank_transfer',
            'description': 'ব্যাংক ট্রান্সফার',
            'is_active': True,
            'processing_fee': 10.00,
            'min_amount': 100.00
        }
    ]
    
    print("Creating payment methods...")
    for method_data in methods_data:
        method, created = PaymentMethod.objects.get_or_create(
            code=method_data['code'],
            defaults=method_data
        )
        if created:
            print(f"Created payment method: {method.name}")
        else:
            print(f"Payment method already exists: {method.name}")


def create_faqs():
    """Create FAQ entries"""
    faqs_data = [
        {
            'question': 'কিভাবে অর্ডার দেব?',
            'answer': 'আপনি আমাদের ওয়েবসাইটে গিয়ে পছন্দের পণ্য নির্বাচন করে অর্ডার দিতে পারেন। অর্ডার দেওয়ার পর আপনি পেমেন্ট করতে পারবেন।',
            'category': 'general',
            'is_active': True,
            'order': 1
        },
        {
            'question': 'ডেলিভারি চার্জ কত?',
            'answer': 'ডেলিভারি চার্জ এলাকা ভেদে ৪৫-৭০ টাকা। আপনি অর্ডার দেওয়ার সময় সঠিক চার্জ দেখতে পাবেন।',
            'category': 'delivery',
            'is_active': True,
            'order': 2
        },
        {
            'question': 'কত সময়ে ডেলিভারি পাব?',
            'answer': 'সাধারণত ২৫-৪০ মিনিটের মধ্যে ডেলিভারি হয়ে থাকে। এলাকা ভেদে সময় পরিবর্তন হতে পারে।',
            'category': 'delivery',
            'is_active': True,
            'order': 3
        },
        {
            'question': 'কোন পেমেন্ট পদ্ধতি গ্রহণ করা হয়?',
            'answer': 'আমরা ক্যাশ অন ডেলিভারি, bKash, Nagad, Rocket এবং ব্যাংক ট্রান্সফার গ্রহণ করি।',
            'category': 'payment',
            'is_active': True,
            'order': 4
        },
        {
            'question': 'অর্ডার বাতিল করতে পারি?',
            'answer': 'হ্যাঁ, ডেলিভারি শুরুর আগে আপনি অর্ডার বাতিল করতে পারবেন।',
            'category': 'orders',
            'is_active': True,
            'order': 5
        },
        {
            'question': 'রিফান্ড পাব কখন?',
            'answer': 'অনলাইন পেমেন্টের ক্ষেত্রে ৩-৫ কার্যদিবসে এবং ক্যাশ পেমেন্টের ক্ষেত্রে পরবর্তী ডেলিভারিতে রিফান্ড দেওয়া হয়।',
            'category': 'payment',
            'is_active': True,
            'order': 6
        }
    ]
    
    print("Creating FAQs...")
    for faq_data in faqs_data:
        faq, created = FAQ.objects.get_or_create(
            question=faq_data['question'],
            defaults=faq_data
        )
        if created:
            print(f"Created FAQ: {faq.question}")
        else:
            print(f"FAQ already exists: {faq.question}")


def create_sample_users():
    """Create sample users"""
    users_data = [
        {
            'username': 'customer1',
            'email': 'customer1@example.com',
            'password': 'customer123',
            'first_name': 'রহিম',
            'last_name': 'আহমেদ',
            'phone_number': '01712345678',
            'user_type': 'customer',
            'address': 'ধানমন্ডি ৮, ঢাকা',
            'city': 'ঢাকা'
        },
        {
            'username': 'delivery_agent1',
            'email': 'agent1@example.com',
            'password': 'agent123',
            'first_name': 'করিম',
            'last_name': 'উদ্দিন',
            'phone_number': '01787654321',
            'user_type': 'delivery_agent',
            'address': 'গুলশান ১, ঢাকা',
            'city': 'ঢাকা'
        }
    ]
    
    print("Creating sample users...")
    for user_data in users_data:
        if not User.objects.filter(username=user_data['username']).exists():
            user = User.objects.create_user(**user_data)
            print(f"Created user: {user.username}")
        else:
            print(f"User already exists: {user_data['username']}")


def main():
    """Main setup function"""
    print("=" * 50)
    print("নগরবাসী এক্সপ্রেস সেটআপ শুরু হচ্ছে...")
    print("=" * 50)
    
    try:
        create_superuser()
        print()
        
        create_sample_products()
        print()
        
        create_delivery_areas()
        print()
        
        create_payment_methods()
        print()
        
        create_faqs()
        print()
        
        create_sample_users()
        print()
        
        print("=" * 50)
        print("সেটআপ সফলভাবে সম্পন্ন হয়েছে!")
        print("=" * 50)
        print()
        print("অ্যাডমিন প্যানেলে প্রবেশ করুন:")
        print("URL: http://127.0.0.1:8000/admin/")
        print("Username: admin")
        print("Password: admin123")
        print()
        print("হোম পেজ দেখুন:")
        print("URL: http://127.0.0.1:8000/")
        print()
        print("সার্ভার চালু করতে:")
        print("python manage.py runserver")
        
    except Exception as e:
        print(f"Error during setup: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
