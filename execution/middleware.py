from django.utils.functional import SimpleLazyObject
from .models import AppUser

def get_shared_user(request):
    """
    Return the user for the current request.
    - If logged-in, return the real user.
    - Otherwise, return a single global demo user.
    """
    if hasattr(request, 'cached_shared_user'):
        return request.cached_shared_user

    # If the request has a logged-in user, use it
    if request.user.is_authenticated:
        request.cached_shared_user = request.user
        return request.cached_shared_user

    # Otherwise, use a single global demo user
    demo_user, _ = AppUser.objects.get_or_create(
        username="demo_user",
        defaults={
            'user_type': AppUser.IS_DEMO,
            'password': 'unused_password'
        }
    )
    request.cached_shared_user = demo_user
    return request.cached_shared_user

class SharedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Attach the shared user to all requests
        request.shared_user = SimpleLazyObject(lambda: get_shared_user(request))
        response = self.get_response(request)
        return response
