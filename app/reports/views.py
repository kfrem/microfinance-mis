"""
Views for Report Generation and Export
"""
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from datetime import date, timedelta

from .excel_generator import ExcelReportGenerator
from .pdf_generator import PDFReportGenerator
from .cashflow import CashFlowProjections


def reports_dashboard(request):
    """Main reports dashboard page."""
    return render(request, 'reports/dashboard.html')


# Excel Report Views

def export_client_portfolio_excel(request):
    """Export client portfolio to Excel."""
    generator = ExcelReportGenerator()
    output = generator.generate_client_portfolio_report()
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="client_portfolio_{date.today()}.xlsx"'
    
    return response


def export_loan_aging_excel(request):
    """Export loan aging report to Excel."""
    generator = ExcelReportGenerator()
    output = generator.generate_loan_aging_report()
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="loan_aging_{date.today()}.xlsx"'
    
    return response


def export_collection_excel(request):
    """Export collection report to Excel."""
    # Get date range from query params
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = date.fromisoformat(start_date)
    if end_date:
        end_date = date.fromisoformat(end_date)
    
    generator = ExcelReportGenerator()
    output = generator.generate_collection_report(start_date, end_date)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="collection_report_{date.today()}.xlsx"'
    
    return response


def export_bog_excel(request):
    """Export BoG regulatory report to Excel."""
    generator = ExcelReportGenerator()
    output = generator.generate_bog_regulatory_report()
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="bog_report_{date.today()}.xlsx"'
    
    return response


def export_loan_schedule_excel(request, loan_id):
    """Export specific loan schedule to Excel."""
    generator = ExcelReportGenerator()
    output = generator.generate_loan_schedule_report(loan_id)
    
    if not output:
        return HttpResponse('Loan not found', status=404)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="loan_schedule_{loan_id}.xlsx"'
    
    return response


# PDF Report Views

def export_loan_statement_pdf(request, loan_id):
    """Export loan statement to PDF."""
    generator = PDFReportGenerator()
    output = generator.generate_loan_statement(loan_id)
    
    if not output:
        return HttpResponse('Loan not found', status=404)
    
    response = HttpResponse(output.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="loan_statement_{loan_id}.pdf"'
    
    return response


def export_payment_receipt_pdf(request, receipt_number):
    """Export payment receipt to PDF."""
    generator = PDFReportGenerator()
    output = generator.generate_payment_receipt(receipt_number)
    
    if not output:
        return HttpResponse('Receipt not found', status=404)
    
    response = HttpResponse(output.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{receipt_number}.pdf"'
    
    return response


def export_portfolio_summary_pdf(request):
    """Export portfolio summary to PDF."""
    generator = PDFReportGenerator()
    output = generator.generate_portfolio_summary()
    
    response = HttpResponse(output.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="portfolio_summary_{date.today()}.pdf"'
    
    return response


# Cash Flow Projections API

@require_http_methods(["GET"])
def cashflow_projections_api(request):
    """API endpoint for cash flow projections."""
    days_ahead = int(request.GET.get('days', 30))
    
    cashflow = CashFlowProjections()
    
    projections = cashflow.get_expected_payments(days_ahead)
    
    # Convert Decimal to float for JSON
    result = []
    for day in projections:
        result.append({
            'date': day['date'].strftime('%Y-%m-%d'),
            'principal': float(day['principal']),
            'interest': float(day['interest']),
            'penalty': float(day['penalty']),
            'total': float(day['total']),
            'loan_count': day['loan_count'],
        })
    
    return JsonResponse({
        'days_ahead': days_ahead,
        'projections': result
    })


@require_http_methods(["GET"])
def monthly_projections_api(request):
    """API endpoint for monthly revenue projections."""
    months = int(request.GET.get('months', 12))
    
    cashflow = CashFlowProjections()
    projections = cashflow.get_monthly_projections(months)
    
    result = []
    for month in projections:
        result.append({
            'month': month['month'],
            'start_date': month['start_date'].strftime('%Y-%m-%d'),
            'end_date': month['end_date'].strftime('%Y-%m-%d'),
            'principal': float(month['principal']),
            'interest': float(month['interest']),
            'penalty': float(month['penalty']),
            'total': float(month['total']),
            'loan_count': month['loan_count'],
        })
    
    return JsonResponse({
        'months_ahead': months,
        'projections': result
    })


@require_http_methods(["GET"])
def collection_forecast_api(request):
    """API endpoint for collection forecast."""
    days = int(request.GET.get('days', 30))
    
    cashflow = CashFlowProjections()
    forecast = cashflow.get_collection_forecast(days)
    
    # Convert daily breakdown
    daily = []
    for day in forecast['daily_breakdown']:
        daily.append({
            'date': day['date'].strftime('%Y-%m-%d'),
            'principal': float(day['principal']),
            'interest': float(day['interest']),
            'penalty': float(day['penalty']),
            'total': float(day['total']),
            'loan_count': day['loan_count'],
        })
    
    return JsonResponse({
        'days_ahead': days,
        'historical_collection_rate': float(forecast['historical_collection_rate']),
        'expected_payments': float(forecast['expected_payments']),
        'forecasted_collection': float(forecast['forecasted_collection']),
        'potential_shortfall': float(forecast['potential_shortfall']),
        'daily_breakdown': daily,
    })


@require_http_methods(["GET"])
def portfolio_growth_api(request):
    """API endpoint for portfolio growth projection."""
    months = int(request.GET.get('months', 12))
    
    cashflow = CashFlowProjections()
    growth = cashflow.get_portfolio_growth_projection(months)
    
    projections = []
    for proj in growth['projections']:
        projections.append({
            'month': proj['month'],
            'projected_portfolio': float(proj['projected_portfolio']),
            'principal_reduction': float(proj['principal_reduction']),
            'interest_revenue': float(proj['interest_revenue']),
        })
    
    return JsonResponse({
        'current_portfolio': float(growth['current_portfolio']),
        'months_ahead': months,
        'projections': projections,
    })


@require_http_methods(["GET"])
def arrears_risk_api(request):
    """API endpoint for arrears risk forecast."""
    days = int(request.GET.get('days', 30))
    
    cashflow = CashFlowProjections()
    risk = cashflow.get_arrears_risk_forecast(days)
    
    by_classification = {}
    for key, data in risk['by_classification'].items():
        by_classification[key] = {
            'loan_count': data['loan_count'],
            'upcoming_payments': float(data['upcoming_payments']),
            'risk_probability': float(data['risk_probability']),
            'at_risk_amount': float(data['at_risk_amount']),
        }
    
    return JsonResponse({
        'days_ahead': days,
        'total_upcoming_payments': float(risk['total_upcoming_payments']),
        'total_at_risk': float(risk['total_at_risk']),
        'overall_risk_rate': float(risk['overall_risk_rate']),
        'by_classification': by_classification,
    })


def cashflow_dashboard(request):
    """Cash flow projections dashboard."""
    return render(request, 'reports/cashflow.html')
