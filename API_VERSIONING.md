# API Versioning Guide

This document explains the API versioning strategy for the Job Board Platform.

## Versioning Strategy

The API uses URL-based versioning with the following structure:

```
/api/v1/...  # Current version
/api/v2/...  # Future versions
```

## Current Version: v1

All current endpoints are available under `/api/v1/`:

- `/api/v1/auth/` - Authentication endpoints
- `/api/v1/jobs/` - Job endpoints
- `/api/v1/categories/` - Category endpoints
- `/api/v1/applications/` - Application endpoints
- `/api/v1/search/` - Search endpoints
- `/api/v1/notifications/` - Notification endpoints
- `/api/v1/export/` - Data export endpoints
- `/api/v1/audit/` - Audit logging endpoints

## Legacy Endpoints

For backward compatibility, legacy endpoints (without version prefix) are still available and redirect to v1:

- `/api/auth/` → `/api/v1/auth/`
- `/api/jobs/` → `/api/v1/jobs/`
- etc.

## Deprecation Policy

1. **Deprecation Notice**: When an endpoint is deprecated, it will be marked with a deprecation header:
   ```
   X-API-Deprecated: true
   X-API-Deprecation-Date: 2024-12-31
   X-API-Sunset-Date: 2025-06-30
   ```

2. **Deprecation Period**: Deprecated endpoints will remain available for at least 6 months.

3. **Version Migration**: Users should migrate to the new version before the sunset date.

## Adding New Versions

To add a new API version (e.g., v2):

1. Create `config/urls_v2.py` with new endpoint structure
2. Update `config/urls.py` to include v2 routes
3. Update Swagger documentation
4. Announce deprecation of v1 endpoints (if applicable)

## Best Practices

1. **Always use versioned URLs** in new integrations
2. **Monitor deprecation headers** in API responses
3. **Plan migrations** before sunset dates
4. **Test thoroughly** when upgrading to new versions
