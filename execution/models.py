
from django.db import models
from django.contrib.auth.models import AbstractUser


class SKU(models.Model):
    sku_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return f"{self.sku_number} - {self.name}"

class PriceData(models.Model):
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
    website = models.CharField(max_length=255)  # Changed to CharField

    price = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['sku', 'website']]  # Composite primary key
        
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
    
    # # Add these to fix the reverse relationship conflicts
    # groups = models.ManyToManyField(
    #     'auth.Group',
    #     verbose_name='groups',
    #     blank=True,
    #     help_text='The groups this user belongs to.',
    #     related_name='appuser_set',  # ← Changed from default 'user_set'
    #     related_query_name='appuser',
    # )
    # user_permissions = models.ManyToManyField(
    #     'auth.Permission',
    #     verbose_name='user permissions',
    #     blank=True,
    #     help_text='Specific permissions for this user.',
    #     related_name='appuser_permissions_set',  # ← Changed from default
    #     related_query_name='appuser_permission',
    # )
    
    class Meta:
        # Optional: add a unique db_table if needed
        pass