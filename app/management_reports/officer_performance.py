"""
Loan Officer Performance Tracking
Monitor individual loan officer productivity, portfolio quality, and targets
"""
from decimal import Decimal
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Count, Q, Avg
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User

from loans.models import Loan
from repayments.models import Repayment
from clients.models import Client


class LoanOfficerPerformance:
    """Track and analyze loan officer performance"""
    
    def __init__(self, officer=None, start_date=None, end_date=None):
        """
        Initialize with optional officer filter and date range
        """
        self.officer = officer
        
        if not start_date:
            today = date.today()
            start_date = date(today.year, today.month, 1)
        if not end_date:
            end_date = date.today()
        
        self.start_date = start_date
        self.end_date = end_date
    
    def get_officer_summary(self, officer_id):
        """Get comprehensive summary for specific officer"""
        
        try:
            officer = User.objects.get(id=officer_id)
        except User.DoesNotExist:
            return None
        
        # Disbursements
        disbursements = self.get_disbursements(officer)
        
        # Collections
        collections = self.get_collections(officer)
        
        # Portfolio quality
        quality = self.get_portfolio_quality(officer)
        
        # Client management
        clients = self.get_client_metrics(officer)
        
        return {
            'officer': {
                'id': officer.id,
                'name': officer.get_full_name() or officer.username,
                'username': officer.username,
            },
            'period_start': self.start_date,
            'period_end': self.end_date,
            'disbursements': disbursements,
            'collections': collections,
            'quality': quality,
            'clients': clients,
        }
    
    def get_disbursements(self, officer):
        """Track loan disbursements by officer"""
        
        # Loans disbursed by this officer in period
        disbursed_loans = Loan.objects.filter(
            disbursed_by=officer,
            disbursed_date__gte=self.start_date,
            disbursed_date__lte=self.end_date,
            status__in=['active', 'closed']
        )
        
        count = disbursed_loans.count()
        
        total_value = disbursed_loans.aggregate(
            total=Coalesce(Sum('principal'), Decimal('0'))
        )['total']
        
        avg_loan_size = disbursed_loans.aggregate(
            avg=Avg('principal')
        )['avg'] or Decimal('0.00')
        
        # Approved loans (awaiting disbursement)
        approved_loans = Loan.objects.filter(
            approved_by=officer,
            approved_date__gte=self.start_date,
            approved_date__lte=self.end_date,
            status='approved'
        ).count()
        
        return {
            'loans_disbursed': count,
            'total_value': total_value,
            'average_loan_size': avg_loan_size,
            'loans_approved_pending': approved_loans,
        }
    
    def get_collections(self, officer):
        """Track collections by officer"""
        
        # Get loans managed by this officer
        officer_loans = Loan.objects.filter(
            Q(disbursed_by=officer) | Q(approved_by=officer)
        ).values_list('id', flat=True)
        
        # Repayments received by this officer
        collections = Repayment.objects.filter(
            received_by=officer,
            status='confirmed',
            paid_on__gte=self.start_date,
            paid_on__lte=self.end_date
        ).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0')),
            count=Count('id')
        )
        
        # Target (for now, we'll estimate based on schedule)
        # In production, this would come from targets set by management
        expected_collections = Decimal('0.00')  # Would be set monthly
        
        collection_rate = Decimal('100.00')  # Placeholder
        
        return {
            'amount_collected': collections['total'],
            'payments_received': collections['count'],
            'expected_collections': expected_collections,
            'collection_rate': collection_rate,
        }
    
    def get_portfolio_quality(self, officer):
        """Assess portfolio quality for officer"""
        
        # Get active loans managed by officer
        active_loans = Loan.objects.filter(
            Q(disbursed_by=officer) | Q(approved_by=officer),
            status='active'
        )
        
        total_loans = active_loans.count()
        
        # Calculate total outstanding
        total_outstanding = Decimal('0.00')
        arrears_value = Decimal('0.00')
        
        for loan in active_loans:
            outstanding = loan.get_outstanding_balance()
            total_outstanding += outstanding
            
            if loan.days_in_arrears > 30:
                arrears_value += outstanding
        
        # PAR 30 rate
        par_30_rate = Decimal('0.00')
        if total_outstanding > 0:
            par_30_rate = (arrears_value / total_outstanding) * 100
        
        # Loans in arrears
        arrears_count = active_loans.filter(days_in_arrears__gt=0).count()
        
        # Classification breakdown
        current = active_loans.filter(classification='current').count()
        substandard = active_loans.filter(classification='substandard').count()
        doubtful = active_loans.filter(classification='doubtful').count()
        loss = active_loans.filter(classification='loss').count()
        
        return {
            'total_active_loans': total_loans,
            'total_outstanding': total_outstanding,
            'loans_in_arrears': arrears_count,
            'arrears_value': arrears_value,
            'par_30_rate': par_30_rate,
            'classification': {
                'current': current,
                'substandard': substandard,
                'doubtful': doubtful,
                'loss': loss,
            }
        }
    
    def get_client_metrics(self, officer):
        """Track client management metrics"""
        
        # Clients created by officer
        new_clients = Client.objects.filter(
            created_by=officer,
            created_at__date__gte=self.start_date,
            created_at__date__lte=self.end_date
        ).count()
        
        # Total clients managed
        total_clients = Client.objects.filter(
            created_by=officer,
            status='active'
        ).count()
        
        # Clients with KYC verified
        kyc_verified = Client.objects.filter(
            kyc_verified_by=officer,
            kyc_verified=True
        ).count()
        
        return {
            'new_clients': new_clients,
            'total_active_clients': total_clients,
            'kyc_verified': kyc_verified,
        }
    
    def get_all_officers_ranking(self):
        """Get performance ranking for all loan officers"""
        
        # Get all users who have disbursed or approved loans
        officers = User.objects.filter(
            Q(disbursed_loans__isnull=False) | Q(approved_loans__isnull=False)
        ).distinct()
        
        rankings = []
        
        for officer in officers:
            summary = self.get_officer_summary(officer.id)
            
            if summary:
                # Calculate performance score (simplified)
                score = self.calculate_performance_score(summary)
                
                rankings.append({
                    'officer': summary['officer'],
                    'disbursements_value': summary['disbursements']['total_value'],
                    'collections': summary['collections']['amount_collected'],
                    'par_30': summary['quality']['par_30_rate'],
                    'new_clients': summary['clients']['new_clients'],
                    'performance_score': score,
                })
        
        # Sort by performance score
        rankings.sort(key=lambda x: x['performance_score'], reverse=True)
        
        return rankings
    
    def calculate_performance_score(self, summary):
        """
        Calculate overall performance score
        Weighted combination of metrics
        """
        
        # Weights (total should be 100)
        weights = {
            'disbursements': 30,
            'collections': 30,
            'quality': 25,
            'clients': 15,
        }
        
        score = Decimal('0.00')
        
        # Disbursement score (based on value)
        disbursement_value = summary['disbursements']['total_value']
        if disbursement_value > 0:
            # Scale to 0-100 (assuming 100,000 GHS is excellent)
            disb_score = min((disbursement_value / Decimal('100000')) * 100, Decimal('100'))
            score += (disb_score * weights['disbursements']) / 100
        
        # Collection score (based on amount)
        collection_value = summary['collections']['amount_collected']
        if collection_value > 0:
            # Scale to 0-100 (assuming 80,000 GHS is excellent)
            coll_score = min((collection_value / Decimal('80000')) * 100, Decimal('100'))
            score += (coll_score * weights['collections']) / 100
        
        # Quality score (inverse of PAR 30)
        par_30 = summary['quality']['par_30_rate']
        quality_score = max(Decimal('100') - par_30, Decimal('0'))
        score += (quality_score * weights['quality']) / 100
        
        # Client acquisition score
        new_clients = summary['clients']['new_clients']
        if new_clients > 0:
            # Scale to 0-100 (assuming 20 new clients is excellent)
            client_score = min((Decimal(new_clients) / Decimal('20')) * 100, Decimal('100'))
            score += (client_score * weights['clients']) / 100
        
        return round(score, 2)
    
    def get_daily_performance(self):
        """Get today's performance for all officers"""
        
        today = date.today()
        
        self.start_date = today
        self.end_date = today
        
        return self.get_all_officers_ranking()
