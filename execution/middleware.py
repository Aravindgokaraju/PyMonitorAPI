# middleware.py
from django.utils.functional import SimpleLazyObject
from .models import AppUser

def get_shared_user(request):
    """Get shared user or create session-based temporary user"""
    if not hasattr(request, 'cached_shared_user'):
        # Use session key to identify anonymous users
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key
            
        username = f"anon_{session_key}"
        
        user, created = AppUser.objects.get_or_create(
            username=username,
            defaults={
                'user_type': 'demo',
                'password': 'unused_password'
            }
        )
        request.cached_shared_user = user
    return request.cached_shared_user

class SharedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        # Attach shared user to all requests
        request.shared_user = SimpleLazyObject(lambda: get_shared_user(request))
        response = self.get_response(request)
        return response