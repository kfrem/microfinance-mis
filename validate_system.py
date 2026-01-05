#!/usr/bin/env python
"""
System Validation Script
Run this BEFORE deploying to ensure no regressions
Usage: docker compose exec web python validate_system.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test.utils import get_runner
from django.conf import settings
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from loans.models import Loan, LoanProduct
from clients.models import Client as ClientModel
from repayments.models import Repayment
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{text.center(80)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

def print_success(text):
    """Print success message."""
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_error(text):
    """Print error message."""
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def print_warning(text):
    """Print warning message."""
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")

def print_info(text):
    """Print info message."""
    print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")


class SystemValidator:
    """Validates entire system health."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = 0
        self.failed = 0
    
    def validate_database_connection(self):
        """Check database connectivity."""
        print_info("Checking database connection...")
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            print_success("Database connection working")
            self.passed += 1
            return True
        except Exception as e:
            print_error(f"Database connection failed: {e}")
            self.errors.append(f"Database: {e}")
            self.failed += 1
            return False
    
    def validate_models_exist(self):
        """Check that all required models exist."""
        print_info("Validating models...")
        models_to_check = [
            ('clients.Client', ClientModel),
            ('loans.Loan', Loan),
            ('loans.LoanProduct', LoanProduct),
            ('repayments.Repayment', Repayment),
        ]
        
        for model_name, model_class in models_to_check:
            try:
                count = model_class.objects.count()
                print_success(f"{model_name}: {count} records")
                self.passed += 1
            except Exception as e:
                print_error(f"{model_name}: Error - {e}")
                self.errors.append(f"{model_name}: {e}")
                self.failed += 1
    
    def validate_urls(self):
        """Check that all critical URLs are configured."""
        print_info("Validating URL configuration...")
        
        urls_to_check = [
            ('home', '/'),
            ('management_reports:dashboard', '/management/'),
            ('management_reports:profit_loss', '/management/profit-loss/'),
            ('management_reports:board_report', '/management/board-report/'),
            ('management_reports:officer_performance', '/management/officer-performance/'),
            ('reports:dashboard', '/reports/'),
            ('dashboard:executive', '/dashboard/'),
        ]
        
        for url_name, expected_path in urls_to_check:
            try:
                resolved_url = reverse(url_name)
                if resolved_url == expected_path:
                    print_success(f"{url_name} → {resolved_url}")
                    self.passed += 1
                else:
                    print_warning(f"{url_name} → {resolved_url} (expected {expected_path})")
                    self.warnings.append(f"{url_name} path mismatch")
                    self.passed += 1
            except Exception as e:
                print_error(f"{url_name}: Not found - {e}")
                self.errors.append(f"URL {url_name}: {e}")
                self.failed += 1
    
    def validate_report_exports(self):
        """Check that report export functions exist."""
        print_info("Validating report export methods...")
        
        from reports.excel_generator import ExcelReportGenerator
        from reports.pdf_generator import PDFReportGenerator
        
        excel_generator = ExcelReportGenerator()
        pdf_generator = PDFReportGenerator()
        
        excel_methods = [
            'generate_profit_loss_excel',
            'generate_board_report_excel',
            'generate_officer_performance_excel',
            'generate_client_portfolio_report',
            'generate_loan_aging_report',
            'generate_bog_regulatory_report',
        ]
        
        pdf_methods = [
            'generate_profit_loss_pdf',
            'generate_board_report_pdf',
            'generate_loan_statement',
            'generate_payment_receipt',
            'generate_portfolio_summary',
        ]
        
        for method_name in excel_methods:
            if hasattr(excel_generator, method_name):
                print_success(f"Excel: {method_name}")
                self.passed += 1
            else:
                print_error(f"Excel: {method_name} NOT FOUND")
                self.errors.append(f"Missing Excel method: {method_name}")
                self.failed += 1
        
        for method_name in pdf_methods:
            if hasattr(pdf_generator, method_name):
                print_success(f"PDF: {method_name}")
                self.passed += 1
            else:
                print_error(f"PDF: {method_name} NOT FOUND")
                self.errors.append(f"Missing PDF method: {method_name}")
                self.failed += 1
    
    def validate_views_load(self):
        """Test that all views can be loaded."""
        print_info("Testing view loading (requires test client)...")
        
        # Create test user
        try:
            user = User.objects.get(username='validator_test')
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='validator_test',
                password='testpass123',
                is_staff=True,
                is_superuser=True
            )
        
        client = Client()
        client.force_login(user)
        
        views_to_test = [
            ('/', 'Home Page'),
            ('/management/', 'Management Dashboard'),
            ('/management/profit-loss/', 'Profit & Loss'),
            ('/management/board-report/', 'Board Report'),
            ('/management/officer-performance/', 'Officer Performance'),
            ('/reports/', 'Reports Dashboard'),
            ('/dashboard/', 'Analytics Dashboard'),
        ]
        
        for url, name in views_to_test:
            try:
                response = client.get(url)
                if response.status_code == 200:
                    print_success(f"{name}: HTTP 200")
                    self.passed += 1
                elif response.status_code == 302:
                    print_warning(f"{name}: HTTP 302 (redirect)")
                    self.warnings.append(f"{name} redirects")
                    self.passed += 1
                else:
                    print_error(f"{name}: HTTP {response.status_code}")
                    self.errors.append(f"{name}: Status {response.status_code}")
                    self.failed += 1
            except Exception as e:
                print_error(f"{name}: {e}")
                self.errors.append(f"{name}: {e}")
                self.failed += 1
    
    def validate_templates_exist(self):
        """Check that all templates exist."""
        print_info("Validating template files...")
        
        import os
        templates_to_check = [
            'app/core/templates/base.html',
            'app/core/templates/home.html',
            'app/management_reports/templates/management_reports/dashboard.html',
            'app/management_reports/templates/management_reports/profit_loss.html',
            'app/management_reports/templates/management_reports/board_report.html',
            'app/management_reports/templates/management_reports/officer_performance.html',
            'app/reports/templates/reports/dashboard.html',
            'app/dashboard/templates/dashboard/executive_dashboard.html',
        ]
        
        for template_path in templates_to_check:
            full_path = f'/app/{template_path}'
            if os.path.exists(full_path):
                print_success(template_path)
                self.passed += 1
            else:
                print_error(f"{template_path} NOT FOUND")
                self.errors.append(f"Missing template: {template_path}")
                self.failed += 1
    
    def print_summary(self):
        """Print validation summary."""
        print_header("VALIDATION SUMMARY")
        
        total_tests = self.passed + self.failed
        pass_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{Fore.CYAN}Total Tests Run: {total_tests}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Passed: {self.passed}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed: {self.failed}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Warnings: {len(self.warnings)}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Pass Rate: {pass_rate:.1f}%{Style.RESET_ALL}\n")
        
        if self.errors:
            print(f"\n{Fore.RED}{'='*80}{Style.RESET_ALL}")
            print(f"{Fore.RED}ERRORS FOUND:{Style.RESET_ALL}\n")
            for i, error in enumerate(self.errors, 1):
                print(f"{Fore.RED}{i}. {error}{Style.RESET_ALL}")
            print(f"\n{Fore.RED}{'='*80}{Style.RESET_ALL}")
        
        if self.warnings:
            print(f"\n{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}WARNINGS:{Style.RESET_ALL}\n")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{Fore.YELLOW}{i}. {warning}{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
        
        if self.failed == 0:
            print(f"\n{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✓ ALL VALIDATIONS PASSED - SAFE TO DEPLOY{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}\n")
            return True
        else:
            print(f"\n{Fore.RED}{'='*80}{Style.RESET_ALL}")
            print(f"{Fore.RED}✗ VALIDATION FAILED - DO NOT DEPLOY{Style.RESET_ALL}")
            print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}\n")
            return False


def main():
    """Run all validations."""
    print_header("GHANA MICROFINANCE MIS - SYSTEM VALIDATION")
    print(f"{Fore.CYAN}Running comprehensive system checks...{Style.RESET_ALL}\n")
    
    validator = SystemValidator()
    
    # Run all validations
    validator.validate_database_connection()
    print()
    
    validator.validate_models_exist()
    print()
    
    validator.validate_urls()
    print()
    
    validator.validate_report_exports()
    print()
    
    validator.validate_templates_exist()
    print()
    
    validator.validate_views_load()
    
    # Print summary
    success = validator.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
