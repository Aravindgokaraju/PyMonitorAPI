
from rest_framework import viewsets
from rest_framework.decorators import api_view
import logging
from rest_framework.response import Response
from rest_framework import status

from execution.browser_config.max_stealth_config import MaxStealthConfig
from execution.browser_config.stable_config import StableConfig
from execution.browser_config.stealth_config import StealthConfig
from execution.mongo_service import MongoService
from execution.scrape_website import ScrapingService
from .models import SKU, PriceData
from .serializers import SKUSerializer, PriceDataSerializer


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

# def run_scraper_view(request):
#     if request.method == 'POST':
#         try:
#             scraper = ScrapingService()
#             scraped_data = scraper.scrape_data()
#             return JsonResponse({
#                 'status': 'success',
#                 'data': scraped_data
#             })
#         except Exception as e:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': str(e)
#             }, status=500)
    
#     # For GET requests, show a form or instructions
#     return render(request, 'scraper/run_scraper.html')

logger = logging.getLogger(__name__)

@api_view(['POST'])
def execute_scraping(request):
    try:
        # Initialize the scraping service
        scraper = ScrapingService()
        
        # Execute scraping (prints will go to console)
        logger.info("Starting scraping process...")
        results = scraper.scrape_websites(request.data)
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
def stable_test(request):
    try:
        # Initialize the scraping service
        config = StableConfig()
        
        # Execute scraping (prints will go to console)
        logger.info("Starting scraping process...")
        results = config.test_driver(delay_seconds=100)
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
def max_stealth_test(request):
    try:
        # Initialize the scraping service
        config = MaxStealthConfig()
        
        # Execute scraping (prints will go to console)
        logger.info("Starting scraping process...")
        results = config.test_stealth(delay_seconds=100)
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
def standard_stealth_test(request):
    try:
        # Initialize the scraping service
        config = StealthConfig()
        
        # Execute scraping (prints will go to console)
        logger.info("Starting scraping process...")
        results = config.test_stealth(delay_seconds=100)
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
def create_flow_view(request):
    """
    Create a new flow in MongoDB
    Expected POST data format:
    {
        "name": "flow_name",
        "steps": [...],
        "url": "https://example.com",
        ...other flow properties
    }
    """
    mongo_service = MongoService()
    
    try:
        # Validate required fields
        if not request.data.get('url'):
            return Response({
                'status': 'error',
                'message': 'Flow url is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create the flow in MongoDB
        data_push = mongo_service.create_flow(request.data)
        
        if not data_push:
            raise Exception("Failed to create flow")

        return Response({
            'status': 'success',
            'message': 'Flow created successfully',
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Failed to create flow: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def get_flow_view(request):
    """
    Get a single flow document by filter criteria.
    Expected POST data format:
    {
        "filter": {"key": "value"},  # Your query filter
        "remove_id": true/false      # Whether to remove _id (default true)
    }
    """
    mongo_service = MongoService()
    
    try:
        query_filter = request.data.get('filter', {})
        remove_id = request.data.get('remove_id', True)
        
        flow = mongo_service.get_flow(query_filter, remove_id)
        
        if not flow:
            return Response({
                'status': 'not_found',
                'message': 'No matching flow found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        return Response({
            'status': 'success',
            'data': flow
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Failed to fetch flow: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_flow_by_id_view(request, flow_id: str):
    """
    Get a flow by its name.
    URL format: /flows/name/<str:name>/
    """
    mongo_service = MongoService()
    
    try:
        flow = mongo_service.get_flow_by_id(flow_id)
        
        if not flow:
            return Response({
                'status': 'not_found',
                'message': f'Flow with name {flow_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        return Response({
            'status': 'success',
            'data': flow
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Failed to fetch flow: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET', 'POST'])
def get_all_flows_view(request):
    """
    Get all flows (optionally filtered).
    For POST requests, accepts filter criteria in request body.
    """
    mongo_service = MongoService()
    
    try:
        filter_query = request.data if request.method == 'POST' else None
        flows = mongo_service.get_all_flows(filter_query)
        
        return Response({
            'status': 'success',
            'count': len(flows),
            'data': flows
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Failed to fetch flows: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['PATCH'])
def partial_update_flow_view(request, flow_id: str):
    """
    Partially update a flow by ID.
    URL format: /flows/<str:flow_id>/
    Expected PATCH data format:
    {
        "field1": "new_value1",
        "field2": "new_value2"
    }
    """
    mongo_service = MongoService()
    
    try:
        success = mongo_service.partial_update_flow(flow_id, request.data)
        
        if not success:
            return Response({
                'status': 'not_modified',
                'message': 'No changes were made (flow not found or data identical)'
            }, status=status.HTTP_304_NOT_MODIFIED)
            
        return Response({
            'status': 'success',
            'message': 'Flow updated successfully'
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({
            'status': 'error',
            'message': f'Invalid flow ID: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Failed to update flow: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)