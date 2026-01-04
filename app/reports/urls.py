"""
URL Configuration for Reports App
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Main dashboard
    path('', views.reports_dashboard, name='dashboard'),
    
    # Excel Exports
    path('excel/clients/', views.export_client_portfolio_excel, name='excel_clients'),
    path('excel/aging/', views.export_loan_aging_excel, name='excel_aging'),
    path('excel/collection/', views.export_collection_excel, name='excel_collection'),
    path('excel/bog/', views.export_bog_excel, name='excel_bog'),
    path('excel/loan/<str:loan_id>/', views.export_loan_schedule_excel, name='excel_loan_schedule'),
    
    # PDF Exports
    path('pdf/loan/<str:loan_id>/', views.export_loan_statement_pdf, name='pdf_loan_statement'),
    path('pdf/receipt/<str:receipt_number>/', views.export_payment_receipt_pdf, name='pdf_receipt'),
    path('pdf/portfolio/', views.export_portfolio_summary_pdf, name='pdf_portfolio'),
    
    # Cash Flow Projections
    path('cashflow/', views.cashflow_dashboard, name='cashflow_dashboard'),
    path('api/cashflow/daily/', views.cashflow_projections_api, name='api_cashflow_daily'),
    path('api/cashflow/monthly/', views.monthly_projections_api, name='api_monthly'),
    path('api/cashflow/forecast/', views.collection_forecast_api, name='api_forecast'),
    path('api/cashflow/growth/', views.portfolio_growth_api, name='api_growth'),
    path('api/cashflow/risk/', views.arrears_risk_api, name='api_risk'),
]
