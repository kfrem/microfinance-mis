"""
Portfolio Analytics Service
Calculates KPIs, PAR, loan classifications, and other metrics
"""
from decimal import Decimal
from datetime import date, timedelta
from django.db.models import Sum, Count, Q, F, Case, When, DecimalField, Value
from django.db.models.functions import Coalesce
from loans.models import Loan, LoanSchedule, LoanProduct
from repayments.models import Repayment
from clients.models import Client


class PortfolioAnalytics:
    """Calculate portfolio-level metrics and KPIs"""
    
    @staticmethod
    def get_portfolio_summary():
        """Get overall portfolio summary statistics"""
        active_loans = Loan.objects.filter(status='active')
        
        total_portfolio = active_loans.aggregate(
            total=Coalesce(Sum('principal'), Decimal('0'))
        )['total']
        
        # Calculate outstanding balance by summing total_repayable for each loan
        total_outstanding = Decimal('0')
        for loan in active_loans:
            total_outstanding += loan.get_outstanding_balance()
        
        total_disbursed = Loan.objects.filter(
            status__in=['active', 'closed']
        ).aggregate(
            total=Coalesce(Sum('principal'), Decimal('0'))
        )['total']
        
        total_collected = Repayment.objects.filter(
            status='confirmed'
        ).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']
        
        return {
            'total_portfolio_value': total_portfolio,
            'total_outstanding': total_outstanding,
            'total_disbursed': total_disbursed,
            'total_collected': total_collected,
            'active_loans_count': active_loans.count(),
            'total_clients': Client.objects.count(),
            'collection_rate': (
                (total_collected / total_disbursed * 100)
                if total_disbursed > 0 else Decimal('0')
            ),
        }
    
    @staticmethod
    def get_par_metrics():
        """Calculate Portfolio at Risk (PAR) metrics"""
        today = date.today()
        active_loans = Loan.objects.filter(status='active')
        
        # Calculate total outstanding
        total_outstanding = Decimal('0')
        for loan in active_loans:
            total_outstanding += loan.get_outstanding_balance()
        
        # PAR 30: Loans with payments overdue by 30+ days
        par_30_loans = active_loans.filter(days_in_arrears__gte=30)
        par_30_value = Decimal('0')
        for loan in par_30_loans:
            par_30_value += loan.get_outstanding_balance()
        
        # PAR 90: Loans with payments overdue by 90+ days
        par_90_loans = active_loans.filter(days_in_arrears__gte=90)
        par_90_value = Decimal('0')
        for loan in par_90_loans:
            par_90_value += loan.get_outstanding_balance()
        
        return {
            'par_30_value': par_30_value,
            'par_30_count': par_30_loans.count(),
            'par_30_rate': (
                (par_30_value / total_outstanding * 100)
                if total_outstanding > 0 else Decimal('0')
            ),
            'par_90_value': par_90_value,
            'par_90_count': par_90_loans.count(),
            'par_90_rate': (
                (par_90_value / total_outstanding * 100)
                if total_outstanding > 0 else Decimal('0')
            ),
            'total_outstanding': total_outstanding,
        }
    
    @staticmethod
    def get_bog_classification():
        """Get BoG loan classification breakdown"""
        active_loans = Loan.objects.filter(status='active')
        
        classification_breakdown = {
            'current': {
                'count': 0,
                'value': Decimal('0'),
                'provision_rate': Decimal('0'),
                'provision_amount': Decimal('0'),
            },
            'substandard': {
                'count': 0,
                'value': Decimal('0'),
                'provision_rate': Decimal('10'),
                'provision_amount': Decimal('0'),
            },
            'doubtful': {
                'count': 0,
                'value': Decimal('0'),
                'provision_rate': Decimal('50'),
                'provision_amount': Decimal('0'),
            },
            'loss': {
                'count': 0,
                'value': Decimal('0'),
                'provision_rate': Decimal('100'),
                'provision_amount': Decimal('0'),
            },
        }
        
        for loan in active_loans:
            classification = loan.bog_classification.lower()
            if classification in classification_breakdown:
                classification_breakdown[classification]['count'] += 1
                classification_breakdown[classification]['value'] += loan.get_outstanding_balance()
        
        # Calculate provision amounts
        for classification, data in classification_breakdown.items():
            if data['provision_rate'] > 0:
                data['provision_amount'] = (
                    data['value'] * data['provision_rate'] / 100
                )
        
        total_provisions = sum(
            data['provision_amount']
            for data in classification_breakdown.values()
        )
        
        return {
            'breakdown': classification_breakdown,
            'total_provisions_required': total_provisions,
        }
    
    @staticmethod
    def get_loan_product_performance():
        """Get performance metrics by loan product"""
        products = LoanProduct.objects.all()
        performance = []
        
        for product in products:
            active_loans = Loan.objects.filter(
                product=product,
                status='active'
            )
            
            total_outstanding = Decimal('0')
            for loan in active_loans:
                total_outstanding += loan.get_outstanding_balance()
            
            arrears_loans = active_loans.filter(days_in_arrears__gt=0)
            arrears_value = Decimal('0')
            for loan in arrears_loans:
                arrears_value += loan.get_outstanding_balance()
            
            performance.append({
                'product_name': product.name,
                'active_count': active_loans.count(),
                'total_outstanding': total_outstanding,
                'arrears_count': arrears_loans.count(),
                'arrears_value': arrears_value,
                'arrears_rate': (
                    (arrears_value / total_outstanding * 100)
                    if total_outstanding > 0 else Decimal('0')
                ),
            })
        
        return performance
    
    @staticmethod
    def get_repayment_trends(days=30):
        """Get repayment collection trends"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        repayments = Repayment.objects.filter(
            paid_on__gte=start_date,
            paid_on__lte=end_date,
            status='confirmed'
        ).values('paid_on').annotate(
            total_amount=Sum('amount'),
            count=Count('id')
        ).order_by('paid_on')
        
        return list(repayments)
    
    @staticmethod
    def get_arrears_aging():
        """Get aging analysis of arrears"""
        active_loans = Loan.objects.filter(status='active', days_in_arrears__gt=0)
        
        aging_buckets = {
            '1-30 days': active_loans.filter(
                days_in_arrears__gte=1, days_in_arrears__lt=30
            ),
            '31-60 days': active_loans.filter(
                days_in_arrears__gte=30, days_in_arrears__lt=60
            ),
            '61-90 days': active_loans.filter(
                days_in_arrears__gte=60, days_in_arrears__lt=90
            ),
            '91-180 days': active_loans.filter(
                days_in_arrears__gte=90, days_in_arrears__lt=180
            ),
            '180+ days': active_loans.filter(
                days_in_arrears__gte=180
            ),
        }
        
        aging_analysis = {}
        for bucket_name, queryset in aging_buckets.items():
            total_value = Decimal('0')
            for loan in queryset:
                total_value += loan.get_outstanding_balance()
            
            aging_analysis[bucket_name] = {
                'count': queryset.count(),
                'value': total_value,
            }
        
        return aging_analysis
    
    @staticmethod
    def get_client_statistics():
        """Get client-level statistics"""
        total_clients = Client.objects.count()
        active_borrowers = Client.objects.filter(
            loans__status='active'
        ).distinct().count()
        
        clients_by_risk = Client.objects.values('risk_level').annotate(
            count=Count('id')
        )
        
        risk_breakdown = {item['risk_level']: item['count'] for item in clients_by_risk}
        
        return {
            'total_clients': total_clients,
            'active_borrowers': active_borrowers,
            'inactive_clients': total_clients - active_borrowers,
            'risk_breakdown': risk_breakdown,
        }


class ReportGenerator:
    """Generate various reports for management and compliance"""
    
    @staticmethod
    def generate_portfolio_quality_report():
        """Comprehensive portfolio quality report"""
        analytics = PortfolioAnalytics()
        
        return {
            'summary': analytics.get_portfolio_summary(),
            'par_metrics': analytics.get_par_metrics(),
            'bog_classification': analytics.get_bog_classification(),
            'product_performance': analytics.get_loan_product_performance(),
            'arrears_aging': analytics.get_arrears_aging(),
            'client_stats': analytics.get_client_statistics(),
            'generated_at': date.today(),
        }
    
    @staticmethod
    def generate_bog_prudential_report():
        """Generate BoG prudential reporting data"""
        analytics = PortfolioAnalytics()
        summary = analytics.get_portfolio_summary()
        par = analytics.get_par_metrics()
        classification = analytics.get_bog_classification()
        
        return {
            'report_date': date.today(),
            'gross_loan_portfolio': summary['total_outstanding'],
            'number_of_active_loans': summary['active_loans_count'],
            'number_of_borrowers': summary['total_clients'],
            'par_30': par['par_30_rate'],
            'par_90': par['par_90_rate'],
            'loan_classification': classification['breakdown'],
            'total_provisions': classification['total_provisions_required'],
            'npl_ratio': par['par_90_rate'],  # NPL typically defined as PAR 90+
        }
