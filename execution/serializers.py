from rest_framework import serializers
from .models import SKU, PriceData


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ['id', 'sku_number', 'name','is_premium']

# class PriceDataSerializer(serializers.ModelSerializer):
#     sku = SKUSerializer(read_only=True)
#     website = serializers.CharField(read_only=True)  # Read the website name directly as string
#     sku_number = serializers.PrimaryKeyRelatedField(queryset=SKU.objects.all(), write_only=True, source='sku')
#     website_id = serializers.CharField(read_only=True)
    
#     class Meta:
#         model = PriceData
#         fields = ['id', 'sku', 'website', 'sku_number', 'website_id', 'price', 'last_updated']

# class PriceDataSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PriceData
#         fields = ['sku', 'website', 'price', 'last_updated']
#         validators = [
#             serializers.UniqueTogetherValidator(
#                 queryset=PriceData.objects.all(),
#                 fields=['sku', 'website']
#             )
#         ]

class PriceDataSerializer(serializers.ModelSerializer):
    # CHANGE: Accept string input ('sku_number') instead of internal ID
    sku = serializers.SlugRelatedField(
        slug_field='sku_number',  # This must match the field name in your Sku model
        queryset=SKU.objects.all()
    )

    class Meta:
        model = PriceData
        fields = ['sku', 'website', 'price', 'last_updated']
        
        # IMPORTANT: We define an empty list for validators to override the default checks.
        # This allows the POST request to pass through to your ViewSet even if 
        # the SKU+Website pair already exists, so your update_or_create logic can run.
        validators = []
