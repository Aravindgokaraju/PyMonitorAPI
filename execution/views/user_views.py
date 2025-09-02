from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from ..utils.premium import downgrade_to_demo, generate_upgrade_key, upgrade_to_premium

@api_view(['POST'])
@permission_classes([AllowAny])
def request_upgrade(request):
    """Request a premium upgrade (e.g., after payment)"""
    user = request.shared_user
    upgrade_key = generate_upgrade_key(user.username)
    
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