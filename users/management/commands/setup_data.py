from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Setup initial demo data for SwiftDrop delivery platform'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Initializing SwiftDrop catalog and accounts...'))

        # Seed required demo accounts
        call_command('seed_demo_accounts')

        # Create essential catalog and operational data
        self.create_sample_products()
        self.create_delivery_areas()
        self.create_payment_methods()
        self.create_faqs()

        self.stdout.write(self.style.SUCCESS('SwiftDrop data setup completed successfully!'))

    def create_sample_products(self):
        """Seed sample products with stock and English descriptions"""
        try:
            from orders.models import ProductService

            products_data = [
                {
                    'name': 'Premium Chicken Biryani Box',
                    'description': 'Fragrant basmati rice cooked with tender marinated chicken, boiled egg, and authentic spice blend.',
                    'category': 'food',
                    'price': 280.00,
                    'stock_quantity': 45,
                    'is_available': True,
                },
                {
                    'name': 'Paracetamol 500mg (Pack of 10)',
                    'description': 'Standard pain and fever relief caplets. Fast acting formula.',
                    'category': 'medicine',
                    'price': 25.00,
                    'stock_quantity': 150,
                    'is_available': True,
                },
                {
                    'name': 'LPG Cooking Gas Cylinder (12kg)',
                    'description': 'Safety-tested domestic LPG refill with doorstep connection check.',
                    'category': 'gas',
                    'price': 1350.00,
                    'stock_quantity': 20,
                    'is_available': True,
                },
                {
                    'name': 'Miniket Premium Rice (5kg Bag)',
                    'description': 'Polished long-grain aromatic rice, cleaned and dust-free.',
                    'category': 'groceries',
                    'price': 380.00,
                    'stock_quantity': 60,
                    'is_available': True,
                },
                {
                    'name': 'Organic Farm Fresh Eggs (Dozen)',
                    'description': 'Grade-A brown eggs packed fresh daily from organic poultry farms.',
                    'category': 'groceries',
                    'price': 155.00,
                    'stock_quantity': 80,
                    'is_available': True,
                },
                {
                    'name': 'Hand Sanitizer Gel (500ml)',
                    'description': '75% isopropyl alcohol hospital grade antiseptic hand rub with aloe vera.',
                    'category': 'medicine',
                    'price': 220.00,
                    'stock_quantity': 35,
                    'is_available': True,
                },
                {
                    'name': 'Wireless Fast Charging Power Bank 10,000mAh',
                    'description': 'Dual USB-C PD 20W output with digital battery indicator.',
                    'category': 'electronics',
                    'price': 1650.00,
                    'stock_quantity': 18,
                    'is_available': True,
                },
                {
                    'name': 'Pure Honey (500g Jar)',
                    'description': '100% natural Sundarban wild honey, raw and unfiltered.',
                    'category': 'groceries',
                    'price': 490.00,
                    'stock_quantity': 25,
                    'is_available': True,
                },
            ]

            for p_data in products_data:
                product, created = ProductService.objects.get_or_create(
                    name=p_data['name'],
                    defaults=p_data
                )
                if created:
                    self.stdout.write(f'  Created product: {product.name}')
                else:
                    # Update stock and category
                    for key, val in p_data.items():
                        setattr(product, key, val)
                    product.save()
        except ImportError:
            self.stdout.write('Orders app not available, skipping products')

    def create_delivery_areas(self):
        """Seed delivery zones with realistic fees and delivery turnaround"""
        try:
            from delivery.models import DeliveryArea

            areas_data = [
                {
                    'name': 'Dhanmondi & Lalmatia',
                    'description': 'Central Dhaka zone covering Dhanmondi 1-32, Shankar, and Lalmatia.',
                    'delivery_fee': 40.00,
                    'estimated_delivery_time': 25,
                    'is_active': True,
                },
                {
                    'name': 'Gulshan & Banani',
                    'description': 'North Dhaka prime zone covering Gulshan 1-2, Banani, and Baridhara.',
                    'delivery_fee': 60.00,
                    'estimated_delivery_time': 30,
                    'is_active': True,
                },
                {
                    'name': 'Uttara Express Zone',
                    'description': 'Uttara Sectors 1 through 14 with dedicated motorcycle fleet.',
                    'delivery_fee': 70.00,
                    'estimated_delivery_time': 35,
                    'is_active': True,
                },
                {
                    'name': 'Mirpur Central',
                    'description': 'Mirpur 1, 2, 6, 10, 11, 12 and Pallabi delivery corridor.',
                    'delivery_fee': 50.00,
                    'estimated_delivery_time': 30,
                    'is_active': True,
                },
                {
                    'name': 'Mohakhali & Tejgaon',
                    'description': 'Tejgaon Industrial Area, Mohakhali DOHS, and Niketan.',
                    'delivery_fee': 45.00,
                    'estimated_delivery_time': 25,
                    'is_active': True,
                },
            ]

            for a_data in areas_data:
                area, created = DeliveryArea.objects.get_or_create(
                    name=a_data['name'],
                    defaults=a_data
                )
                if created:
                    self.stdout.write(f'  Created delivery area: {area.name}')
                else:
                    for key, val in a_data.items():
                        setattr(area, key, val)
                    area.save()
        except ImportError:
            self.stdout.write('Delivery app not available, skipping areas')

    def create_payment_methods(self):
        """Seed payment methods supported by SwiftDrop"""
        try:
            from payments.models import PaymentMethod

            methods_data = [
                {
                    'name': 'Cash on Delivery',
                    'code': 'cash_on_delivery',
                    'description': 'Pay cash directly to the delivery rider upon receiving your package.',
                    'is_active': True,
                    'processing_fee': 0.00,
                    'min_amount': 0.00,
                },
                {
                    'name': 'bKash Mobile Wallet',
                    'code': 'bkash',
                    'description': 'Pay securely with bKash merchant/sandbox payment.',
                    'is_active': True,
                    'processing_fee': 0.00,
                    'min_amount': 10.00,
                },
                {
                    'name': 'Nagad Digital Payment',
                    'code': 'nagad',
                    'description': 'Instant wallet transaction using Nagad mobile account.',
                    'is_active': True,
                    'processing_fee': 0.00,
                    'min_amount': 10.00,
                },
                {
                    'name': 'Rocket (DBBL)',
                    'code': 'rocket',
                    'description': 'Dutch-Bangla Bank Rocket mobile financial service.',
                    'is_active': True,
                    'processing_fee': 0.00,
                    'min_amount': 10.00,
                },
            ]

            for m_data in methods_data:
                method, created = PaymentMethod.objects.get_or_create(
                    code=m_data['code'],
                    defaults=m_data
                )
                if created:
                    self.stdout.write(f'  Created payment method: {method.name}')
                else:
                    for key, val in m_data.items():
                        setattr(method, key, val)
                    method.save()
        except ImportError:
            self.stdout.write('Payments app not available, skipping payment methods')

    def create_faqs(self):
        """Seed standard FAQs in English"""
        try:
            from dashboard.models import FAQ

            faqs_data = [
                {
                    'question': 'How does SwiftDrop delivery work?',
                    'answer': 'Browse products across food, groceries, medicine, or LPG gas, add items to your cart, select your delivery zone and address, pick a payment method, and confirm your order. A delivery rider is dispatched immediately.',
                    'category': 'general',
                    'is_active': True,
                    'order': 1,
                },
                {
                    'question': 'What are the delivery fees across Dhaka?',
                    'answer': 'Delivery fees vary by zone from ৳40 to ৳70 depending on the delivery distance. The fee is clearly calculated and displayed before you checkout.',
                    'category': 'delivery',
                    'is_active': True,
                    'order': 2,
                },
                {
                    'question': 'Which payment methods are accepted?',
                    'answer': 'We support Cash on Delivery (COD) as well as mobile wallets including bKash, Nagad, and Rocket.',
                    'category': 'payment',
                    'is_active': True,
                    'order': 3,
                },
                {
                    'question': 'Can I cancel an order after placing it?',
                    'answer': 'Yes, orders with Pending or Confirmed status can be cancelled directly from your Order Detail page.',
                    'category': 'orders',
                    'is_active': True,
                    'order': 4,
                },
            ]

            for f_data in faqs_data:
                faq, created = FAQ.objects.get_or_create(
                    question=f_data['question'],
                    defaults=f_data
                )
                if created:
                    self.stdout.write(f'  Created FAQ: {faq.question}')
                else:
                    for key, val in f_data.items():
                        setattr(faq, key, val)
                    faq.save()
        except ImportError:
            self.stdout.write('Dashboard app not available, skipping FAQs')
