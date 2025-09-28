from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Setup initial data for Nagaribashi Express'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('নাগরীবাসী এক্সপ্রেস সেটআপ শুরু হচ্ছে...')
        )
        
        # Create superuser
        self.create_superuser()
        
        # Create sample data
        self.create_sample_products()
        self.create_delivery_areas()
        self.create_payment_methods()
        self.create_faqs()
        self.create_sample_users()
        
        self.stdout.write(
            self.style.SUCCESS('সেটআপ সফলভাবে সম্পন্ন হয়েছে!')
        )

    def create_superuser(self):
        """Create a superuser if it doesn't exist"""
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@nagaribashiexpress.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                phone_number='01711234567',
                user_type='admin'
            )
            self.stdout.write('Superuser created: admin/admin123')
        else:
            self.stdout.write('Superuser already exists')

    def create_sample_products(self):
        """Create sample products"""
        try:
            from orders.models import ProductService
            
            products_data = [
                {
                    'name': 'বিরিয়ানি (চিকেন)',
                    'description': 'সুস্বাদু চিকেন বিরিয়ানি - বিশেষ মসলা দিয়ে রান্না',
                    'category': 'food',
                    'price': 250.00,
                    'is_available': True
                },
                {
                    'name': 'প্যারাসিটামল ৫০০মিগ্রা',
                    'description': 'জ্বর ও ব্যথার ঔষধ - ডাক্তারের পরামর্শ অনুযায়ী সেবন করুন',
                    'category': 'medicine',
                    'price': 2.00,
                    'is_available': True
                },
                {
                    'name': 'এলপিজি গ্যাস (১২ কেজি)',
                    'description': 'রান্নার গ্যাস - নিরাপদ ডেলিভারি',
                    'category': 'gas',
                    'price': 1200.00,
                    'is_available': True
                },
                {
                    'name': 'চাল (৫ কেজি)',
                    'description': 'উচ্চমানের চাল - দৈনন্দিন রান্নার জন্য',
                    'category': 'groceries',
                    'price': 300.00,
                    'is_available': True
                },
                {
                    'name': 'স্মার্টফোন (স্যামসাং)',
                    'description': 'লেটেস্ট স্মার্টফোন - সব ফিচার সহ',
                    'category': 'electronics',
                    'price': 25000.00,
                    'is_available': True
                }
            ]
            
            for product_data in products_data:
                product, created = ProductService.objects.get_or_create(
                    name=product_data['name'],
                    defaults=product_data
                )
                if created:
                    self.stdout.write(f'Created product: {product.name}')
        except ImportError:
            self.stdout.write('Orders app not available, skipping products')

    def create_delivery_areas(self):
        """Create delivery areas"""
        try:
            from delivery.models import DeliveryArea
            
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
                }
            ]
            
            for area_data in areas_data:
                area, created = DeliveryArea.objects.get_or_create(
                    name=area_data['name'],
                    defaults=area_data
                )
                if created:
                    self.stdout.write(f'Created delivery area: {area.name}')
        except ImportError:
            self.stdout.write('Delivery app not available, skipping areas')

    def create_payment_methods(self):
        """Create payment methods"""
        try:
            from payments.models import PaymentMethod
            
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
                }
            ]
            
            for method_data in methods_data:
                method, created = PaymentMethod.objects.get_or_create(
                    code=method_data['code'],
                    defaults=method_data
                )
                if created:
                    self.stdout.write(f'Created payment method: {method.name}')
        except ImportError:
            self.stdout.write('Payments app not available, skipping methods')

    def create_faqs(self):
        """Create FAQ entries"""
        try:
            from dashboard.models import FAQ
            
            faqs_data = [
                {
                    'question': 'কিভাবে অর্ডার দেব?',
                    'answer': 'আপনি আমাদের ওয়েবসাইটে গিয়ে পছন্দের পণ্য নির্বাচন করে অর্ডার দিতে পারেন।',
                    'category': 'general',
                    'is_active': True,
                    'order': 1
                },
                {
                    'question': 'ডেলিভারি চার্জ কত?',
                    'answer': 'ডেলিভারি চার্জ এলাকা ভেদে ৪৫-৭০ টাকা।',
                    'category': 'delivery',
                    'is_active': True,
                    'order': 2
                }
            ]
            
            for faq_data in faqs_data:
                faq, created = FAQ.objects.get_or_create(
                    question=faq_data['question'],
                    defaults=faq_data
                )
                if created:
                    self.stdout.write(f'Created FAQ: {faq.question}')
        except ImportError:
            self.stdout.write('Dashboard app not available, skipping FAQs')

    def create_sample_users(self):
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
            }
        ]
        
        for user_data in users_data:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(**user_data)
                self.stdout.write(f'Created user: {user.username}')
