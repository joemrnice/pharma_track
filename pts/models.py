from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date

class Drug(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    manufacturer = models.CharField(max_length=255)
    batch_number = models.CharField(max_length=50, unique=True)
    expiry_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        if self.expiry_date is not None and self.expiry_date < date.today():
            raise ValidationError("Expiry date must be in the future.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensures validation on save
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# The rest of models.py (Stock and Transaction classes) remains unchanged

class Stock(models.Model):
    drug = models.OneToOneField(Drug, on_delete=models.CASCADE)  # One stock per drug for simplicity
    quantity = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=100)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.drug.name} - {self.quantity}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('in', 'In'),
        ('out', 'Out'),
    )
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        # Get or create stock (one per drug)
        stock, created = Stock.objects.get_or_create(
            drug=self.drug,
            defaults={'quantity': 0, 'location': 'Default Warehouse', 'date_added': date.today()}
        )
        if self.type == 'in':
            stock.quantity += self.quantity
        elif self.type == 'out':
            if stock.quantity < self.quantity:
                raise ValidationError("Insufficient stock for this transaction.")
            stock.quantity -= self.quantity
        stock.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.type.upper()} {self.quantity} of {self.drug.name} on {self.date}"
    