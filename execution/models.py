
from django.db import models
from django.contrib.auth.models import AbstractUser


class SKU(models.Model):
    sku_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sku_number} - {self.name}"

class PriceData(models.Model):
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
    website = models.CharField(max_length=255)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    # Remove default 'id' to make (sku, website) the natural key
    id = None  

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['sku', 'website'],
                name='unique_sku_website'
            )
        ]

    def __str__(self):
        return f"{self.sku} @ {self.website}: ${self.price}"


class AppUser(AbstractUser):
    IS_DEMO = 'demo'
    IS_PREMIUM = 'premium'
    USER_TYPES = (
        (IS_DEMO, 'Demo User'),
        (IS_PREMIUM, 'Premium User'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default=IS_DEMO)
    upgrade_key = models.CharField(max_length=100, blank=True, null=True)
    upgraded_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        # Optional: add a unique db_table if needed
        pass