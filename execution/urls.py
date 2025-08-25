from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'skus', views.SKUViewSet)
router.register(r'pricedata', views.PriceDataViewSet)

urlpatterns = [
    path('', include(router.urls)),

    path('flows/create-config/', views.create_flow_view, name='create-config'),
    path('flows/get/', views.get_flow_view, name='get-flow'),
    path('flows/get/<str:flow_id>/', views.get_flow_by_id_view, name='get-flow-by-id'),
    path('flows/', views.get_all_flows_view, name='get-all-flows'),
    path('flows/update/<str:flow_id>/', views.partial_update_flow_view, name='partial-update-flow'),
    path('flows/delete/<str:flow_id>/', views.delete_flow_view, name='partial-delete-flow'),
    path('test-mongo/', views.test_mongo, name='test_mongo'),



    path('execute/', views.execute_scraping, name='execute-scraping'),
    path('max-stealth-test/', views.max_stealth_test, name='max-stealth-test'),
    path('stealth-test/', views.standard_stealth_test, name='standard-stealth-test'),
    path('stable-test/', views.stable_test, name='stable-test'),

    path('apply-upgrade/', views.apply_upgrade, name='apply-upgrade'),
    path('apply-downgrade/', views.apply_downgrade, name='apply-downgrade'),

    path('health/', views.health_check, name='health_check'),


]