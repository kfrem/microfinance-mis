from django.db import models
from clients.models import Client


class Loan(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("active", "Active"),
        ("closed", "Closed"),
        ("defaulted", "Defaulted"),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="loans")
    principal = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Annual %")
    term_months = models.PositiveIntegerField(default=12)

    disbursed_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Loan #{self.id} - {self.client}"

