from rest_framework import serializers
from .models import SKU, PriceData


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ['id', 'sku_number', 'name']

class PriceDataSerializer(serializers.ModelSerializer):
    sku = SKUSerializer(read_only=True)
    website = serializers.CharField(read_only=True)  # Read the website name directly as string
    sku_number = serializers.PrimaryKeyRelatedField(queryset=SKU.objects.all(), write_only=True, source='sku')
    website_id = serializers.CharField(read_only=True)
    
    class Meta:
        model = PriceData
        fields = ['id', 'sku', 'website', 'sku_number', 'website_id', 'price', 'last_updated']
