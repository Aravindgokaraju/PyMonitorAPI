import json
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view
import logging
from rest_framework.response import Response
from rest_framework import status

from execution.scrape_website import ScrapingService
from .models import Website, SKU, PriceData, save_scraping_config
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

logger = logging.getLogger(__name__)

@api_view(['POST'])
def execute_scraping(request):
    try:
        # Initialize the scraping service
        scraper = ScrapingService()
        
        # Execute scraping (prints will go to console)
        logger.info("Starting scraping process...")
        results = scraper.scrape_websites()
        logger.info(f"Scraping completed with {len(results)} results")
        
        # Return results as JSON
        return Response({
            'status': 'success',
            'data': results
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def save_scraping_config_view(request):
    try:
        # DRF automatically parses JSON body into request.data
        # inserted_id = save_scraping_config(request.data)
        inserted_id = save_scraping_config(request.data)
        return Response({
            'status': 'success',
            'inserted_id': str(inserted_id)
        }, status=status.HTTP_201_CREATED)
        
    except json.JSONDecodeError:
        return Response({
            'status': 'error',
            'message': 'Invalid JSON format'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)