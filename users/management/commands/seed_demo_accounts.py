from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import CustomerProfile, DeliveryAgentProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds idempotent local development accounts for SwiftDrop (Customer & Admin)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding SwiftDrop development accounts...'))

        # 1. Customer Demo Account: rifat@gmail.com / 123456
        customer_email = 'rifat@gmail.com'
        customer_user = User.objects.filter(email__iexact=customer_email).first()
        if not customer_user:
            # Check if username 'rifat' exists, or create unique
            username = 'rifat'
            if User.objects.filter(username=username).exists():
                username = 'rifat_customer'
            customer_user = User(
                username=username,
                email=customer_email,
                first_name='Rifat',
                last_name='Customer',
                phone_number='01710000001',
                user_type='customer',
                is_staff=False,
                is_superuser=False,
                is_active=True,
                address='House 12, Road 5, Dhanmondi',
                city='Dhaka',
                postal_code='1205',
            )
            customer_user.set_password('123456')
            customer_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created Customer account: {customer_email}'))
        else:
            customer_user.user_type = 'customer'
            customer_user.is_staff = False
            customer_user.is_superuser = False
            customer_user.is_active = True
            customer_user.set_password('123456')
            if not customer_user.phone_number:
                customer_user.phone_number = '01710000001'
            customer_user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated Customer account: {customer_email}'))

        CustomerProfile.objects.get_or_create(
            user=customer_user,
            defaults={
                'preferred_language': 'en',
                'delivery_instructions': 'Leave at front desk if unavailable',
            }
        )

        # 2. Admin Demo Account: rifatadmin@gmail.com / 123456
        admin_email = 'rifatadmin@gmail.com'
        admin_user = User.objects.filter(email__iexact=admin_email).first()
        if not admin_user:
            username = 'rifatadmin'
            if User.objects.filter(username=username).exists():
                username = 'rifat_admin'
            admin_user = User(
                username=username,
                email=admin_email,
                first_name='Rifat',
                last_name='Admin',
                phone_number='01710000002',
                user_type='admin',
                is_staff=True,
                is_superuser=True,
                is_active=True,
                address='SwiftDrop HQ, Gulshan 2',
                city='Dhaka',
                postal_code='1212',
            )
            admin_user.set_password('123456')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created Admin account: {admin_email}'))
        else:
            admin_user.user_type = 'admin'
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.is_active = True
            admin_user.set_password('123456')
            if not admin_user.phone_number:
                admin_user.phone_number = '01710000002'
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated Admin account: {admin_email}'))

        # 3. Delivery Agent Demo Account: agent@swiftdrop.com / 123456 (for testing Phase 7 agent portal)
        agent_email = 'agent@swiftdrop.com'
        agent_user = User.objects.filter(email__iexact=agent_email).first()
        if not agent_user:
            username = 'deliveryagent'
            if User.objects.filter(username=username).exists():
                username = 'swift_delivery_agent'
            agent_user = User(
                username=username,
                email=agent_email,
                first_name='Tariq',
                last_name='Rider',
                phone_number='01710000003',
                user_type='delivery_agent',
                is_staff=False,
                is_superuser=False,
                is_active=True,
                address='Mohakhali, Dhaka',
                city='Dhaka',
                postal_code='1212',
            )
            agent_user.set_password('123456')
            agent_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created Delivery Agent account: {agent_email}'))
        else:
            agent_user.user_type = 'delivery_agent'
            agent_user.is_staff = False
            agent_user.is_superuser = False
            agent_user.set_password('123456')
            if not agent_user.phone_number:
                agent_user.phone_number = '01710000003'
            agent_user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated Delivery Agent account: {agent_email}'))

        DeliveryAgentProfile.objects.get_or_create(
            user=agent_user,
            defaults={
                'license_number': 'DHAKA-METRO-HA-1234',
                'vehicle_type': 'bike',
                'vehicle_number': 'DHK-MET-11-2233',
                'is_available': True,
                'rating': 4.9,
                'total_deliveries': 42,
            }
        )

        self.stdout.write(self.style.SUCCESS('All SwiftDrop demo accounts seeded successfully.'))
