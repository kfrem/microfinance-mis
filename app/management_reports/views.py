"""
Management Reports Views
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from .profit_loss import ProfitLossCalculator
from .board_analytics import BoardAnalytics
from .officer_performance import LoanOfficerPerformance


def management_dashboard(request):
    """Main management dashboard"""
    return render(request, 'management_reports/management_dashboard.html')


def board_dashboard(request):
    """Board-level executive dashboard"""
    return render(request, 'management_reports/board_dashboard.html')


def profit_loss_report(request):
    """Profit & Loss statement view"""
    return render(request, 'management_reports/profit_loss.html')


def officer_performance_dashboard(request):
    """Loan officer performance dashboard"""
    return render(request, 'management_reports/officer_performance.html')


# API Endpoints

@require_http_methods(["GET"])
def api_profit_loss(request):
    """API endpoint for P&L data"""
    
    # Get date range from params
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    start_date = None
    end_date = None
    
    if start_date_str:
        start_date = date.fromisoformat(start_date_str)
    if end_date_str:
        end_date = date.fromisoformat(end_date_str)
    
    pl_calc = ProfitLossCalculator(start_date, end_date)
    statement = pl_calc.get_profit_loss_statement()
    
    # Convert Decimals to floats for JSON
    return JsonResponse({
        'period_start': statement['period_start'].isoformat(),
        'period_end': statement['period_end'].isoformat(),
        'revenue': {
            'interest_income': float(statement['revenue']['interest_income']),
            'processing_fees': float(statement['revenue']['processing_fees']),
            'insurance_fees': float(statement['revenue']['insurance_fees']),
            'penalty_income': float(statement['revenue']['penalty_income']),
            'total_revenue': float(statement['revenue']['total_revenue']),
        },
        'expenses': {
            'loan_loss_provisions': float(statement['expenses']['loan_loss_provisions']),
            'staff_salaries': float(statement['expenses']['staff_salaries']),
            'rent_utilities': float(statement['expenses']['rent_utilities']),
            'marketing': float(statement['expenses']['marketing']),
            'administrative': float(statement['expenses']['administrative']),
            'total_expenses': float(statement['expenses']['total_expenses']),
        },
        'gross_profit': float(statement['gross_profit']),
        'profit_margin': float(statement['profit_margin']),
    })


@require_http_methods(["GET"])
def api_comparative_pl(request):
    """API endpoint for comparative P&L"""
    
    periods = int(request.GET.get('periods', 3))
    
    pl_calc = ProfitLossCalculator()
    statements = pl_calc.get_comparative_pl(periods)
    
    result = []
    for stmt in statements:
        result.append({
            'period_name': stmt['period_name'],
            'period_start': stmt['period_start'].isoformat(),
            'period_end': stmt['period_end'].isoformat(),
            'revenue': float(stmt['revenue']['total_revenue']),
            'expenses': float(stmt['expenses']['total_expenses']),
            'profit': float(stmt['gross_profit']),
            'margin': float(stmt['profit_margin']),
        })
    
    return JsonResponse({'statements': result})


@require_http_methods(["GET"])
def api_daily_summary(request):
    """API endpoint for daily operations summary"""
    
    pl_calc = ProfitLossCalculator()
    summary = pl_calc.get_daily_summary()
    
    return JsonResponse({
        'date': summary['date'].isoformat(),
        'collections': float(summary['collections']),
        'disbursements': float(summary['disbursements']),
        'net_cash_flow': float(summary['net_cash_flow']),
        'new_clients': summary['new_clients'],
        'new_applications': summary['new_applications'],
        'approvals': summary['approvals'],
    })


@require_http_methods(["GET"])
def api_weekly_summary(request):
    """API endpoint for weekly operations summary"""
    
    pl_calc = ProfitLossCalculator()
    summary = pl_calc.get_weekly_summary()
    
    return JsonResponse({
        'week_start': summary['week_start'].isoformat(),
        'week_end': summary['week_end'].isoformat(),
        'collections': float(summary['collections']),
        'disbursements': float(summary['disbursements']),
        'net_cash_flow': float(summary['net_cash_flow']),
        'new_clients': summary['new_clients'],
        'new_applications': summary['new_applications'],
        'approvals': summary['approvals'],
        'revenue': float(summary['revenue']),
    })


@require_http_methods(["GET"])
def api_board_summary(request):
    """API endpoint for board-level executive summary"""
    
    board = BoardAnalytics()
    summary = board.get_executive_summary()
    
    return JsonResponse({
        'report_date': summary['report_date'].isoformat(),
        'portfolio': {
            'total_portfolio_value': float(summary['portfolio']['total_portfolio_value']),
            'total_outstanding': float(summary['portfolio']['total_outstanding']),
            'active_loans_count': summary['portfolio']['active_loans_count'],
            'collection_rate': float(summary['portfolio']['collection_rate']),
        },
        'growth': {
            'current_portfolio': float(summary['growth']['current_portfolio']),
            'mom_growth_rate': float(summary['growth']['mom_growth_rate']),
            'current_clients': summary['growth']['current_clients'],
            'client_growth_rate': float(summary['growth']['client_growth_rate']),
            'new_loans_count': summary['growth']['new_loans_count'],
            'new_loans_value': float(summary['growth']['new_loans_value']),
        },
        'quality': {
            'par_30': float(summary['quality']['par_30']),
            'par_90': float(summary['quality']['par_90']),
            'npl_ratio': float(summary['quality']['npl_ratio']),
            'write_off_rate': float(summary['quality']['write_off_rate']),
        },
        'profitability': {
            'revenue': float(summary['profitability']['revenue']),
            'expenses': float(summary['profitability']['expenses']),
            'profit': float(summary['profitability']['profit']),
            'profit_margin': float(summary['profitability']['profit_margin']),
            'roa': float(summary['profitability']['roa']),
            'portfolio_yield': float(summary['profitability']['portfolio_yield']),
        },
        'risk': {
            'concentration_ratio': float(summary['risk']['concentration_ratio']),
            'provision_coverage': float(summary['risk']['provision_coverage']),
            'total_provisions': float(summary['risk']['total_provisions']),
            'arrears_trend': [
                {
                    'month': trend['month'],
                    'arrears_count': trend['arrears_count'],
                    'arrears_value': float(trend['arrears_value']),
                }
                for trend in summary['risk']['arrears_trend']
            ],
        },
    })


@require_http_methods(["GET"])
def api_officer_ranking(request):
    """API endpoint for loan officer performance ranking"""
    
    officer_perf = LoanOfficerPerformance()
    rankings = officer_perf.get_all_officers_ranking()
    
    result = []
    for rank in rankings:
        result.append({
            'officer_id': rank['officer']['id'],
            'officer_name': rank['officer']['name'],
            'disbursements_value': float(rank['disbursements_value']),
            'collections': float(rank['collections']),
            'par_30': float(rank['par_30']),
            'new_clients': rank['new_clients'],
            'performance_score': float(rank['performance_score']),
        })
    
    return JsonResponse({'rankings': result})


@require_http_methods(["GET"])
def api_officer_detail(request, officer_id):
    """API endpoint for specific officer performance"""
    
    officer_perf = LoanOfficerPerformance()
    summary = officer_perf.get_officer_summary(officer_id)
    
    if not summary:
        return JsonResponse({'error': 'Officer not found'}, status=404)
    
    return JsonResponse({
        'officer': summary['officer'],
        'period_start': summary['period_start'].isoformat(),
        'period_end': summary['period_end'].isoformat(),
        'disbursements': {
            'loans_disbursed': summary['disbursements']['loans_disbursed'],
            'total_value': float(summary['disbursements']['total_value']),
            'average_loan_size': float(summary['disbursements']['average_loan_size']),
            'loans_approved_pending': summary['disbursements']['loans_approved_pending'],
        },
        'collections': {
            'amount_collected': float(summary['collections']['amount_collected']),
            'payments_received': summary['collections']['payments_received'],
            'collection_rate': float(summary['collections']['collection_rate']),
        },
        'quality': {
            'total_active_loans': summary['quality']['total_active_loans'],
            'total_outstanding': float(summary['quality']['total_outstanding']),
            'loans_in_arrears': summary['quality']['loans_in_arrears'],
            'arrears_value': float(summary['quality']['arrears_value']),
            'par_30_rate': float(summary['quality']['par_30_rate']),
            'classification': summary['quality']['classification'],
        },
        'clients': summary['clients'],
    })
