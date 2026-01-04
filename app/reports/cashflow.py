"""
Cash Flow Projections for Microfinance MIS
Predicts expected payments and revenue for planning purposes
"""
from decimal import Decimal
from datetime import date, timedelta
from django.db.models import Sum, Q
from collections import defaultdict

from loans.models import Loan, LoanSchedule


class CashFlowProjections:
    """Generate cash flow projections based on loan schedules."""
    
    def __init__(self):
        pass
    
    def get_expected_payments(self, days_ahead=30):
        """
        Get expected payments for the next N days.
        Returns daily breakdown of expected principal, interest, and total.
        """
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        
        # Get all schedule entries due within the period for active loans
        schedule_entries = LoanSchedule.objects.filter(
            loan__status='active',
            due_date__gte=today,
            due_date__lte=end_date,
            is_paid=False
        ).select_related('loan').order_by('due_date')
        
        # Group by date
        daily_projections = defaultdict(lambda: {
            'date': None,
            'principal': Decimal('0.00'),
            'interest': Decimal('0.00'),
            'penalty': Decimal('0.00'),
            'total': Decimal('0.00'),
            'loan_count': 0,
        })
        
        for entry in schedule_entries:
            date_key = entry.due_date.strftime('%Y-%m-%d')
            
            # Calculate outstanding amounts
            principal_due = entry.principal_due - entry.principal_paid
            interest_due = entry.interest_due - entry.interest_paid
            penalty_due = entry.penalty_due - entry.penalty_paid
            
            daily_projections[date_key]['date'] = entry.due_date
            daily_projections[date_key]['principal'] += principal_due
            daily_projections[date_key]['interest'] += interest_due
            daily_projections[date_key]['penalty'] += penalty_due
            daily_projections[date_key]['total'] += (principal_due + interest_due + penalty_due)
            daily_projections[date_key]['loan_count'] += 1
        
        # Convert to sorted list
        projections = sorted(daily_projections.values(), key=lambda x: x['date'])
        
        return projections
    
    def get_monthly_projections(self, months_ahead=12):
        """
        Get monthly revenue projections for the next N months.
        """
        today = date.today()
        projections = []
        
        for month_offset in range(months_ahead):
            # Calculate month range
            if month_offset == 0:
                start_date = today
            else:
                start_date = date(
                    today.year + (today.month + month_offset - 1) // 12,
                    (today.month + month_offset - 1) % 12 + 1,
                    1
                )
            
            # End date is last day of the month
            if start_date.month == 12:
                end_date = date(start_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(start_date.year, start_date.month + 1, 1) - timedelta(days=1)
            
            # Get schedule entries for this month
            entries = LoanSchedule.objects.filter(
                loan__status='active',
                due_date__gte=start_date,
                due_date__lte=end_date,
                is_paid=False
            ).aggregate(
                principal=Sum('principal_due') - Sum('principal_paid'),
                interest=Sum('interest_due') - Sum('interest_paid'),
                penalty=Sum('penalty_due') - Sum('penalty_paid'),
            )
            
            principal = entries['principal'] or Decimal('0.00')
            interest = entries['interest'] or Decimal('0.00')
            penalty = entries['penalty'] or Decimal('0.00')
            total = principal + interest + penalty
            
            # Count loans
            loan_count = LoanSchedule.objects.filter(
                loan__status='active',
                due_date__gte=start_date,
                due_date__lte=end_date,
                is_paid=False
            ).values('loan').distinct().count()
            
            projections.append({
                'month': start_date.strftime('%B %Y'),
                'start_date': start_date,
                'end_date': end_date,
                'principal': principal,
                'interest': interest,
                'penalty': penalty,
                'total': total,
                'loan_count': loan_count,
            })
        
        return projections
    
    def get_collection_forecast(self, days_ahead=30):
        """
        Forecast collection efficiency based on historical performance.
        """
        from repayments.models import Repayment
        
        # Calculate historical collection rate (last 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        
        # Expected payments (from schedule)
        expected = LoanSchedule.objects.filter(
            loan__status='active',
            due_date__gte=thirty_days_ago,
            due_date__lt=date.today()
        ).aggregate(
            total=Sum('total_due')
        )['total'] or Decimal('0.00')
        
        # Actual collections
        actual = Repayment.objects.filter(
            status='confirmed',
            paid_on__gte=thirty_days_ago,
            paid_on__lt=date.today()
        ).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Collection rate
        collection_rate = (actual / expected * 100) if expected > 0 else Decimal('100.00')
        
        # Get future expected payments
        future_expected = self.get_expected_payments(days_ahead)
        
        total_expected = sum(day['total'] for day in future_expected)
        forecasted_collection = total_expected * (collection_rate / 100)
        
        return {
            'days_ahead': days_ahead,
            'historical_collection_rate': collection_rate,
            'expected_payments': total_expected,
            'forecasted_collection': forecasted_collection,
            'potential_shortfall': total_expected - forecasted_collection,
            'daily_breakdown': future_expected,
        }
    
    def get_portfolio_growth_projection(self, months_ahead=12):
        """
        Project portfolio growth based on current trends.
        """
        from clients.models import Client
        
        # Current portfolio
        active_loans = Loan.objects.filter(status='active')
        current_portfolio = sum(loan.get_outstanding_balance() for loan in active_loans)
        
        # Calculate monthly reduction (principal payments)
        projections = self.get_monthly_projections(months_ahead)
        
        portfolio_projection = []
        running_portfolio = current_portfolio
        
        for month_data in projections:
            # Reduce by expected principal payments
            running_portfolio -= month_data['principal']
            
            # Ensure it doesn't go negative
            if running_portfolio < 0:
                running_portfolio = Decimal('0.00')
            
            portfolio_projection.append({
                'month': month_data['month'],
                'projected_portfolio': running_portfolio,
                'principal_reduction': month_data['principal'],
                'interest_revenue': month_data['interest'],
            })
        
        return {
            'current_portfolio': current_portfolio,
            'months_ahead': months_ahead,
            'projections': portfolio_projection,
        }
    
    def get_arrears_risk_forecast(self, days_ahead=30):
        """
        Forecast potential arrears risk based on loan classifications.
        """
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        
        # Get loans by classification
        classifications = ['current', 'substandard', 'doubtful', 'loss']
        
        risk_forecast = {}
        
        for classification in classifications:
            loans = Loan.objects.filter(
                status='active',
                classification=classification
            )
            
            # Get upcoming payments for these loans
            upcoming = LoanSchedule.objects.filter(
                loan__in=loans,
                due_date__gte=today,
                due_date__lte=end_date,
                is_paid=False
            ).aggregate(
                total=Sum('total_due')
            )['total'] or Decimal('0.00')
            
            # Assign risk probability based on classification
            risk_probabilities = {
                'current': 0.05,      # 5% risk
                'substandard': 0.25,  # 25% risk
                'doubtful': 0.50,     # 50% risk
                'loss': 0.90,         # 90% risk
            }
            
            risk_prob = risk_probabilities.get(classification, 0.0)
            at_risk_amount = upcoming * Decimal(str(risk_prob))
            
            risk_forecast[classification] = {
                'loan_count': loans.count(),
                'upcoming_payments': upcoming,
                'risk_probability': risk_prob * 100,
                'at_risk_amount': at_risk_amount,
            }
        
        # Total risk
        total_upcoming = sum(data['upcoming_payments'] for data in risk_forecast.values())
        total_at_risk = sum(data['at_risk_amount'] for data in risk_forecast.values())
        
        return {
            'days_ahead': days_ahead,
            'total_upcoming_payments': total_upcoming,
            'total_at_risk': total_at_risk,
            'overall_risk_rate': (total_at_risk / total_upcoming * 100) if total_upcoming > 0 else Decimal('0.00'),
            'by_classification': risk_forecast,
        }
