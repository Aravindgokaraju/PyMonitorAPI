from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from ..mongo_service import MongoService

@api_view(['POST'])
@permission_classes([AllowAny])
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
        if not request.data.get('url'):
            return Response({
                'status': 'error',
                'message': 'Flow url is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.shared_user
        is_demo = user.user_type == 'demo'
        
        flow_data = request.data.copy()
        success = mongo_service.create_flow(flow_data, is_demo)
        
        if not success:
            return Response({
                'status': 'error',
                'message': 'Failed to create flow (URL may already exist)'
            }, status=status.HTTP_400_BAD_REQUEST)

        created_flow = mongo_service.get_flow(
            query_filter={"url": flow_data["url"]},
            is_demo_user=is_demo,
            remove_id=False
        )
        
        if not created_flow:
            raise Exception("Flow created but not found")

        return Response({
            'status': 'success',
            'message': 'Flow created successfully',
            'data': created_flow
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
        "filter": {"key": "value"},
        "remove_id": true/false
    }
    """
    mongo_service = MongoService()
    
    try:
        query_filter = request.data.get('filter', {})
        remove_id = request.data.get('remove_id', True)
        user = request.shared_user
        is_demo_user = user.user_type == 'demo'

        flow = mongo_service.get_flow(query_filter, is_demo_user, remove_id)
        
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
                'message': f'Flow with ID {flow_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        return Response({
            'status': 'success',
            'data': flow
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({
            'status': 'error',
            'message': str(e)
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
        user = request.shared_user
        is_demo = user.user_type == 'demo'
        filter_query = request.data if request.method == 'POST' else None
        
        flows = mongo_service.get_all_flows(is_demo, filter_query)
        
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
    """
    mongo_service = MongoService()
    
    try:
        existing_flow = mongo_service.get_flow_by_id(flow_id)
        if not existing_flow:
            return Response({
                'status': 'not_found',
                'message': f'Flow with ID In API {flow_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
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