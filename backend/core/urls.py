"""
URL configuration for Finance Hub TDD project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include('apps.authentication.urls', namespace='auth')),
    path("api/", include('apps.companies.urls', namespace='companies')),
    path("api/banking/", include('apps.banking.urls', namespace='banking')),
    path("api/categories/", include('apps.categories.urls', namespace='categories')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
