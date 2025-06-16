from django.db import models

class Website(models.Model):
    name = models.CharField(max_length=200, unique=True)
    
    def __str__(self):
        return self.name

class SKU(models.Model):
    sku_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return f"{self.sku_number} - {self.name}"

class PriceData(models.Model):
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['sku', 'website']]  # Composite primary key
        
    def __str__(self):
        return f"{self.sku} @ {self.website}: ${self.price}"