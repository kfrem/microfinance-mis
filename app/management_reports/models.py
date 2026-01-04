from django.db import models
from django.contrib.auth.models import User


class ScheduledReport(models.Model):
    """Scheduled reports for automated generation and delivery"""
    
    REPORT_TYPES = [
        ('profit_loss', 'Profit & Loss Statement'),
        ('balance_sheet', 'Balance Sheet'),
        ('cash_flow', 'Cash Flow Statement'),
        ('portfolio_summary', 'Portfolio Summary'),
        ('officer_performance', 'Officer Performance'),
        ('board_summary', 'Board Summary'),
    ]
    
    FREQUENCIES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    frequency = models.CharField(max_length=20, choices=FREQUENCIES)
    recipients = models.TextField(help_text="Email addresses, one per line")
    is_active = models.BooleanField(default=True)
    last_generated = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"


class ReportSnapshot(models.Model):
    """Historical snapshots of key metrics for trend analysis"""
    
    snapshot_date = models.DateField(unique=True)
    
    # Portfolio metrics
    total_portfolio_value = models.DecimalField(max_digits=15, decimal_places=2)
    total_outstanding = models.DecimalField(max_digits=15, decimal_places=2)
    active_loans_count = models.IntegerField()
    
    # PAR metrics
    par_30_value = models.DecimalField(max_digits=15, decimal_places=2)
    par_90_value = models.DecimalField(max_digits=15, decimal_places=2)
    par_30_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    par_90_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Performance metrics
    collection_rate = models.DecimalField(max_digits=5, decimal_places=2)
    disbursement_amount = models.DecimalField(max_digits=15, decimal_places=2)
    repayment_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Client metrics
    total_clients = models.IntegerField()
    active_clients = models.IntegerField()
    new_clients = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-snapshot_date']
        indexes = [
            models.Index(fields=['-snapshot_date']),
        ]
    
    def __str__(self):
        return f"Snapshot for {self.snapshot_date}"
