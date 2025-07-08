from django.contrib import admin

from execution.models import SKU, PriceData

# Register your models here.
admin.site.register(SKU)
admin.site.register(PriceData)