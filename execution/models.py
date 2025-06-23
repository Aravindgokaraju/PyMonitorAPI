import json
import os
from django.db import models
from PyMonitor.mongo import db

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

class ScrapingResult(models.Model):
    """
    Stores scraped data from websites with metadata
    """
    url = models.URLField(max_length=500)
    sku = models.CharField(max_length=100)  # Could also be ForeignKey to SKU model
    price = models.CharField(max_length=50)  # Using CharField to handle various price formats
    element_text = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    website = models.ForeignKey(Website, on_delete=models.CASCADE, null=True, blank=True)
    is_success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sku', 'website']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.sku} @ {self.url} - {self.price}"

def save_scraping_config(config_data):
    """Saves a scraping config to MongoDB"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_file = os.path.join(current_dir, 'test_data')
        with open(test_file, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)

        config_data = test_data
        
        result = db.scraping_configs.insert_one(config_data)
        return result.inserted_id
    except FileNotFoundError:
        raise Exception(f"Test data file not found at: {test_file}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON format in test data file: {str(e)}")
    except Exception as e:
        print(f"MongoDB Error: {e}")
        raise