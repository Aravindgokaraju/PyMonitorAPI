from rest_framework import serializers
from .models import ScrapingResult, Website, SKU, PriceData

class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = ['id', 'name']

class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ['id', 'sku_number', 'name']

class PriceDataSerializer(serializers.ModelSerializer):
    sku = SKUSerializer(read_only=True)
    website = WebsiteSerializer(read_only=True)
    sku_id = serializers.PrimaryKeyRelatedField(queryset=SKU.objects.all(), write_only=True, source='sku')
    website_id = serializers.PrimaryKeyRelatedField(queryset=Website.objects.all(), write_only=True, source='website')
    
    class Meta:
        model = PriceData
        fields = ['id', 'sku', 'website', 'sku_id', 'website_id', 'price', 'last_updated']

class ScrapingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapingResult
        fields = [
            'id',
            'url',
            'sku',
            'price',
            'element_text',
            'timestamp',
            'website',
            'is_success',
            'error_message'
        ]
        read_only_fields = ['timestamp']

    def create(self, validated_data):
        """
        Custom create to handle the table_data format
        """
        return ScrapingResult.objects.create(**validated_data)