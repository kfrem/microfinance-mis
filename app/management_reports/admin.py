from django.contrib import admin
from .models import ScheduledReport, ReportSnapshot


# Note: These admin interfaces are hidden from the main admin menu
# because they are primarily for system use, not user interaction.
# 
# To access reports, users should use:
# - Management Dashboard: /management/
# - Operational Reports: /reports/
# - Analytics Dashboard: /dashboard/
#
# Uncomment below if you need to manage scheduled reports or snapshots directly:

# @admin.register(ScheduledReport)
# class ScheduledReportAdmin(admin.ModelAdmin):
#     list_display = ['name', 'report_type', 'frequency', 'is_active', 'last_generated', 'created_at']
#     list_filter = ['report_type', 'frequency', 'is_active']
#     search_fields = ['name', 'recipients']
#     readonly_fields = ['last_generated', 'created_at']


# @admin.register(ReportSnapshot)
# class ReportSnapshotAdmin(admin.ModelAdmin):
#     list_display = ['snapshot_date', 'total_portfolio_value', 'active_loans_count', 
#                     'par_30_percentage', 'collection_rate', 'created_at']
#     list_filter = ['snapshot_date']
#     readonly_fields = ['created_at']
#     date_hierarchy = 'snapshot_date'
