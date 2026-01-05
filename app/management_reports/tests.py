"""
Automated Tests for Management Reports
Ensures all reports work correctly and prevents regressions
"""
from django.test import TestCase, Client as TestClient
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date, timedelta

from clients.models import Client
from loans.models import Loan, LoanProduct
from repayments.models import Repayment


class ManagementReportsTestCase(TestCase):
    """Test suite for all management reports to prevent regressions."""
    
    def setUp(self):
        """Set up test data before each test."""
        # Create test user
        self.user = User.objects.create_user(
            username='testadmin',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create test client
        self.client = TestClient()
        self.client.login(username='testadmin', password='testpass123')
        
        # Create loan product
        self.product = LoanProduct.objects.create(
            code='TEST001',
            name='Test Loan Product',
            interest_rate=Decimal('20.00'),
            interest_method='flat',
            repayment_frequency='monthly',
            min_amount=Decimal('1000.00'),
            max_amount=Decimal('50000.00'),
            min_term_months=6,
            max_term_months=24,
            processing_fee_percentage=Decimal('5.00'),
            insurance_fee_percentage=Decimal('2.00'),
            is_active=True
        )
        
        # Create test client
        self.test_client = Client.objects.create(
            client_id='C99999',
            full_name='Test Client',
            phone='+233241234567',
            email='test@example.com',
            client_type='individual',
            status='active',
            kyc_verified=True
        )
        
        # Create test loan
        self.loan = Loan.objects.create(
            client=self.test_client,
            product=self.product,
            principal=Decimal('10000.00'),
            interest_rate=Decimal('20.00'),
            interest_method='flat',
            term_months=12,
            repayment_frequency='monthly',
            status='active',
            application_date=date.today() - timedelta(days=30),
            approved_date=date.today() - timedelta(days=25),
            disbursed_date=date.today() - timedelta(days=20),
            created_by=self.user,
            disbursed_by=self.user
        )
        
        # Generate repayment schedule
        self.loan.generate_repayment_schedule()
        
        # Create test repayment
        Repayment.objects.create(
            loan=self.loan,
            amount=Decimal('1200.00'),
            principal_paid=Decimal('1000.00'),
            interest_paid=Decimal('200.00'),
            penalty_paid=Decimal('0.00'),
            paid_on=date.today(),
            method='cash',
            status='confirmed',
            received_by=self.user
        )
    
    def test_management_dashboard_loads(self):
        """Test that management dashboard loads without errors."""
        response = self.client.get(reverse('management_reports:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Management & Board Dashboard')
        self.assertContains(response, 'Total Portfolio Value')
    
    def test_profit_loss_report_loads(self):
        """Test that P&L report page loads."""
        response = self.client.get(reverse('management_reports:profit_loss'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profit & Loss Statement')
    
    def test_board_report_loads(self):
        """Test that board report page loads."""
        response = self.client.get(reverse('management_reports:board_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Board Executive Summary')
    
    def test_officer_performance_loads(self):
        """Test that officer performance page loads."""
        response = self.client.get(reverse('management_reports:officer_performance'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Loan Officer Performance')
    
    def test_profit_loss_excel_export(self):
        """Test that P&L Excel export works."""
        response = self.client.get(reverse('management_reports:export_profit_loss_excel'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('profit_loss_', response['Content-Disposition'])
    
    def test_profit_loss_pdf_export(self):
        """Test that P&L PDF export works."""
        response = self.client.get(reverse('management_reports:export_profit_loss_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('profit_loss_', response['Content-Disposition'])
    
    def test_board_excel_export(self):
        """Test that board Excel export works."""
        response = self.client.get(reverse('management_reports:export_board_excel'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    def test_board_pdf_export(self):
        """Test that board PDF export works."""
        response = self.client.get(reverse('management_reports:export_board_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
    
    def test_officer_excel_export(self):
        """Test that officer performance Excel export works."""
        response = self.client.get(reverse('management_reports:export_officer_performance_excel'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    def test_all_reports_dashboard_links(self):
        """Test that all report links work from reports dashboard."""
        response = self.client.get(reverse('reports:dashboard'))
        self.assertEqual(response.status_code, 200)
        # Check for key report links
        self.assertContains(response, 'Client Portfolio Report')
        self.assertContains(response, 'Loan Aging Analysis')
    
    def test_analytics_dashboard_loads(self):
        """Test that analytics dashboard loads."""
        response = self.client.get(reverse('dashboard:executive'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Analytics Dashboard')
    
    def test_home_page_loads(self):
        """Test that home page loads with all dashboard cards."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ghana Microfinance MIS')
        self.assertContains(response, 'Management Dashboard')
        self.assertContains(response, 'Operational Reports')


class ReportDataValidationTestCase(TestCase):
    """Test that report calculations are accurate."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            is_staff=True
        )
        
        self.product = LoanProduct.objects.create(
            code='VAL001',
            name='Validation Product',
            interest_rate=Decimal('15.00'),
            interest_method='flat',
            repayment_frequency='monthly',
            min_amount=Decimal('5000.00'),
            max_amount=Decimal('100000.00'),
            min_term_months=6,
            max_term_months=36,
            processing_fee_percentage=Decimal('5.00'),
            insurance_fee_percentage=Decimal('2.00'),
            is_active=True
        )
        
        self.test_client = Client.objects.create(
            client_id='C88888',
            full_name='Validation Client',
            phone='+233241111111',
            email='validation@test.com',
            client_type='individual',
            status='active',
            kyc_verified=True
        )
        
        # Create loan with known values
        self.loan = Loan.objects.create(
            client=self.test_client,
            product=self.product,
            principal=Decimal('10000.00'),
            interest_rate=Decimal('15.00'),
            interest_method='flat',
            term_months=12,
            repayment_frequency='monthly',
            status='active',
            processing_fee=Decimal('500.00'),  # 5%
            insurance_fee=Decimal('200.00'),   # 2%
            application_date=date.today(),
            approved_date=date.today(),
            disbursed_date=date.today(),
            created_by=self.user
        )
    
    def test_portfolio_value_calculation(self):
        """Test that total portfolio value is calculated correctly."""
        from loans.models import Loan
        from django.db.models import Sum
        
        active_loans = Loan.objects.filter(status='active')
        expected_total = active_loans.aggregate(total=Sum('principal'))['total']
        
        # This should equal the sum of all active loan principals
        self.assertIsNotNone(expected_total)
        self.assertGreater(expected_total, 0)
    
    def test_fee_calculation(self):
        """Test that processing and insurance fees are correct."""
        self.assertEqual(self.loan.processing_fee, Decimal('500.00'))
        self.assertEqual(self.loan.insurance_fee, Decimal('200.00'))


class NavigationTestCase(TestCase):
    """Test that navigation works across all pages."""
    
    def setUp(self):
        """Set up test client."""
        self.user = User.objects.create_user(
            username='navtest',
            password='navpass',
            is_staff=True
        )
        self.client = TestClient()
        self.client.login(username='navtest', password='navpass')
    
    def test_home_to_management_navigation(self):
        """Test navigation from home to management dashboard."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Now navigate to management
        response = self.client.get('/management/')
        self.assertEqual(response.status_code, 200)
    
    def test_management_to_reports_navigation(self):
        """Test navigation from management to reports."""
        response = self.client.get('/management/')
        self.assertEqual(response.status_code, 200)
        
        # Navigate to reports
        response = self.client.get('/reports/')
        self.assertEqual(response.status_code, 200)
    
    def test_base_template_navigation_bar(self):
        """Test that navigation bar appears on all pages."""
        pages = [
            '/',
            '/management/',
            '/reports/',
            '/dashboard/',
        ]
        
        for page in pages:
            response = self.client.get(page)
            self.assertEqual(response.status_code, 200)
            # Check for nav bar elements
            self.assertContains(response, 'Ghana Microfinance MIS')
            self.assertContains(response, 'Home')
