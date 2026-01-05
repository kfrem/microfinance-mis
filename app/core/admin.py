"""
Custom Admin Dashboard with Direct Report Links
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.template.response import TemplateResponse


class CustomAdminSite(admin.AdminSite):
    """
    Custom admin site with direct links to reports and dashboards.
    """
    site_header = "Ghana Microfinance MIS - Administration"
    site_title = "Microfinance MIS Admin"
    index_title = "System Administration & Reports"
    
    def get_urls(self):
        """Add custom admin URLs."""
        urls = super().get_urls()
        custom_urls = [
            path('goto-home/', self.admin_view(self.goto_home), name='goto_home'),
            path('goto-management/', self.admin_view(self.goto_management), name='goto_management'),
            path('goto-reports/', self.admin_view(self.goto_reports), name='goto_reports'),
            path('goto-analytics/', self.admin_view(self.goto_analytics), name='goto_analytics'),
        ]
        return custom_urls + urls
    
    def goto_home(self, request):
        """Redirect to home page."""
        return redirect('/')
    
    def goto_management(self, request):
        """Redirect to management dashboard."""
        return redirect('/management/')
    
    def goto_reports(self, request):
        """Redirect to reports dashboard."""
        return redirect('/reports/')
    
    def goto_analytics(self, request):
        """Redirect to analytics dashboard."""
        return redirect('/dashboard/')
    
    def index(self, request, extra_context=None):
        """
        Custom admin index page with quick links to reports.
        """
        extra_context = extra_context or {}
        
        # Add quick links
        extra_context['quick_links'] = [
            {
                'title': '🏠 Home Dashboard',
                'url': '/',
                'description': 'Main system dashboard with overview of all modules'
            },
            {
                'title': '📊 Management Reports',
                'url': '/management/',
                'description': 'P&L Statement, Officer Performance, Board Reports'
            },
            {
                'title': '📈 Operational Reports',
                'url': '/reports/',
                'description': 'Client Portfolio, Loan Aging, BoG Compliance, Cash Flow'
            },
            {
                'title': '📉 Analytics Dashboard',
                'url': '/dashboard/',
                'description': 'Portfolio Analysis, PAR Metrics, Trend Analysis'
            },
        ]
        
        # Get system stats
        from loans.models import Loan
        from clients.models import Client
        from repayments.models import Repayment
        
        extra_context['system_stats'] = {
            'total_clients': Client.objects.count(),
            'active_clients': Client.objects.filter(status='active').count(),
            'total_loans': Loan.objects.count(),
            'active_loans': Loan.objects.filter(status='active').count(),
            'total_repayments': Repayment.objects.count(),
            'confirmed_repayments': Repayment.objects.filter(status='confirmed').count(),
        }
        
        return super().index(request, extra_context)


# Create custom admin site instance
admin_site = CustomAdminSite(name='custom_admin')
