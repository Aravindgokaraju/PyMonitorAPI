from collections import defaultdict
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import SKU, PriceData,AppUser
from ..serializers import SKUSerializer, PriceDataSerializer

class SKUViewSet(viewsets.ModelViewSet):
    queryset = SKU.objects.all()
    serializer_class = SKUSerializer
    def get_queryset(self):
        user = self.request.shared_user
        qs = super().get_queryset()

        if user.user_type == AppUser.IS_DEMO:
            qs = qs.filter(is_premium=False)

        return qs
    
class PriceDataViewSet(viewsets.ModelViewSet):
    queryset = PriceData.objects.all()
    serializer_class = PriceDataSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        sku_id = self.request.query_params.get('sku')
        website = self.request.query_params.get('website')
        
        if sku_id:
            queryset = queryset.filter(sku_id=sku_id)
        if website:
            queryset = queryset.filter(website=website)
            
        return queryset

    def perform_create(self, serializer):
        """
        Upsert logic: if a PriceData for this (sku, website) already exists,
        update price and last_updated; otherwise, create new.
        """
        sku = serializer.validated_data['sku']
        website = serializer.validated_data['website']
        price = serializer.validated_data['price']

        obj, created = PriceData.objects.update_or_create(
            sku=sku,
            website=website,
            defaults={'price': price}
        )
        serializer.instance = obj

    def get_best_prices_by_sku(self, price_data):
        """
        Given a queryset of PriceData, return best price per SKU.
        """
        sku_map = defaultdict(list)
        
        for item in price_data:
            sku_map[item.sku.sku_number].append({
                'price': float(item.price),
                'website': item.website,
                'name': item.sku.name,
                'last_updated': item.last_updated
            })
        
        result = []
        for sku_number, entries in sku_map.items():
            best_price_entry = min(entries, key=lambda x: x['price'])
            result.append({
                'sku_number': sku_number,
                'product_name': entries[0]['name'],
                'best_price': best_price_entry['price'],
                'best_price_website': best_price_entry['website'],
                'all_offers': sorted(entries, key=lambda x: x['price']),
                'last_updated': best_price_entry['last_updated']
            })
        
        return sorted(result, key=lambda x: x['sku_number'])

    @action(detail=False, methods=['get'], url_path='best_prices')
    def best_prices(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        best_prices_data = self.get_best_prices_by_sku(queryset)
        return Response(best_prices_data)