from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import flow_views, health_views, pricing_views, scraping_views, user_views
# from . import views

router = DefaultRouter()
router.register(r'skus', pricing_views.SKUViewSet)
router.register(r'pricedata', pricing_views.PriceDataViewSet)

urlpatterns = [
    path('', include(router.urls)),

    path('flows/create-config/', flow_views.create_flow_view, name='create-config'),
    path('flows/get/', flow_views.get_flow_view, name='get-flow'),
    path('flows/get/<str:flow_id>/', flow_views.get_flow_by_id_view, name='get-flow-by-id'),
    path('flows/', flow_views.get_all_flows_view, name='get-all-flows'),
    path('flows/update/<str:flow_id>/', flow_views.partial_update_flow_view, name='partial-update-flow'),
    path('flows/delete/<str:flow_id>/', flow_views.delete_flow_view, name='partial-delete-flow'),
    path('test-mongo/', health_views.test_mongo, name='test_mongo'),



    path('scrape/', scraping_views.start_worker, name='start-scraping'),
    path('status/', scraping_views.queue_status, name='queue-status'),


    path('apply-upgrade/', user_views.apply_upgrade, name='apply-upgrade'),
    path('apply-downgrade/', user_views.apply_downgrade, name='apply-downgrade'),

    path('health/', health_views.health_check, name='health_check'),
    path('job-result/<str:job_id>/', scraping_views.get_job_result, name='get_job_result'),


]