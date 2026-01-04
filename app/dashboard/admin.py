"""
Dashboard admin interface
Provides links to reports and dashboards in Django admin
"""
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html


class DashboardAdmin(admin.ModelAdmin):
    """
    Placeholder admin to show dashboard links in admin site
    """
    
    def changelist_view(self, request, extra_context=None):
        """Override to show dashboard links"""
        extra_context = extra_context or {}
        extra_context['dashboard_links'] = [
            {
                'title': 'Executive Dashboard',
                'url': reverse('dashboard:executive'),
                'description': 'Portfolio overview, KPIs, and key metrics',
            },
            {
                'title': 'Portfolio Quality Report',
                'url': reverse('dashboard:portfolio_report'),
                'description': 'Detailed portfolio analysis, PAR, arrears aging',
            },
            {
                'title': 'BoG Prudential Report',
                'url': reverse('dashboard:bog_report'),
                'description': 'Bank of Ghana regulatory compliance report',
            },
        ]
        return super().changelist_view(request, extra_context)


# Register a simple way to access dashboards from admin
admin.site.index_template = 'admin/dashboard_index.html'
