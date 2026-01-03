from decimal import Decimal

from django.db import models
from loans.models import Loan


class Repayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="repayments")

    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    paid_on = models.DateField()

    method = models.CharField(max_length=50, blank=True, default="")
    reference = models.CharField(max_length=100, blank=True, default="")
    notes = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Repayment {self.amount} on {self.paid_on} (Loan #{self.loan_id})"
