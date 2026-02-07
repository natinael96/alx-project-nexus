"""
URL configuration for Job Board Platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


def landing_page(request):
    """Root landing page — confirms the API is live."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Board Platform API</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #e2e8f0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            text-align: center;
            padding: 2rem;
            max-width: 600px;
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(34, 197, 94, 0.15);
            border: 1px solid rgba(34, 197, 94, 0.3);
            color: #4ade80;
            padding: 0.5rem 1.25rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            margin-bottom: 2rem;
        }
        .status-dot {
            width: 8px; height: 8px;
            background: #4ade80;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        h1 {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(to right, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.75rem;
        }
        .subtitle {
            color: #94a3b8;
            font-size: 1.125rem;
            margin-bottom: 2.5rem;
            line-height: 1.6;
        }
        .links {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            justify-content: center;
        }
        a.btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 600;
            text-decoration: none;
            font-size: 0.95rem;
            transition: all 0.2s;
        }
        a.btn-primary {
            background: #3b82f6;
            color: #fff;
        }
        a.btn-primary:hover { background: #2563eb; transform: translateY(-1px); }
        a.btn-secondary {
            background: rgba(255,255,255,0.08);
            color: #cbd5e1;
            border: 1px solid rgba(255,255,255,0.1);
        }
        a.btn-secondary:hover { background: rgba(255,255,255,0.12); transform: translateY(-1px); }
        .footer {
            margin-top: 3rem;
            color: #475569;
            font-size: 0.8rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="status-badge">
            <span class="status-dot"></span>
            All systems operational
        </div>
        <h1>Job Board Platform</h1>
        <p class="subtitle">
            The API is live and ready to accept requests.<br>
            Explore the endpoints using the interactive documentation below.
        </p>
        <div class="links">
            <a href="/api/docs/" class="btn btn-primary">
                &#128214; API Documentation
            </a>
            <a href="/api/redoc/" class="btn btn-secondary">
                &#128195; ReDoc
            </a>
            <a href="/admin/" class="btn btn-secondary">
                &#128274; Admin Panel
            </a>
        </div>
        <p class="footer">Job Board Platform API v1 &mdash; Powered by Django REST Framework</p>
    </div>
</body>
</html>"""
    return HttpResponse(html)

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
    # Landing page
    path('', landing_page, name='landing-page'),
    
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

