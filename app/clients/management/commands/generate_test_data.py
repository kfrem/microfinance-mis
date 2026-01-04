"""
Generate realistic test data for Phase 1 & 2 testing.
Creates Ghana-based microfinance test data including clients, loans, and repayments.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import random

from clients.models import Client
from loans.models import Loan, LoanProduct
from repayments.models import Repayment


class Command(BaseCommand):
    help = 'Generate realistic test data for microfinance system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clients',
            type=int,
            default=20,
            help='Number of clients to create'
        )
        parser.add_argument(
            '--loans',
            type=int,
            default=15,
            help='Number of loans to create'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting Test Data Generation...'))
        
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'email': 'admin@microfinance.gh'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created admin user'))
        
        # Ghana-specific test data
        ghana_names = [
            'Kwame Mensah', 'Akosua Addo', 'Kofi Owusu', 'Ama Asante',
            'Kwabena Boateng', 'Abena Ofori', 'Yaw Amoako', 'Efua Gyasi',
            'Kwesi Appiah', 'Adjoa Bonsu', 'Kojo Ansah', 'Adwoa Sarpong',
            'Fiifi Yankson', 'Esi Darko', 'Kobby Agyeman', 'Akua Frimpong',
            'Nana Osei', 'Maame Afia', 'Papa Yeboah', 'Afua Boakye',
            'Yaa Konadu', 'Kwaku Frimpong', 'Abena Asare', 'Kojo Manu'
        ]
        
        ghana_occupations = [
            'Trader', 'Seamstress', 'Hairdresser', 'Carpenter', 'Mason',
            'Farmer', 'Food Vendor', 'Shop Owner', 'Mechanic', 'Driver',
            'Teacher', 'Tailor', 'Baker', 'Electrician', 'Plumber'
        ]
        
        ghana_locations = [
            'Accra', 'Kumasi', 'Tamale', 'Takoradi', 'Cape Coast',
            'Tema', 'Sunyani', 'Ho', 'Koforidua', 'Wa'
        ]
        
        # Create Clients
        num_clients = options['clients']
        clients_created = 0
        
        self.stdout.write(f'\n📋 Creating {num_clients} test clients...')
        
        for i in range(num_clients):
            name = random.choice(ghana_names)
            
            # Ensure unique phone numbers
            phone = f"+233{random.randint(200000000, 599999999)}"
            
            # Random Ghana Card ID (format: GHA-XXXXXXXXX-X)
            ghana_card = f"GHA-{random.randint(100000000, 999999999)}-{random.randint(1, 9)}"
            
            client = Client.objects.create(
                full_name=name,
                phone=phone,
                email=f"{name.lower().replace(' ', '.')}@example.gh",
                address=f"{random.randint(1, 200)} {random.choice(['High', 'Main', 'Market', 'Station'])} Street, {random.choice(ghana_locations)}",
                ghana_card_id=ghana_card,
                date_of_birth=date(random.randint(1970, 2000), random.randint(1, 12), random.randint(1, 28)),
                occupation=random.choice(ghana_occupations),
                monthly_income=Decimal(str(random.randint(500, 5000))),
                risk_category=random.choice(['low', 'medium', 'high']),
                status=random.choice(['active'] * 8 + ['inactive'] * 2),  # 80% active
                kyc_verified=random.choice([True, True, True, False]),  # 75% verified
                kyc_verified_date=date.today() - timedelta(days=random.randint(1, 365)) if random.random() > 0.25 else None,
                kyc_verified_by=admin_user if random.random() > 0.25 else None,
                created_by=admin_user,
                client_type=random.choice(['individual'] * 7 + ['group'] * 2 + ['sme'] * 1),
            )
            
            # For groups, add group info
            if client.client_type == 'group':
                client.group_size = random.randint(5, 15)
                client.group_leader = random.choice(ghana_names)
                client.save()
            
            clients_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {clients_created} clients'))
        
        # Create Loans
        num_loans = options['loans']
        loans_created = 0
        
        self.stdout.write(f'\n💰 Creating {num_loans} test loans...')
        
        # Get all loan products
        products = list(LoanProduct.objects.filter(is_active=True))
        if not products:
            self.stdout.write(self.style.ERROR('❌ No loan products found! Run create_loan_products first.'))
            return
        
        # Get active clients
        active_clients = list(Client.objects.filter(status='active'))
        
        for i in range(num_loans):
            client = random.choice(active_clients)
            product = random.choice(products)
            
            # Random principal within product limits
            principal = Decimal(str(random.randint(
                int(product.min_amount),
                int(product.max_amount)
            )))
            
            # Random term within product limits
            term_months = random.randint(product.min_term_months, product.max_term_months)
            
            # Random disbursement date (between 180 days ago and 30 days ago)
            days_ago = random.randint(30, 180)
            disbursed_date = date.today() - timedelta(days=days_ago)
            
            # Calculate processing and insurance fees
            processing_fee = principal * (product.processing_fee_percentage / Decimal('100'))
            insurance_fee = principal * (product.insurance_fee_percentage / Decimal('100'))
            
            # Determine loan status
            status_weights = ['active'] * 12 + ['closed'] * 2 + ['pending'] * 1
            status = random.choice(status_weights)
            
            loan = Loan.objects.create(
                client=client,
                product=product,
                principal=principal,
                interest_rate=product.interest_rate,
                interest_method=product.interest_method,
                term_months=term_months,
                repayment_frequency=product.repayment_frequency,
                processing_fee=processing_fee,
                insurance_fee=insurance_fee,
                application_date=disbursed_date - timedelta(days=7),
                approved_date=disbursed_date - timedelta(days=3),
                disbursed_date=disbursed_date if status in ['active', 'closed'] else None,
                status=status,
                approved_by=admin_user,
                disbursed_by=admin_user if status in ['active', 'closed'] else None,
                disbursement_method=random.choice(['cash', 'bank_transfer', 'mobile_money']),
                disbursement_reference=f"TXN{random.randint(100000, 999999)}",
            )
            
            # Generate repayment schedule for active/closed loans
            if loan.status in ['active', 'closed'] and loan.disbursed_date:
                loan.first_repayment_date = loan.disbursed_date + timedelta(days=30)
                loan.save()
                loan.generate_repayment_schedule()
                
                # Create some repayments
                if loan.status == 'active':
                    # Active loans: 40-90% paid
                    payment_ratio = random.uniform(0.4, 0.9)
                    self._create_repayments(loan, payment_ratio, admin_user)
                elif loan.status == 'closed':
                    # Closed loans: 100% paid
                    self._create_repayments(loan, 1.0, admin_user)
            
            loans_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {loans_created} loans with schedules'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('🎉 TEST DATA GENERATION COMPLETE!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'  • Clients Created: {clients_created}')
        self.stdout.write(f'  • Loans Created: {loans_created}')
        self.stdout.write(f'  • Total Repayments: {Repayment.objects.count()}')
        
        # Portfolio stats
        active_loans = Loan.objects.filter(status='active')
        total_principal = sum(loan.principal for loan in active_loans)
        total_outstanding = sum(loan.get_outstanding_balance() for loan in active_loans)
        
        self.stdout.write(f'\n💼 Portfolio Stats:')
        self.stdout.write(f'  • Active Loans: {active_loans.count()}')
        self.stdout.write(f'  • Total Principal: GHS {total_principal:,.2f}')
        self.stdout.write(f'  • Total Outstanding: GHS {total_outstanding:,.2f}')
        
        # Arrears summary
        loans_in_arrears = active_loans.filter(days_in_arrears__gt=0)
        self.stdout.write(f'  • Loans in Arrears: {loans_in_arrears.count()}')
        
        self.stdout.write(f'\n✅ Ready to test! Visit: http://localhost:8000/dashboard/')
        self.stdout.write(self.style.SUCCESS('\n'))
    
    def _create_repayments(self, loan, payment_ratio, user):
        """Create repayments for a loan based on payment ratio."""
        schedule_entries = list(loan.schedule_entries.all().order_by('due_date'))
        
        num_to_pay = int(len(schedule_entries) * payment_ratio)
        
        for i, entry in enumerate(schedule_entries[:num_to_pay]):
            # Random payment amount (80-100% of due amount)
            payment_amount = entry.total_due * Decimal(str(random.uniform(0.8, 1.0)))
            
            # Random payment date (around due date ± 5 days)
            payment_date = entry.due_date + timedelta(days=random.randint(-5, 15))
            
            Repayment.objects.create(
                loan=loan,
                amount=payment_amount,
                paid_on=payment_date,
                method=random.choice(['cash', 'mobile_money', 'bank_transfer']),
                reference=f"REF{random.randint(10000, 99999)}",
                status='confirmed',
                received_by=user,
                confirmed_by=user,
            )
