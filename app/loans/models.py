from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from clients.models import Client


class LoanProduct(models.Model):
    """Loan product definitions based on Ghana microfinance standards."""
    
    INTEREST_METHOD_CHOICES = [
        ('flat', 'Flat Rate'),
        ('declining', 'Declining Balance'),
        ('compound', 'Compound Interest'),
    ]
    
    REPAYMENT_FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
        ('bullet', 'Bullet (End of Term)'),
    ]
    
    name = models.CharField(max_length=100, help_text="Product name (e.g., 'Individual Micro Loan')")
    code = models.CharField(max_length=20, unique=True, help_text="Product code (e.g., 'IML-001')")
    description = models.TextField(blank=True)
    
    # Loan Limits
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('100.00'))
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('50000.00'))
    
    # Interest Configuration
    interest_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Annual interest rate (%)",
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    interest_method = models.CharField(max_length=20, choices=INTEREST_METHOD_CHOICES, default='declining')
    
    # Term Configuration
    min_term_months = models.PositiveIntegerField(default=3)
    max_term_months = models.PositiveIntegerField(default=24)
    repayment_frequency = models.CharField(max_length=20, choices=REPAYMENT_FREQUENCY_CHOICES, default='monthly')
    
    # Fees
    processing_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('2.00'), help_text="% of principal")
    insurance_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), help_text="% of principal")
    late_payment_penalty_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('2.00'), help_text="% per month overdue")
    
    # Collateral & Requirements
    requires_collateral = models.BooleanField(default=False)
    requires_guarantor = models.BooleanField(default=True)
    min_guarantors = models.PositiveIntegerField(default=1)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Loan(models.Model):
    """Enhanced loan model with full amortization and BoG compliance."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('active', 'Active/Disbursed'),
        ('closed', 'Closed/Paid Off'),
        ('written_off', 'Written Off'),
    ]
    
    # BoG Loan Classification
    CLASSIFICATION_CHOICES = [
        ('current', 'Current (0-30 days)'),
        ('substandard', 'Substandard (31-90 days)'),
        ('doubtful', 'Doubtful (91-180 days)'),
        ('loss', 'Loss (>180 days)'),
    ]
    
    # Core Information
    loan_id = models.CharField(max_length=20, unique=True, editable=False)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="loans")
    product = models.ForeignKey(LoanProduct, on_delete=models.PROTECT, null=True, blank=True, related_name="loans")
    
    # Loan Terms
    principal = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Annual %")
    interest_method = models.CharField(max_length=20, choices=LoanProduct.INTEREST_METHOD_CHOICES, default='declining')
    term_months = models.PositiveIntegerField(default=12)
    repayment_frequency = models.CharField(max_length=20, choices=LoanProduct.REPAYMENT_FREQUENCY_CHOICES, default='monthly')
    
    # Fees
    processing_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    insurance_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Dates
    application_date = models.DateField(default=date.today)
    approved_date = models.DateField(null=True, blank=True)
    disbursed_date = models.DateField(null=True, blank=True)
    maturity_date = models.DateField(null=True, blank=True, help_text="Expected final payment date")
    first_repayment_date = models.DateField(null=True, blank=True)
    
    # Status & Classification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    classification = models.CharField(max_length=20, choices=CLASSIFICATION_CHOICES, default='current', help_text="BoG loan classification")
    days_in_arrears = models.IntegerField(default=0, help_text="Days overdue")
    
    # Approval & Disbursement
    approved_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_loans')
    disbursed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='disbursed_loans')
    disbursement_method = models.CharField(max_length=50, blank=True, help_text="Cash, Bank Transfer, Mobile Money")
    disbursement_reference = models.CharField(max_length=100, blank=True)
    
    # Calculated Fields (cached)
    total_interest = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), help_text="Total interest over loan term")
    total_repayable = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), help_text="Principal + Interest")
    installment_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), help_text="Regular installment amount")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['loan_id']),
            models.Index(fields=['status']),
            models.Index(fields=['classification']),
            models.Index(fields=['disbursed_date']),
        ]
    
    def __str__(self):
        return f"Loan #{self.loan_id} - {self.client.full_name}"
    
    def save(self, *args, **kwargs):
        # Auto-generate loan ID
        if not self.loan_id:
            last_loan = Loan.objects.order_by('-id').first()
            if last_loan and last_loan.loan_id:
                try:
                    last_num = int(last_loan.loan_id[1:])
                    self.loan_id = f"L{str(last_num + 1).zfill(6)}"
                except (ValueError, IndexError):
                    self.loan_id = "L000001"
            else:
                self.loan_id = "L000001"
        
        # Calculate maturity date if disbursed
        if self.disbursed_date and not self.maturity_date:
            self.maturity_date = self.disbursed_date + relativedelta(months=self.term_months)
        
        # Calculate loan amounts if not set
        if self.principal and self.interest_rate and not self.total_interest:
            self.calculate_loan_amounts()
        
        super().save(*args, **kwargs)
    
    def calculate_loan_amounts(self):
        """Calculate total interest, total repayable, and installment amount."""
        principal = Decimal(str(self.principal))
        rate = Decimal(str(self.interest_rate)) / Decimal('100')
        months = Decimal(str(self.term_months))
        
        if self.interest_method == 'flat':
            # Flat Rate: Interest = Principal × Rate × Term
            self.total_interest = principal * rate * (months / Decimal('12'))
            self.total_repayable = principal + self.total_interest
            
            # Calculate number of installments
            num_installments = self.get_number_of_installments()
            if num_installments > 0:
                self.installment_amount = self.total_repayable / Decimal(str(num_installments))
        
        elif self.interest_method == 'declining':
            # Declining Balance (Reducing Balance)
            monthly_rate = rate / Decimal('12')
            num_installments = Decimal(str(self.get_number_of_installments()))
            
            if monthly_rate > 0 and num_installments > 0:
                # EMI Formula: P * r * (1+r)^n / ((1+r)^n - 1)
                factor = (Decimal('1') + monthly_rate) ** num_installments
                self.installment_amount = principal * monthly_rate * factor / (factor - Decimal('1'))
                self.total_repayable = self.installment_amount * num_installments
                self.total_interest = self.total_repayable - principal
    
    def get_number_of_installments(self):
        """Calculate total number of installments based on frequency."""
        if self.repayment_frequency == 'daily':
            return self.term_months * 30
        elif self.repayment_frequency == 'weekly':
            return self.term_months * 4
        elif self.repayment_frequency == 'biweekly':
            return self.term_months * 2
        elif self.repayment_frequency == 'monthly':
            return self.term_months
        elif self.repayment_frequency == 'bullet':
            return 1
        return self.term_months
    
    def generate_repayment_schedule(self):
        """Generate or regenerate the loan repayment schedule."""
        from loans.models import LoanSchedule
        
        if not self.disbursed_date:
            return
        
        # Delete existing schedule
        self.schedule_entries.all().delete()
        
        principal = Decimal(str(self.principal))
        rate = Decimal(str(self.interest_rate)) / Decimal('100')
        monthly_rate = rate / Decimal('12')
        
        num_installments = self.get_number_of_installments()
        current_date = self.first_repayment_date or self.disbursed_date
        
        # Calculate installment interval
        if self.repayment_frequency == 'daily':
            interval = timedelta(days=1)
        elif self.repayment_frequency == 'weekly':
            interval = timedelta(weeks=1)
        elif self.repayment_frequency == 'biweekly':
            interval = timedelta(weeks=2)
        elif self.repayment_frequency == 'monthly':
            interval = relativedelta(months=1)
        elif self.repayment_frequency == 'bullet':
            interval = relativedelta(months=self.term_months)
        else:
            interval = relativedelta(months=1)
        
        outstanding_balance = principal
        
        for installment_num in range(1, num_installments + 1):
            if self.interest_method == 'flat':
                # Flat rate: Equal principal + equal interest each period
                principal_due = principal / Decimal(str(num_installments))
                interest_due = self.total_interest / Decimal(str(num_installments))
            
            elif self.interest_method == 'declining':
                # Declining balance: Interest on outstanding balance
                interest_due = outstanding_balance * monthly_rate
                principal_due = self.installment_amount - interest_due
                
                # Adjust last installment for rounding
                if installment_num == num_installments:
                    principal_due = outstanding_balance
            else:
                principal_due = principal / Decimal(str(num_installments))
                interest_due = Decimal('0.00')
            
            total_due = principal_due + interest_due
            outstanding_balance -= principal_due
            
            # Ensure outstanding balance doesn't go negative
            if outstanding_balance < Decimal('0.01'):
                outstanding_balance = Decimal('0.00')
            
            # Create schedule entry
            LoanSchedule.objects.create(
                loan=self,
                installment_number=installment_num,
                due_date=current_date,
                principal_due=principal_due,
                interest_due=interest_due,
                total_due=total_due,
                principal_balance=outstanding_balance,
            )
            
            # Move to next due date
            if isinstance(interval, timedelta):
                current_date += interval
            else:
                current_date += interval
    
    def get_outstanding_balance(self):
        """Calculate current outstanding balance."""
        from repayments.models import Repayment
        
        total_paid = Repayment.objects.filter(loan=self).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        
        return self.total_repayable - total_paid
    
    def get_arrears_amount(self):
        """Calculate total arrears (overdue amount)."""
        from loans.models import LoanSchedule
        
        today = date.today()
        overdue = LoanSchedule.objects.filter(
            loan=self,
            due_date__lt=today,
            balance_due__gt=0
        ).aggregate(total=models.Sum('balance_due'))['total'] or Decimal('0.00')
        
        return overdue
    
    def update_classification(self):
        """Update BoG loan classification based on days in arrears."""
        if self.days_in_arrears == 0:
            self.classification = 'current'
        elif 1 <= self.days_in_arrears <= 30:
            self.classification = 'current'
        elif 31 <= self.days_in_arrears <= 90:
            self.classification = 'substandard'
        elif 91 <= self.days_in_arrears <= 180:
            self.classification = 'doubtful'
        else:  # > 180 days
            self.classification = 'loss'
        
        self.save(update_fields=['classification'])


class LoanSchedule(models.Model):
    """Repayment schedule for each loan installment."""
    
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='schedule_entries')
    installment_number = models.PositiveIntegerField()
    due_date = models.DateField()
    
    # Due amounts
    principal_due = models.DecimalField(max_digits=12, decimal_places=2)
    interest_due = models.DecimalField(max_digits=12, decimal_places=2)
    penalty_due = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_due = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Paid amounts
    principal_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    interest_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    penalty_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Balances
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, help_text="Remaining balance for this installment")
    principal_balance = models.DecimalField(max_digits=12, decimal_places=2, help_text="Outstanding principal after this installment")
    
    # Status
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    days_late = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['loan', 'installment_number']
        unique_together = ['loan', 'installment_number']
        indexes = [
            models.Index(fields=['loan', 'due_date']),
            models.Index(fields=['due_date']),
            models.Index(fields=['is_paid']),
        ]
    
    def __str__(self):
        return f"{self.loan.loan_id} - Installment #{self.installment_number}"
    
    def save(self, *args, **kwargs):
        # Calculate balance due
        self.balance_due = self.total_due - self.total_paid
        
        # Mark as paid if fully paid
        if self.balance_due <= Decimal('0.01'):
            self.is_paid = True
            if not self.paid_date:
                self.paid_date = date.today()
        
        super().save(*args, **kwargs)
