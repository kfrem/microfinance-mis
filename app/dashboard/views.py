"""
Dashboard views for analytics and reporting
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from decimal import Decimal


def executive_dashboard(request):
    """Main executive dashboard view - simplified"""
    
    # Import models here
    from loans.models import Loan
    from repayments.models import Repayment
    from clients.models import Client
    
    # Calculate basic metrics
    active_loans = Loan.objects.filter(status='active')
    
    total_portfolio = active_loans.aggregate(
        total=Sum('principal')
    )['total'] or 0
    
    total_outstanding = sum(
        loan.get_outstanding_balance() 
        for loan in active_loans
    )
    
    disbursed = Loan.objects.filter(
        status__in=['active', 'closed']
    ).aggregate(total=Sum('principal'))['total'] or 0
    
    collected = Repayment.objects.filter(
        status='confirmed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    collection_rate = (collected / disbursed * 100) if disbursed > 0 else 0
    
    # PAR 30
    par_30_loans = active_loans.filter(days_in_arrears__gte=30)
    par_30_value = sum(loan.get_outstanding_balance() for loan in par_30_loans)
    par_30_percentage = (par_30_value / total_outstanding * 100) if total_outstanding > 0 else 0
    
    context = {
        'summary': {
            'total_portfolio_value': total_portfolio,
            'total_outstanding': total_outstanding,
            'active_loans': active_loans.count(),
            'collection_rate': round(collection_rate, 2),
        },
        'par_metrics': {
            'par_30_value': par_30_value,
            'par_30_percentage': round(par_30_percentage, 2),
        },
        'client_stats': {
            'total_clients': Client.objects.count(),
            'active_clients': Client.objects.filter(status='active').count(),
        },
    }
    
    return render(request, 'dashboard/executive_dashboard.html', context)


def portfolio_report(request):
    """Detailed portfolio quality report"""
    context = {
        'title': 'Portfolio Quality Report',
    }
    return render(request, 'dashboard/portfolio_report.html', context)


def bog_report(request):
    """BoG prudential report"""
    context = {
        'title': 'Bank of Ghana Prudential Report',
    }
    return render(request, 'dashboard/bog_report.html', context)


def api_dashboard_data(request):
    """API endpoint for dashboard data (for charts)"""
    
    from loans.models import Loan
    from repayments.models import Repayment
    
    active_loans = Loan.objects.filter(status='active')
    
    total_portfolio = active_loans.aggregate(total=Sum('principal'))['total'] or 0
    total_outstanding = sum(loan.get_outstanding_balance() for loan in active_loans)
    
    data = {
        'summary': {
            'total_portfolio_value': float(total_portfolio),
            'total_outstanding': float(total_outstanding),
            'active_loans': active_loans.count(),
        },
    }
    
    return JsonResponse(data)
