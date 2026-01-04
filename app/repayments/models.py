from decimal import Decimal
from django.db import models
from django.utils import timezone
from loans.models import Loan, LoanSchedule


class Repayment(models.Model):
    """Enhanced repayment model with allocation tracking."""
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('cheque', 'Cheque'),
        ('direct_debit', 'Direct Debit'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('reversed', 'Reversed'),
    ]
    
    # Core Information
    receipt_number = models.CharField(max_length=20, unique=True, editable=False)
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT, related_name="repayments")
    
    # Payment Details
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    paid_on = models.DateField()
    received_on = models.DateTimeField(default=timezone.now, help_text="When payment was received/recorded")
    
    method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='cash')
    reference = models.CharField(max_length=100, blank=True, default="", help_text="Transaction reference/cheque number")
    
    # Allocation (how payment is split)
    principal_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    interest_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    penalty_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    fees_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    
    # Processing
    received_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='received_payments')
    confirmed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='confirmed_payments')
    
    notes = models.TextField(blank=True, default="")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-paid_on', '-created_at']
        indexes = [
            models.Index(fields=['receipt_number']),
            models.Index(fields=['loan', 'paid_on']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self) -> str:
        return f"Receipt {self.receipt_number}: GHS {self.amount} on {self.paid_on} (Loan {self.loan.loan_id})"
    
    def save(self, *args, **kwargs):
        # Auto-generate receipt number
        if not self.receipt_number:
            last_payment = Repayment.objects.order_by('-id').first()
            if last_payment and last_payment.receipt_number:
                try:
                    last_num = int(last_payment.receipt_number[3:])
                    self.receipt_number = f"RCP{str(last_num + 1).zfill(7)}"
                except (ValueError, IndexError):
                    self.receipt_number = "RCP0000001"
            else:
                self.receipt_number = "RCP0000001"
        
        # Allocate payment if not already allocated
        if self.amount > 0 and self.principal_paid == 0 and self.interest_paid == 0:
            self.allocate_payment()
        
        super().save(*args, **kwargs)
        
        # Update loan schedule after saving
        if self.status == 'confirmed':
            self.update_loan_schedule()
    
    def allocate_payment(self):
        """
        Allocate payment according to standard waterfall:
        1. Penalties (oldest first)
        2. Interest (oldest first)
        3. Principal (oldest first)
        """
        remaining = Decimal(str(self.amount))
        
        # Get all unpaid/partially paid schedule entries ordered by due date
        schedule_entries = self.loan.schedule_entries.filter(
            is_paid=False
        ).order_by('due_date')
        
        total_penalty = Decimal('0.00')
        total_interest = Decimal('0.00')
        total_principal = Decimal('0.00')
        
        for entry in schedule_entries:
            if remaining <= 0:
                break
            
            # 1. Pay penalties first
            penalty_due = entry.penalty_due - entry.penalty_paid
            if penalty_due > 0 and remaining > 0:
                penalty_payment = min(penalty_due, remaining)
                total_penalty += penalty_payment
                remaining -= penalty_payment
            
            # 2. Pay interest
            interest_due = entry.interest_due - entry.interest_paid
            if interest_due > 0 and remaining > 0:
                interest_payment = min(interest_due, remaining)
                total_interest += interest_payment
                remaining -= interest_payment
            
            # 3. Pay principal
            principal_due = entry.principal_due - entry.principal_paid
            if principal_due > 0 and remaining > 0:
                principal_payment = min(principal_due, remaining)
                total_principal += principal_payment
                remaining -= principal_payment
        
        self.penalty_paid = total_penalty
        self.interest_paid = total_interest
        self.principal_paid = total_principal
    
    def update_loan_schedule(self):
        """Update loan schedule entries with this payment."""
        remaining = Decimal(str(self.amount))
        
        schedule_entries = self.loan.schedule_entries.filter(
            is_paid=False
        ).order_by('due_date')
        
        for entry in schedule_entries:
            if remaining <= 0:
                break
            
            # Pay penalties
            penalty_due = entry.penalty_due - entry.penalty_paid
            if penalty_due > 0 and remaining > 0:
                penalty_payment = min(penalty_due, remaining)
                entry.penalty_paid += penalty_payment
                remaining -= penalty_payment
            
            # Pay interest
            interest_due = entry.interest_due - entry.interest_paid
            if interest_due > 0 and remaining > 0:
                interest_payment = min(interest_due, remaining)
                entry.interest_paid += interest_payment
                remaining -= interest_payment
            
            # Pay principal
            principal_due = entry.principal_due - entry.principal_paid
            if principal_due > 0 and remaining > 0:
                principal_payment = min(principal_due, remaining)
                entry.principal_paid += principal_payment
                remaining -= principal_payment
            
            # Update totals
            entry.total_paid = entry.principal_paid + entry.interest_paid + entry.penalty_paid
            entry.save()
        
        # Update loan's days in arrears
        self.loan.days_in_arrears = self.calculate_days_in_arrears()
        self.loan.update_classification()
    
    def calculate_days_in_arrears(self):
        """Calculate current days in arrears for the loan."""
        from datetime import date
        
        # Find the earliest unpaid installment
        earliest_overdue = self.loan.schedule_entries.filter(
            is_paid=False,
            due_date__lt=date.today()
        ).order_by('due_date').first()
        
        if earliest_overdue:
            days_overdue = (date.today() - earliest_overdue.due_date).days
            return max(0, days_overdue)
        
        return 0


class PaymentReversal(models.Model):
    """Track payment reversals for audit purposes."""
    
    repayment = models.ForeignKey(Repayment, on_delete=models.CASCADE, related_name='reversals')
    reason = models.TextField()
    reversed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    reversed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reversal of {self.repayment.receipt_number}"
