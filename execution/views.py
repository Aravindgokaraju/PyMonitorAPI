from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets

from execution.scrape import ScrapingService
from .models import Website, SKU, PriceData
from .serializers import WebsiteSerializer, SKUSerializer, PriceDataSerializer

class WebsiteViewSet(viewsets.ModelViewSet):
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer

class SKUViewSet(viewsets.ModelViewSet):
    queryset = SKU.objects.all()
    serializer_class = SKUSerializer

class PriceDataViewSet(viewsets.ModelViewSet):
    queryset = PriceData.objects.all()
    serializer_class = PriceDataSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        sku = self.request.query_params.get('sku')
        website = self.request.query_params.get('website')
        
        if sku:
            queryset = queryset.filter(sku__sku_number=sku)
        if website:
            queryset = queryset.filter(website__name=website)
            
        return queryset

def run_scraper_view(request):
    if request.method == 'POST':
        try:
            scraper = ScrapingService()
            scraped_data = scraper.scrape_data()
            return JsonResponse({
                'status': 'success',
                'data': scraped_data
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    # For GET requests, show a form or instructions
    return render(request, 'scraper/run_scraper.html')