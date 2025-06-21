from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'websites', views.WebsiteViewSet)
router.register(r'skus', views.SKUViewSet)
router.register(r'pricedata', views.PriceDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('execute/', views.execute_scraping, name='execute-scraping'),
]