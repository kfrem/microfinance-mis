from django.db import models
from django.core.validators import RegexValidator


class Client(models.Model):
    """Enhanced client model with KYC and risk classification."""
    
    CLIENT_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('group', 'Group/Solidarity'),
        ('sme', 'Small/Medium Enterprise'),
    ]
    
    RISK_CATEGORY_CHOICES = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('blacklisted', 'Blacklisted'),
    ]
    
    # Core Information
    client_id = models.CharField(max_length=20, unique=True, editable=False, help_text="Auto-generated ID")
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPE_CHOICES, default='individual')
    full_name = models.CharField(max_length=200)
    
    # Contact Information
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+233XXXXXXXXX'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True, help_text="Residential/Business address")
    
    # KYC Information (Ghana-specific)
    ghana_card_id = models.CharField(max_length=20, blank=True, help_text="Ghana Card Number (masked)")
    date_of_birth = models.DateField(null=True, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    employer = models.CharField(max_length=200, blank=True)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Estimated monthly income in GHS")
    
    # Risk & Compliance
    risk_category = models.CharField(max_length=20, choices=RISK_CATEGORY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    kyc_verified = models.BooleanField(default=False, help_text="KYC documents verified")
    kyc_verified_date = models.DateField(null=True, blank=True)
    kyc_verified_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_clients')
    
    # Group Information (for solidarity groups)
    group_size = models.PositiveIntegerField(null=True, blank=True, help_text="Number of members in group")
    group_leader = models.CharField(max_length=200, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_clients')
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client_id']),
            models.Index(fields=['ghana_card_id']),
            models.Index(fields=['status']),
            models.Index(fields=['risk_category']),
        ]
    
    def __str__(self):
        return f"{self.client_id} - {self.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.client_id:
            # Auto-generate client ID: C00001, C00002, etc.
            last_client = Client.objects.order_by('-id').first()
            if last_client and last_client.client_id:
                try:
                    last_num = int(last_client.client_id[1:])
                    self.client_id = f"C{str(last_num + 1).zfill(5)}"
                except (ValueError, IndexError):
                    self.client_id = "C00001"
            else:
                self.client_id = "C00001"
        super().save(*args, **kwargs)
    
    def get_active_loans_count(self):
        """Return count of active loans."""
        return self.loans.filter(status='active').count()
    
    def get_total_outstanding(self):
        """Return total outstanding balance across all active loans."""
        from decimal import Decimal
        total = Decimal('0.00')
        for loan in self.loans.filter(status='active'):
            total += loan.get_outstanding_balance()
        return total
