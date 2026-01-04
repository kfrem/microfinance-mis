"""
Dashboard views for analytics and reporting
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import JsonResponse
from .analytics import PortfolioAnalytics, ReportGenerator


@staff_member_required
def executive_dashboard(request):
    """Main executive dashboard view"""
    analytics = PortfolioAnalytics()
    
    context = {
        'summary': analytics.get_portfolio_summary(),
        'par_metrics': analytics.get_par_metrics(),
        'bog_classification': analytics.get_bog_classification(),
        'product_performance': analytics.get_loan_product_performance(),
        'client_stats': analytics.get_client_statistics(),
        'arrears_aging': analytics.get_arrears_aging(),
    }
    
    return render(request, 'dashboard/executive_dashboard.html', context)


@staff_member_required
def portfolio_report(request):
    """Detailed portfolio quality report"""
    report = ReportGenerator.generate_portfolio_quality_report()
    return render(request, 'dashboard/portfolio_report.html', {'report': report})


@staff_member_required
def bog_report(request):
    """BoG prudential report"""
    report = ReportGenerator.generate_bog_prudential_report()
    return render(request, 'dashboard/bog_report.html', {'report': report})


@staff_member_required
def api_dashboard_data(request):
    """API endpoint for dashboard data (for charts)"""
    analytics = PortfolioAnalytics()
    
    data = {
        'summary': analytics.get_portfolio_summary(),
        'par_metrics': analytics.get_par_metrics(),
        'trends': analytics.get_repayment_trends(days=30),
    }
    
    # Convert Decimal to float for JSON serialization
    def decimal_to_float(obj):
        if isinstance(obj, dict):
            return {k: decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [decimal_to_float(item) for item in obj]
        elif hasattr(obj, '__iter__') and not isinstance(obj, str):
            return [decimal_to_float(item) for item in obj]
        elif isinstance(obj, Decimal):
            return float(obj)
        return obj
    
    from decimal import Decimal
    data = decimal_to_float(data)
    
    return JsonResponse(data)
