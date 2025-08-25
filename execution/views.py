
from collections import defaultdict
from bson import ObjectId
from rest_framework.decorators import action 
from rest_framework import viewsets
from rest_framework.decorators import api_view
import logging
from rest_framework.response import Response
from rest_framework import status

from execution import mongo_service
from execution.browser_config.max_stealth_config import MaxStealthConfig
from execution.browser_config.stable_config import StableConfig
from execution.browser_config.stealth_config import StealthConfig
from execution.mongo_service import MongoService
from execution.scrape_website import ScrapingService
from execution.utils.premium import downgrade_to_demo, generate_upgrade_key, upgrade_to_premium
from .models import SKU, PriceData
from .serializers import SKUSerializer, PriceDataSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

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
    
    def get_best_prices_by_sku(self,price_data):
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
    
    @action(detail=False, methods=['get'],url_path='best_prices')
    def best_prices(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        best_prices_data = self.get_best_prices_by_sku(queryset)
        return Response(best_prices_data)

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
    
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_flow_view(request):
#     """
#     Create a new flow in MongoDB
#     Expected POST data format:
#     {
#         "name": "flow_name",
#         "steps": [...],
#         "url": "https://example.com",
#         ...other flow properties
#     }
#     """
#     mongo_service = MongoService()
    
#     try:
#         # Validate required fields
#         if not request.data.get('url'):
#             return Response({
#                 'status': 'error',
#                 'message': 'Flow url is required'
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         flow_data = request.data.copy()
#         if "_id" not in flow_data:
#             flow_data["_id"] = ObjectId()
        
#         # Create the flow in MongoDB
#         data_push = mongo_service.create_flow(flow_data)
        
#         if not data_push:
#             raise Exception("Failed to create flow")

#         return Response({
#             'status': 'success',
#             'message': 'Flow created successfully',
#             'data': {
#                 **flow_data,
#                 '_id': str(flow_data['_id'])  # Convert to string only in response
#             }
#         }, status=status.HTTP_201_CREATED)

#     except Exception as e:
#         return Response({
#             'status': 'error',
#             'message': f'Failed to create flow: {str(e)}'
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([AllowAny])  # ← Change to AllowAny for middleware approach
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
        
        # Get user from middleware
        user = request.shared_user  # From middleware
        is_demo = user.user_type == 'demo'
        
        flow_data = request.data.copy()
        
        # REMOVE manual _id creation - let MongoDB handle it!
        # if "_id" not in flow_data:
        #     flow_data["_id"] = ObjectId()
        
        # Create the flow in MongoDB
        success = mongo_service.create_flow(flow_data, is_demo)  # ← Pass is_demo
        
        if not success:
            return Response({
                'status': 'error',
                'message': 'Failed to create flow (URL may already exist)'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get the actual created flow from MongoDB
        created_flow = mongo_service.get_flow(
            query_filter={"url": flow_data["url"]},
            is_demo_user=is_demo,
            remove_id=False  # Keep _id for response
        )
        
        if not created_flow:
            raise Exception("Flow created but not found")

        return Response({
            'status': 'success',
            'message': 'Flow created successfully',
            'data': created_flow  # ← Return the actual MongoDB document
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
        user = request.shared_user  # From middleware
        is_demo_user = user.user_type == 'demo'

        flow = mongo_service.get_flow(query_filter,is_demo_user, remove_id)
        
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
    Get a flow by its ID.
    URL format: /flows/id/<str:flow_id>/
    """
    mongo_service = MongoService()
    
    try:
        flow = mongo_service.get_flow_by_id(flow_id)
        
        if not flow:
            return Response({
                'status': 'not_found',
                'message': f'Flow with ID {flow_id} not found'  # Corrected message to say ID instead of name
            }, status=status.HTTP_404_NOT_FOUND)
            
        return Response({
            'status': 'success',
            'data': flow
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({
            'status': 'error',
            'message': str(e)  # More specific error for invalid ID format
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Failed to fetch flow: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def get_all_flows_view(request):
    """
    Get all flows (optionally filtered).
    For POST requests, accepts filter criteria in request body.
    """
    mongo_service = MongoService()
    
    try:
        user = request.shared_user  # From middleware
        is_demo = user.user_type == 'demo'

        filter_query = request.data if request.method == 'POST' else None
        
        # Option 1: Both positional (cleanest)
        flows = mongo_service.get_all_flows(is_demo, filter_query)
        
        # Option 2: Both keyword (more explicit)
        # flows = mongo_service.get_all_flows(
        #     is_demo_user=is_demo,
        #     filter_query=filter_query
        # )
        
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
    Partially update a flow by ID and return the updated document.
    URL format: /flows/<str:flow_id>/
    Expected PATCH data format:
    {
        "field1": "new_value1",
        "field2": "new_value2"
    }
    Returns:
    {
        "status": "success",
        "message": "Flow updated successfully",
        "data": { /* the complete updated flow document */ }
    }
    """
    mongo_service = MongoService()
    
    try:
        # First perform the update
        success = mongo_service.partial_update_flow(flow_id, request.data)
        
        if not success:
            return Response({
                'status': 'not_modified',
                'message': 'No changes were made (flow not found or data identical)'
            }, status=status.HTTP_304_NOT_MODIFIED)
            
        # Then fetch the updated document
        # updated_flow = success.data.data
            
        return Response({
            'status': 'success',
            'message': 'Flow updated successfully',
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

@api_view(['DELETE'])
def delete_flow_view(request, flow_id: str):
    """
    Delete a flow by ID.
    URL format: /flows/<str:flow_id>/
    Returns:
    {
        "status": "success",
        "message": "Flow deleted successfully"
    }
    """
    mongo_service = MongoService()
    
    try:
        # First check if flow exists
        existing_flow = mongo_service.get_flow_by_id(flow_id)
        if not existing_flow:
            return Response({
                'status': 'not_found',
                'message': f'Flow with ID In API {flow_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Perform deletion
        delete_result = mongo_service.delete_flow(flow_id)
        
        if not delete_result:
            raise Exception("Deletion operation failed")
            
        return Response({
            'status': 'success',
            'message': 'Flow deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({
            'status': 'error',
            'message': f'Invalid flow ID: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Failed to delete flow: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_flows(request):
#     """Get flows based on user type (no authentication required)"""
#     user = request.shared_user  # From middleware
    
#     flows = mongo_service.get_all_flows(is_demo_user=(user.user_type == 'demo'))
    
#     return Response({
#         'user_type': user.user_type,
#         'flows': flows
#     })

@api_view(['POST'])
@permission_classes([AllowAny])
def request_upgrade(request):
    """Request a premium upgrade (e.g., after payment)"""
    user = request.shared_user
    upgrade_key = generate_upgrade_key(user.username)
    
    # In real app, you might:
    # 1. Process payment here
    # 2. Send email with upgrade key
    # 3. Store upgrade key for validation
    
    return Response({
        'upgrade_key': upgrade_key,
        'message': 'Upgrade key generated. Process payment to complete upgrade.'
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def apply_upgrade(request):
    """Apply premium upgrade with validation key"""
    user = request.shared_user
    upgrade_key = request.data.get('upgrade_key')
    
    success, message = upgrade_to_premium(user, upgrade_key)
    
    if success:
        return Response({
            'message': message,
            'user_type': user.user_type
        })
    else:
        return Response({
            'error': message
        }, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def apply_downgrade(request):
    """Apply premium upgrade with validation key"""
    user = request.shared_user
    upgrade_key = request.data.get('upgrade_key')
    
    success, message = downgrade_to_demo(user, upgrade_key)
    
    if success:
        return Response({
            'message': message,
            'user_type': user.user_type
        })
    else:
        return Response({
            'error': message
        }, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
def test_mongo(request):
    try:
        mongo_service = MongoService()
        # Simple count query to test connection
        count = mongo_service.collection.count_documents({})
        return Response({"status": "success", "count": count})
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)
    
@api_view(['GET'])
def health_check(request):
    return Response({"status": "healthy", "service": "backend"})