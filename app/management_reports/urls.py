from django.urls import path
from . import views

app_name = 'management_reports'

urlpatterns = [
    # Main dashboard
    path('', views.management_dashboard, name='dashboard'),
    
    # Profit & Loss
    path('profit-loss/', views.profit_loss_report, name='profit_loss'),
    path('excel/profit-loss/', views.export_profit_loss_excel, name='export_profit_loss_excel'),
    path('pdf/profit-loss/', views.export_profit_loss_pdf, name='export_profit_loss_pdf'),
    
    # Board Reports
    path('board-report/', views.board_report, name='board_report'),
    path('excel/board-report/', views.export_board_excel, name='export_board_excel'),
    path('pdf/board-report/', views.export_board_pdf, name='export_board_pdf'),
    
    # Officer Performance
    path('officer-performance/', views.officer_performance, name='officer_performance'),
    path('excel/officer-performance/', views.export_officer_performance_excel, name='export_officer_performance_excel'),
    
    # API endpoints for AJAX
    path('api/trends/', views.api_portfolio_trends, name='api_trends'),
    path('api/officer-metrics/', views.api_officer_metrics, name='api_officer_metrics'),
]
