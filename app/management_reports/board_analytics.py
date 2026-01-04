"""
Board-Level Analytics & Executive KPIs
High-level metrics for board monitoring and strategic decision making
"""
from decimal import Decimal
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Count, Q, Avg
from django.db.models.functions import Coalesce

from loans.models import Loan, LoanProduct
from repayments.models import Repayment
from clients.models import Client
from dashboard.analytics import PortfolioAnalytics


class BoardAnalytics:
    """Executive-level analytics for board reporting"""
    
    def __init__(self):
        self.portfolio_analytics = PortfolioAnalytics()
    
    def get_executive_summary(self):
        """Get high-level executive summary for board"""
        
        # Portfolio overview
        portfolio = self.portfolio_analytics.get_portfolio_summary()
        
        # Growth metrics
        growth = self.get_growth_metrics()
        
        # Quality metrics
        quality = self.get_portfolio_quality()
        
        # Profitability
        profitability = self.get_profitability_metrics()
        
        # Risk indicators
        risk = self.get_risk_indicators()
        
        return {
            'portfolio': portfolio,
            'growth': growth,
            'quality': quality,
            'profitability': profitability,
            'risk': risk,
            'report_date': date.today(),
        }
    
    def get_growth_metrics(self):
        """Calculate growth metrics (MoM, YoY)"""
        
        today = date.today()
        
        # Current month
        current_month_start = date(today.year, today.month, 1)
        
        # Last month
        last_month_end = current_month_start - timedelta(days=1)
        last_month_start = date(last_month_end.year, last_month_end.month, 1)
        
        # Same month last year
        last_year_month = current_month_start - relativedelta(years=1)
        
        # Current portfolio
        current_portfolio = Loan.objects.filter(
            status='active'
        ).aggregate(
            total=Coalesce(Sum('principal'), Decimal('0'))
        )['total']
        
        # Last month portfolio
        last_month_portfolio = Loan.objects.filter(
            status='active',
            disbursed_date__lte=last_month_end
        ).aggregate(
            total=Coalesce(Sum('principal'), Decimal('0'))
        )['total']
        
        # Calculate MoM growth
        mom_growth = Decimal('0.00')
        if last_month_portfolio > 0:
            mom_growth = ((current_portfolio - last_month_portfolio) / last_month_portfolio) * 100
        
        # Client growth
        current_clients = Client.objects.filter(status='active').count()
        
        last_month_clients = Client.objects.filter(
            status='active',
            created_at__date__lte=last_month_end
        ).count()
        
        client_growth = Decimal('0.00')
        if last_month_clients > 0:
            client_growth = Decimal((current_clients - last_month_clients) / last_month_clients * 100)
        
        # New loans this month
        new_loans_count = Loan.objects.filter(
            disbursed_date__gte=current_month_start,
            disbursed_date__lte=today
        ).count()
        
        new_loans_value = Loan.objects.filter(
            disbursed_date__gte=current_month_start,
            disbursed_date__lte=today
        ).aggregate(
            total=Coalesce(Sum('principal'), Decimal('0'))
        )['total']
        
        return {
            'current_portfolio': current_portfolio,
            'mom_growth_rate': mom_growth,
            'current_clients': current_clients,
            'client_growth_rate': client_growth,
            'new_loans_count': new_loans_count,
            'new_loans_value': new_loans_value,
        }
    
    def get_portfolio_quality(self):
        """Portfolio quality indicators"""
        
        par = self.portfolio_analytics.get_par_metrics()
        
        # Calculate NPL ratio (Non-Performing Loans > 90 days)
        active_loans = Loan.objects.filter(status='active')
        
        total_outstanding = Decimal('0.00')
        for loan in active_loans:
            total_outstanding += loan.get_outstanding_balance()
        
        npl_ratio = Decimal('0.00')
        if total_outstanding > 0:
            npl_ratio = (par['par_90_value'] / total_outstanding) * 100
        
        # Write-off rate
        written_off = Loan.objects.filter(status='written_off').count()
        total_loans = Loan.objects.count()
        
        write_off_rate = Decimal('0.00')
        if total_loans > 0:
            write_off_rate = Decimal((written_off / total_loans) * 100)
        
        # Collection efficiency
        collection_efficiency = par.get('collection_efficiency', Decimal('0.00'))
        
        return {
            'par_30': par['par_30_rate'],
            'par_90': par['par_90_rate'],
            'npl_ratio': npl_ratio,
            'write_off_rate': write_off_rate,
            'collection_efficiency': collection_efficiency,
        }
    
    def get_profitability_metrics(self):
        """Calculate profitability indicators"""
        
        from management_reports.profit_loss import ProfitLossCalculator
        
        # Current month P&L
        today = date.today()
        month_start = date(today.year, today.month, 1)
        
        pl_calc = ProfitLossCalculator(month_start, today)
        pl = pl_calc.get_profit_loss_statement()
        
        # Calculate ROA (Return on Assets)
        total_assets = Loan.objects.filter(status='active').aggregate(
            total=Coalesce(Sum('principal'), Decimal('0'))
        )['total']
        
        roa = Decimal('0.00')
        if total_assets > 0:
            roa = (pl['gross_profit'] / total_assets) * 100
        
        # Calculate yield (interest income / portfolio)
        yield_rate = Decimal('0.00')
        if total_assets > 0:
            yield_rate = (pl['revenue']['interest_income'] / total_assets) * 100
        
        return {
            'revenue': pl['revenue']['total_revenue'],
            'expenses': pl['expenses']['total_expenses'],
            'profit': pl['gross_profit'],
            'profit_margin': pl['profit_margin'],
            'roa': roa,
            'portfolio_yield': yield_rate,
        }
    
    def get_risk_indicators(self):
        """Risk management indicators"""
        
        # Capital adequacy (simplified)
        active_loans_value = Loan.objects.filter(status='active').aggregate(
            total=Coalesce(Sum('principal'), Decimal('0'))
        )['total']
        
        # Concentration risk (top 10 clients)
        top_clients_exposure = Decimal('0.00')
        top_clients = Client.objects.annotate(
            total_loans=Sum('loans__principal', filter=Q(loans__status='active'))
        ).order_by('-total_loans')[:10]
        
        for client in top_clients:
            if client.total_loans:
                top_clients_exposure += client.total_loans
        
        concentration_ratio = Decimal('0.00')
        if active_loans_value > 0:
            concentration_ratio = (top_clients_exposure / active_loans_value) * 100
        
        # Loan loss provisions
        provisions = ProfitLossCalculator().calculate_loan_loss_provisions()
        
        provision_coverage = Decimal('0.00')
        if active_loans_value > 0:
            provision_coverage = (provisions / active_loans_value) * 100
        
        # Arrears trend (comparing last 3 months)
        arrears_trend = self.get_arrears_trend()
        
        return {
            'concentration_ratio': concentration_ratio,
            'provision_coverage': provision_coverage,
            'total_provisions': provisions,
            'arrears_trend': arrears_trend,
        }
    
    def get_arrears_trend(self):
        """Get 3-month arrears trend"""
        
        trends = []
        today = date.today()
        
        for i in range(3):
            # Calculate month
            month_date = today - relativedelta(months=i)
            month_start = date(month_date.year, month_date.month, 1)
            
            if month_date.month == 12:
                month_end = date(month_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(month_date.year, month_date.month + 1, 1) - timedelta(days=1)
            
            # Get PAR for that month
            arrears_loans = Loan.objects.filter(
                status='active',
                disbursed_date__lte=month_end,
                days_in_arrears__gt=0
            )
            
            arrears_value = Decimal('0.00')
            for loan in arrears_loans:
                arrears_value += loan.get_outstanding_balance()
            
            trends.insert(0, {
                'month': month_start.strftime('%B %Y'),
                'arrears_count': arrears_loans.count(),
                'arrears_value': arrears_value,
            })
        
        return trends
    
    def get_strategic_metrics(self):
        """Strategic performance indicators"""
        
        # Client retention rate (simplified)
        total_clients = Client.objects.count()
        active_clients = Client.objects.filter(status='active').count()
        
        retention_rate = Decimal('0.00')
        if total_clients > 0:
            retention_rate = Decimal((active_clients / total_clients) * 100)
        
        # Average loan size
        avg_loan = Loan.objects.filter(status='active').aggregate(
            avg=Avg('principal')
        )['avg'] or Decimal('0.00')
        
        # Loans per client
        active_borrowers = Client.objects.filter(
            loans__status='active'
        ).distinct().count()
        
        active_loans_count = Loan.objects.filter(status='active').count()
        
        loans_per_client = Decimal('0.00')
        if active_borrowers > 0:
            loans_per_client = Decimal(active_loans_count / active_borrowers)
        
        # Product distribution
        product_dist = LoanProduct.objects.annotate(
            loan_count=Count('loans', filter=Q(loans__status='active')),
            loan_value=Sum('loans__principal', filter=Q(loans__status='active'))
        ).values('name', 'loan_count', 'loan_value')
        
        return {
            'client_retention_rate': retention_rate,
            'average_loan_size': avg_loan,
            'loans_per_client': loans_per_client,
            'product_distribution': list(product_dist),
        }
