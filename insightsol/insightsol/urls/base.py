from mainsite import views as mainsite_views
from django.contrib import admin
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from django.urls import include, path
from django.conf import settings
from mainsite.api import controllers as mainsite_api_views
from .mainsite import urlpatterns as mainsite_url_patterns

urlpatterns = [
    path("", mainsite_views.home, name="home"),
    path("api/<int:version>/health",mainsite_api_views.HealthCheckAPI.as_view()),
    path("internal-admin/", admin.site.urls, name="admin"),
    path('favicon.ico', RedirectView.as_view(url='https://www.ignitesol.com/wp-content/uploads/2017/08/cropped-Graphic-32x32.png')),  # Adjust the path as needed
]

urlpatterns += mainsite_url_patterns

if settings.DEBUG:

    documentation_url_patterns = [
        # Schema generation
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

        # Swagger UI
        path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

        # ReDoc UI
        path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]
    urlpatterns += documentation_url_patterns