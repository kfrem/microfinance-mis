"""
Test command to verify analytics calculations
"""
from django.core.management.base import BaseCommand
from dashboard.analytics import PortfolioAnalytics, ReportGenerator


class Command(BaseCommand):
    help = 'Test analytics and report generation'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing Analytics...'))
        
        analytics = PortfolioAnalytics()
        
        # Test portfolio summary
        self.stdout.write('\n=== Portfolio Summary ===')
        summary = analytics.get_portfolio_summary()
        for key, value in summary.items():
            self.stdout.write(f'{key}: {value}')
        
        # Test PAR metrics
        self.stdout.write('\n=== PAR Metrics ===')
        par = analytics.get_par_metrics()
        for key, value in par.items():
            self.stdout.write(f'{key}: {value}')
        
        # Test BoG classification
        self.stdout.write('\n=== BoG Classification ===')
        bog = analytics.get_bog_classification()
        self.stdout.write(f'Total Provisions: {bog["total_provisions_required"]}')
        for classification, data in bog['breakdown'].items():
            self.stdout.write(f'{classification}: {data["count"]} loans, GH₵ {data["value"]}')
        
        # Test product performance
        self.stdout.write('\n=== Product Performance ===')
        products = analytics.get_loan_product_performance()
        for product in products:
            self.stdout.write(f'{product["product_name"]}: {product["active_count"]} loans, GH₵ {product["total_outstanding"]}')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Analytics test completed successfully!'))
