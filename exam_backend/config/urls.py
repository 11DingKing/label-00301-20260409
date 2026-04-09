"""
URL configuration for exam_backend project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# API v1 URLs
api_v1_patterns = [
    path('auth/', include('apps.accounts.urls.auth_urls')),
    path('users/', include('apps.accounts.urls.user_urls')),
    path('questions/', include('apps.questions.urls')),
    path('exams/', include('apps.exams.urls')),
    path('papers/', include('apps.papers.urls')),
    path('submissions/', include('apps.submissions.urls')),
    path('grading/', include('apps.grading.urls')),
    path('statistics/', include('apps.statistics.urls')),
    path('tags/', include('apps.tags.urls')),
    path('commons/', include('apps.commons.urls')),
]

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/', include(api_v1_patterns)),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Debug Toolbar (only in development)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
