"""
Management command to create standard Ghana microfinance loan products.
Based on research from Microfinance_MIS_Complete_Research.md
"""
from django.core.management.base import BaseCommand
from decimal import Decimal
from loans.models import LoanProduct


class Command(BaseCommand):
    help = 'Create standard Ghana microfinance loan products'
    
    def handle(self, *args, **options):
        products = [
            {
                'name': 'Individual Micro Loan',
                'code': 'IML-001',
                'description': 'Small loans for traders, artisans, self-employed individuals',
                'min_amount': Decimal('100.00'),
                'max_amount': Decimal('5000.00'),
                'interest_rate': Decimal('30.00'),  # 30% annual
                'interest_method': 'flat',
                'min_term_months': 3,
                'max_term_months': 12,
                'repayment_frequency': 'weekly',
                'processing_fee_percentage': Decimal('2.00'),
                'insurance_fee_percentage': Decimal('1.00'),
                'late_payment_penalty_rate': Decimal('2.00'),
                'requires_collateral': False,
                'requires_guarantor': True,
                'min_guarantors': 1,
                'is_active': True,
            },
            {
                'name': 'Group Solidarity Loan',
                'code': 'GSL-001',
                'description': 'Loans for solidarity groups (5-10 members with joint liability)',
                'min_amount': Decimal('500.00'),
                'max_amount': Decimal('10000.00'),
                'interest_rate': Decimal('28.00'),
                'interest_method': 'flat',
                'min_term_months': 4,
                'max_term_months': 12,
                'repayment_frequency': 'biweekly',
                'processing_fee_percentage': Decimal('1.50'),
                'insurance_fee_percentage': Decimal('1.00'),
                'late_payment_penalty_rate': Decimal('2.00'),
                'requires_collateral': False,
                'requires_guarantor': False,  # Group serves as guarantee
                'min_guarantors': 0,
                'is_active': True,
            },
            {
                'name': 'SME Business Loan',
                'code': 'SME-001',
                'description': 'Larger loans for established small/medium enterprises',
                'min_amount': Decimal('5000.00'),
                'max_amount': Decimal('50000.00'),
                'interest_rate': Decimal('24.00'),
                'interest_method': 'declining',
                'min_term_months': 6,
                'max_term_months': 24,
                'repayment_frequency': 'monthly',
                'processing_fee_percentage': Decimal('3.00'),
                'insurance_fee_percentage': Decimal('1.50'),
                'late_payment_penalty_rate': Decimal('2.00'),
                'requires_collateral': True,
                'requires_guarantor': True,
                'min_guarantors': 2,
                'is_active': True,
            },
            {
                'name': 'Agricultural Loan',
                'code': 'AGL-001',
                'description': 'Seasonal loans for farmers (harvest-linked repayment)',
                'min_amount': Decimal('500.00'),
                'max_amount': Decimal('20000.00'),
                'interest_rate': Decimal('22.00'),
                'interest_method': 'flat',
                'min_term_months': 6,
                'max_term_months': 12,
                'repayment_frequency': 'monthly',
                'processing_fee_percentage': Decimal('2.00'),
                'insurance_fee_percentage': Decimal('2.00'),
                'late_payment_penalty_rate': Decimal('1.50'),
                'requires_collateral': True,
                'requires_guarantor': True,
                'min_guarantors': 1,
                'is_active': True,
            },
            {
                'name': 'Emergency Loan',
                'code': 'EML-001',
                'description': 'Quick short-term loans for emergencies (existing clients only)',
                'min_amount': Decimal('200.00'),
                'max_amount': Decimal('3000.00'),
                'interest_rate': Decimal('35.00'),
                'interest_method': 'flat',
                'min_term_months': 1,
                'max_term_months': 6,
                'repayment_frequency': 'monthly',
                'processing_fee_percentage': Decimal('3.00'),
                'insurance_fee_percentage': Decimal('0.00'),
                'late_payment_penalty_rate': Decimal('3.00'),
                'requires_collateral': False,
                'requires_guarantor': True,
                'min_guarantors': 1,
                'is_active': True,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for product_data in products:
            product, created = LoanProduct.objects.update_or_create(
                code=product_data['code'],
                defaults=product_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {product.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'→ Updated: {product.name}'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} and updated {updated_count} loan products'))
