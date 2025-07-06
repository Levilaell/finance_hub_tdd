from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

app_name = 'companies'

# Router principal
router = DefaultRouter()
router.register(r'companies', views.CompanyViewSet, basename='company')
router.register(r'subscription-plans', views.SubscriptionPlanViewSet)
router.register(r'subscriptions', views.SubscriptionViewSet, basename='subscription')

# Router aninhado para membros da empresa
companies_router = routers.NestedDefaultRouter(router, r'companies', lookup='company')
companies_router.register(r'members', views.CompanyUserViewSet, basename='company-members')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(companies_router.urls)),
]