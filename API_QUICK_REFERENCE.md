# API Quick Reference Card

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication Header
```
Authorization: Bearer <access_token>
```

## Common Endpoints

### Authentication
```
POST   /auth/register/              Register new user
POST   /auth/login/                 Login (get tokens)
POST   /auth/refresh/               Refresh access token
GET    /auth/me/                    Get current user
PATCH  /auth/me/update/             Update current user
POST   /auth/change-password/       Change password
```

### Jobs
```
GET    /jobs/                       List jobs (with filters)
GET    /jobs/{id}/                  Get job details
POST   /jobs/                       Create job (employer/admin)
PUT    /jobs/{id}/                  Update job (owner/admin)
PATCH  /jobs/{id}/                  Partial update job
DELETE /jobs/{id}/                  Delete job (owner/admin)
GET    /jobs/search/                Search jobs
GET    /jobs/categories/            List categories
```

### Applications
```
GET    /jobs/applications/          List applications
GET    /jobs/applications/{id}/     Get application details
POST   /jobs/applications/          Create application
PATCH  /jobs/applications/{id}/     Update application status
POST   /jobs/applications/{id}/withdraw/  Withdraw application
```

### Profile
```
GET    /auth/profile/               Get full profile
POST   /auth/profile/skills/        Add skill
PUT    /auth/profile/skills/{id}/   Update skill
DELETE /auth/profile/skills/{id}/   Delete skill
POST   /auth/profile/education/     Add education
POST   /auth/profile/work-history/  Add work history
POST   /auth/profile/social-links/  Add social link
POST   /auth/profile/saved-jobs/   Save job
DELETE /auth/profile/saved-jobs/{id}/  Unsave job
```

### Notifications
```
GET    /core/notifications/         List notifications
POST   /core/notifications/{id}/mark-read/  Mark as read
POST   /core/notifications/mark-all-read/   Mark all as read
```

## Common Query Parameters

### Pagination
```
?page=1&page_size=20
```

### Job Filters
```
?category=<uuid>
?location=New York
?job_type=full-time
?status=active
?is_featured=true
?min_salary=50000
?max_salary=100000
?search=developer
?ordering=-created_at
```

### Application Filters
```
?job=<uuid>
?status=pending
?ordering=-applied_at
```

## Status Codes
```
200  OK
201  Created
204  No Content
400  Bad Request
401  Unauthorized
403  Forbidden
404  Not Found
429  Too Many Requests
500  Server Error
```

## Data Types

### UUID Format
```
550e8400-e29b-41d4-a716-446655440000
```

### Date Format (ISO 8601)
```
2026-02-07T10:00:00Z
```

### Decimal Format
```
"80000.00"  (as string)
```

## File Uploads

### Resume (Application)
- Field: `resume`
- Formats: PDF, DOC, DOCX
- Max size: 5MB
- Content-Type: `multipart/form-data`

### Profile Picture
- Field: `profile_picture`
- Formats: JPG, JPEG, PNG
- Max size: 2MB
- Content-Type: `multipart/form-data`

## Error Response Format
```json
{
  "detail": "Error message",
  "code": "error_code"
}
```

## Validation Error Format
```json
{
  "field_name": ["Error message"],
  "non_field_errors": ["General error"]
}
```

## Swagger Documentation
```
http://localhost:8000/api/docs/
```
