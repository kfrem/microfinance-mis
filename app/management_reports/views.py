"""
Management Reports Views
Simplified version to avoid import errors
"""
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from datetime import date, timedelta
from decimal import Decimal

# Import analytics from reports app
import sys
sys.path.append('/app/reports')


def management_dashboard(request):
    """Main management dashboard with KPI metrics"""
    
    # Import here to avoid circular imports
    from reports.analytics import PortfolioAnalytics
    
    analytics = PortfolioAnalytics()
    portfolio_summary = analytics.get_portfolio_summary()
    par_metrics = analytics.get_par_metrics()
    
    # Combine metrics
    metrics = {
        'total_portfolio': portfolio_summary.get('total_portfolio_value', 0),
        'total_outstanding': portfolio_summary.get('total_outstanding', 0),
        'collection_rate': portfolio_summary.get('collection_rate', 0),
        'par_30_percentage': par_metrics.get('par_30_percentage', 0),
    }
    
    context = {
        'metrics': metrics,
    }
    
    return render(request, 'management_reports/dashboard.html', context)


def profit_loss_report(request):
    """Profit & Loss statement view"""
    context = {
        'title': 'Profit & Loss Statement',
        'report_date': date.today(),
    }
    return render(request, 'management_reports/profit_loss.html', context)


def export_profit_loss_excel(request):
    """Export P&L to Excel"""
    from reports.excel_generator import ExcelReportGenerator
    
    generator = ExcelReportGenerator()
    excel_file = generator.generate_profit_loss_excel()
    
    response = HttpResponse(
        excel_file,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="profit_loss_{date.today()}.xlsx"'
    return response


def export_profit_loss_pdf(request):
    """Export P&L to PDF"""
    from reports.pdf_generator import PDFReportGenerator
    
    generator = PDFReportGenerator()
    pdf_file = generator.generate_profit_loss_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="profit_loss_{date.today()}.pdf"'
    return response


def board_report(request):
    """Board executive summary view"""
    context = {
        'title': 'Board Executive Summary',
        'report_date': date.today(),
    }
    return render(request, 'management_reports/board_report.html', context)


def export_board_excel(request):
    """Export board report to Excel"""
    from reports.excel_generator import ExcelReportGenerator
    
    generator = ExcelReportGenerator()
    excel_file = generator.generate_board_report_excel()
    
    response = HttpResponse(
        excel_file,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="board_report_{date.today()}.xlsx"'
    return response


def export_board_pdf(request):
    """Export board report to PDF"""
    from reports.pdf_generator import PDFReportGenerator
    
    generator = PDFReportGenerator()
    pdf_file = generator.generate_board_report_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="board_report_{date.today()}.pdf"'
    return response


def officer_performance(request):
    """Loan officer performance dashboard"""
    
    # Import models
    from django.contrib.auth.models import User
    from loans.models import Loan
    from repayments.models import Repayment
    from django.db.models import Count, Sum, Q
    
    # Get all loan officers (users with loans)
    officers = User.objects.filter(
        created_loans__isnull=False
    ).distinct().annotate(
        active_loans=Count('created_loans', filter=Q(created_loans__status='active')),
        total_portfolio=Sum('created_loans__principal', filter=Q(created_loans__status='active'))
    )
    
    officer_data = []
    for officer in officers:
        # Calculate metrics
        active_loans_qs = Loan.objects.filter(created_by=officer, status='active')
        
        total_outstanding = sum(
            loan.get_outstanding_balance() 
            for loan in active_loans_qs
        )
        
        # Collection rate
        disbursed = Loan.objects.filter(
            created_by=officer,
            status__in=['active', 'closed']
        ).aggregate(total=Sum('principal'))['total'] or 0
        
        collected = Repayment.objects.filter(
            loan__created_by=officer,
            status='confirmed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        collection_rate = (collected / disbursed * 100) if disbursed > 0 else 0
        
        # PAR 30
        par_30_loans = active_loans_qs.filter(days_in_arrears__gte=30)
        par_30_value = sum(loan.get_outstanding_balance() for loan in par_30_loans)
        par_30_percentage = (par_30_value / total_outstanding * 100) if total_outstanding > 0 else 0
        
        officer_data.append({
            'officer': officer,
            'active_loans': active_loans_qs.count(),
            'total_portfolio': officer.total_portfolio or 0,
            'total_outstanding': total_outstanding,
            'collection_rate': round(collection_rate, 2),
            'par_30_percentage': round(par_30_percentage, 2),
        })
    
    context = {
        'officers': officer_data,
        'report_date': date.today(),
    }
    
    return render(request, 'management_reports/officer_performance.html', context)


def export_officer_performance_excel(request):
    """Export officer performance to Excel"""
    from reports.excel_generator import ExcelReportGenerator
    
    generator = ExcelReportGenerator()
    excel_file = generator.generate_officer_performance_excel()
    
    response = HttpResponse(
        excel_file,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="officer_performance_{date.today()}.xlsx"'
    return response


@require_http_methods(["GET"])
def api_portfolio_trends(request):
    """API endpoint for portfolio trend data"""
    from reports.analytics import PortfolioAnalytics
    
    analytics = PortfolioAnalytics()
    portfolio_summary = analytics.get_portfolio_summary()
    
    return JsonResponse(portfolio_summary)


@require_http_methods(["GET"])
def api_officer_metrics(request):
    """API endpoint for officer metrics"""
    
    # Get officer ID from request
    officer_id = request.GET.get('officer_id')
    
    if not officer_id:
        return JsonResponse({'error': 'officer_id required'}, status=400)
    
    # Return dummy data for now
    data = {
        'officer_id': officer_id,
        'active_loans': 25,
        'portfolio_value': 150000,
        'collection_rate': 96.5,
    }
    
    return JsonResponse(data)
