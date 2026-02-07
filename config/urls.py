"""
URL configuration for Job Board Platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Job Board Platform API",
        default_version='v1',
        description="""
## Job Board Platform — REST API Documentation

A comprehensive REST API for a full-featured Job Board Platform.

### Key Features
- **Role-Based Access Control** — Admin, Employer, and User roles with fine-grained permissions
- **JWT Authentication** — Secure token-based auth with refresh tokens
- **Job Management** — Full CRUD with advanced filtering, search, and analytics
- **Application Tracking** — Multi-stage application pipeline with screening and interviews
- **Real-time Notifications** — Configurable notification preferences
- **Data Export** — CSV and JSON export for jobs, applications, and users
- **Audit Logging** — Complete change history and audit trail

### Authentication
All protected endpoints require a JWT token in the `Authorization` header:
```
Authorization: Bearer <your_access_token>
```
""",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@jobboard.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # API endpoints (versioned)
    path('api/v1/', include('config.urls_v1')),
    
    # Legacy API endpoints (redirect to v1)
    path('api/auth/', include('apps.accounts.urls')),
    path('api/jobs/', include('apps.jobs.urls')),
    path('api/jobs/', include('apps.jobs.urls_job_enhancements')),
    path('api/categories/', include('apps.jobs.urls_category')),
    path('api/applications/', include('apps.jobs.urls_application')),
    path('api/applications/', include('apps.jobs.urls_application_enhancements')),
    path('api/search/', include('apps.jobs.urls_search')),
    path('api/notifications/', include('apps.core.urls_notifications')),
    path('api/export/', include('apps.core.urls_export')),
    path('api/audit/', include('apps.core.urls_audit')),
    
    # Health checks and monitoring
    path('health/', include('apps.core.urls')),
    
    # File downloads (secure) - using different namespace to avoid conflict
    path('api/files/', include('apps.core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

