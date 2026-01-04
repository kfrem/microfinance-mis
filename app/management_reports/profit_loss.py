"""
Profit & Loss Statement Generator
Calculates revenue, expenses, and net profit for management accounting
"""
from decimal import Decimal
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce

from loans.models import Loan, LoanProduct
from repayments.models import Repayment
from clients.models import Client


class ProfitLossCalculator:
    """Generate Profit & Loss statements for microfinance operations"""
    
    def __init__(self, start_date=None, end_date=None):
        """
        Initialize with date range
        If not provided, defaults to current month
        """
        if not start_date:
            today = date.today()
            start_date = date(today.year, today.month, 1)
        if not end_date:
            end_date = date.today()
        
        self.start_date = start_date
        self.end_date = end_date
    
    def get_revenue(self):
        """Calculate total revenue breakdown"""
        
        # Interest income from repayments
        interest_income = Repayment.objects.filter(
            status='confirmed',
            paid_on__gte=self.start_date,
            paid_on__lte=self.end_date
        ).aggregate(
            total=Coalesce(Sum('interest_paid'), Decimal('0'))
        )['total']
        
        # Processing fees from loans disbursed in period
        processing_fees = Loan.objects.filter(
            disbursed_date__gte=self.start_date,
            disbursed_date__lte=self.end_date,
            status__in=['active', 'closed']
        ).aggregate(
            total=Coalesce(Sum('processing_fee'), Decimal('0'))
        )['total']
        
        # Insurance fees
        insurance_fees = Loan.objects.filter(
            disbursed_date__gte=self.start_date,
            disbursed_date__lte=self.end_date,
            status__in=['active', 'closed']
        ).aggregate(
            total=Coalesce(Sum('insurance_fee'), Decimal('0'))
        )['total']
        
        # Penalty income
        penalty_income = Repayment.objects.filter(
            status='confirmed',
            paid_on__gte=self.start_date,
            paid_on__lte=self.end_date
        ).aggregate(
            total=Coalesce(Sum('penalty_paid'), Decimal('0'))
        )['total']
        
        total_revenue = (
            interest_income + 
            processing_fees + 
            insurance_fees + 
            penalty_income
        )
        
        return {
            'interest_income': interest_income,
            'processing_fees': processing_fees,
            'insurance_fees': insurance_fees,
            'penalty_income': penalty_income,
            'total_revenue': total_revenue,
        }
    
    def get_expenses(self):
        """
        Calculate operating expenses
        Note: This is a simplified version. In production, you'd integrate
        with an accounting system or expense tracking module.
        """
        
        # For now, we'll calculate provisions as an expense
        provisions = self.calculate_loan_loss_provisions()
        
        # Placeholder for other expenses
        # In production, these would come from an expense tracking module
        staff_salaries = Decimal('0.00')  # Would come from HR/Payroll system
        rent_utilities = Decimal('0.00')   # Would come from accounting
        marketing = Decimal('0.00')        # Would come from accounting
        administrative = Decimal('0.00')   # Would come from accounting
        
        total_expenses = (
            provisions +
            staff_salaries +
            rent_utilities +
            marketing +
            administrative
        )
        
        return {
            'loan_loss_provisions': provisions,
            'staff_salaries': staff_salaries,
            'rent_utilities': rent_utilities,
            'marketing': marketing,
            'administrative': administrative,
            'total_expenses': total_expenses,
        }
    
    def calculate_loan_loss_provisions(self):
        """Calculate required loan loss provisions based on BoG standards"""
        
        # Get active loans at end of period
        active_loans = Loan.objects.filter(
            status='active',
            disbursed_date__lte=self.end_date
        )
        
        total_provisions = Decimal('0.00')
        
        provision_rates = {
            'current': Decimal('0.01'),      # 1%
            'substandard': Decimal('0.10'),  # 10%
            'doubtful': Decimal('0.50'),     # 50%
            'loss': Decimal('1.00'),         # 100%
        }
        
        for loan in active_loans:
            outstanding = loan.get_outstanding_balance()
            rate = provision_rates.get(loan.classification, Decimal('0.01'))
            total_provisions += outstanding * rate
        
        return total_provisions
    
    def get_profit_loss_statement(self):
        """Generate complete P&L statement"""
        
        revenue = self.get_revenue()
        expenses = self.get_expenses()
        
        gross_profit = revenue['total_revenue'] - expenses['total_expenses']
        
        # Calculate profit margin
        profit_margin = (
            (gross_profit / revenue['total_revenue'] * 100)
            if revenue['total_revenue'] > 0 else Decimal('0.00')
        )
        
        return {
            'period_start': self.start_date,
            'period_end': self.end_date,
            'revenue': revenue,
            'expenses': expenses,
            'gross_profit': gross_profit,
            'profit_margin': profit_margin,
        }
    
    def get_comparative_pl(self, periods=3):
        """
        Get comparative P&L for multiple months
        Returns list of P&L statements for comparison
        """
        statements = []
        
        # Start from N months ago
        current_start = self.start_date - relativedelta(months=periods-1)
        
        for i in range(periods):
            period_start = date(current_start.year, current_start.month, 1)
            
            # Last day of month
            if current_start.month == 12:
                period_end = date(current_start.year + 1, 1, 1) - timedelta(days=1)
            else:
                period_end = date(current_start.year, current_start.month + 1, 1) - timedelta(days=1)
            
            # Don't go beyond today
            if period_end > date.today():
                period_end = date.today()
            
            # Calculate P&L for this period
            pl_calc = ProfitLossCalculator(period_start, period_end)
            statement = pl_calc.get_profit_loss_statement()
            statement['period_name'] = period_start.strftime('%B %Y')
            
            statements.append(statement)
            
            # Move to next month
            current_start = current_start + relativedelta(months=1)
        
        return statements
    
    def get_daily_summary(self):
        """Get daily operations summary"""
        
        # Today's collections
        today_collections = Repayment.objects.filter(
            status='confirmed',
            paid_on=date.today()
        ).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']
        
        # Today's disbursements
        today_disbursements = Loan.objects.filter(
            disbursed_date=date.today(),
            status__in=['active', 'closed']
        ).aggregate(
            total=Coalesce(Sum('principal'), Decimal('0'))
        )['total']
        
        # Today's new clients
        today_clients = Client.objects.filter(
            created_at__date=date.today()
        ).count()
        
        # Today's new loans (applications)
        today_loans = Loan.objects.filter(
            application_date=date.today()
        ).count()
        
        # Today's approvals
        today_approvals = Loan.objects.filter(
            approved_date=date.today()
        ).count()
        
        return {
            'date': date.today(),
            'collections': today_collections,
            'disbursements': today_disbursements,
            'net_cash_flow': today_collections - today_disbursements,
            'new_clients': today_clients,
            'new_applications': today_loans,
            'approvals': today_approvals,
        }
    
    def get_weekly_summary(self):
        """Get weekly operations summary"""
        
        # Last 7 days
        week_start = date.today() - timedelta(days=7)
        week_end = date.today()
        
        # Week's collections
        week_collections = Repayment.objects.filter(
            status='confirmed',
            paid_on__gte=week_start,
            paid_on__lte=week_end
        ).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']
        
        # Week's disbursements
        week_disbursements = Loan.objects.filter(
            disbursed_date__gte=week_start,
            disbursed_date__lte=week_end,
            status__in=['active', 'closed']
        ).aggregate(
            total=Coalesce(Sum('principal'), Decimal('0'))
        )['total']
        
        # Week's new clients
        week_clients = Client.objects.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=week_end
        ).count()
        
        # Week's new loans
        week_loans = Loan.objects.filter(
            application_date__gte=week_start,
            application_date__lte=week_end
        ).count()
        
        # Week's approvals
        week_approvals = Loan.objects.filter(
            approved_date__gte=week_start,
            approved_date__lte=week_end
        ).count()
        
        # Week's revenue
        week_interest = Repayment.objects.filter(
            status='confirmed',
            paid_on__gte=week_start,
            paid_on__lte=week_end
        ).aggregate(
            total=Coalesce(Sum('interest_paid'), Decimal('0'))
        )['total']
        
        week_fees = Loan.objects.filter(
            disbursed_date__gte=week_start,
            disbursed_date__lte=week_end
        ).aggregate(
            processing=Coalesce(Sum('processing_fee'), Decimal('0')),
            insurance=Coalesce(Sum('insurance_fee'), Decimal('0'))
        )
        
        week_revenue = (
            week_interest + 
            week_fees['processing'] + 
            week_fees['insurance']
        )
        
        return {
            'week_start': week_start,
            'week_end': week_end,
            'collections': week_collections,
            'disbursements': week_disbursements,
            'net_cash_flow': week_collections - week_disbursements,
            'new_clients': week_clients,
            'new_applications': week_loans,
            'approvals': week_approvals,
            'revenue': week_revenue,
        }
