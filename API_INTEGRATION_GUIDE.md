# API Integration Guide for Frontend Developers

This comprehensive guide provides everything you need to integrate the Job Board Platform API into your frontend application.

## Table of Contents

1. [Base Configuration](#base-configuration)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Formats](#requestresponse-formats)
5. [Error Handling](#error-handling)
6. [Pagination](#pagination)
7. [Filtering & Search](#filtering--search)
8. [File Uploads](#file-uploads)
9. [WebSocket/Real-time Updates](#websocketreal-time-updates)
10. [Code Examples](#code-examples)
11. [Testing](#testing)

---

## Base Configuration

### Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

### API Version

All endpoints are prefixed with `/api/v1/`

### Content Type

All requests should include:
```
Content-Type: application/json
```

### CORS

The API supports CORS. Configure your frontend to include credentials:

```javascript
// Example: Axios configuration
axios.defaults.withCredentials = true;
```

---

## Authentication

### Overview

The API uses **JWT (JSON Web Tokens)** for authentication. You'll receive two tokens:
- **Access Token**: Short-lived (default: 60 minutes) - used for API requests
- **Refresh Token**: Long-lived (default: 24 hours) - used to get new access tokens

### Authentication Flow

1. **Register** or **Login** to get tokens
2. **Store tokens** securely (localStorage, sessionStorage, or httpOnly cookies)
3. **Include access token** in all authenticated requests
4. **Refresh token** when access token expires

### Register User

**Endpoint:** `POST /api/v1/auth/register/`

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user"  // Optional: "user" | "employer" (default: "user")
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": "8dd98fbe-86dc-4c95-8d5f-eae043788543",
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "role": "user",
    "phone_number": null,
    "profile_picture": null,
    "bio": null,
    "date_joined": "2026-02-07T19:30:00Z",
    "last_login": null
  },
  "message": "User registered successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Validation errors
- `429 Too Many Requests`: Rate limit exceeded

### Login

**Endpoint:** `POST /api/v1/auth/login/`

**Request Body:**
```json
{
  "username": "johndoe",  // Can be username or email
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "8dd98fbe-86dc-4c95-8d5f-eae043788543",
    "username": "johndoe",
    "email": "john@example.com",
    "role": "user",
    // ... other user fields
  }
}
```

### Refresh Token

**Endpoint:** `POST /api/v1/auth/refresh/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Get Current User

**Endpoint:** `GET /api/v1/auth/me/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "8dd98fbe-86dc-4c95-8d5f-eae043788543",
  "username": "johndoe",
  "email": "john@example.com",
  "role": "user",
  // ... other user fields
}
```

### Update Current User

**Endpoint:** `PUT /api/v1/auth/me/update/` or `PATCH /api/v1/auth/me/update/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "bio": "Software developer with 5 years of experience"
}
```

### Change Password

**Endpoint:** `POST /api/v1/auth/change-password/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword123!",
  "confirm_password": "NewPassword123!"
}
```

---

## API Endpoints

### Jobs

#### List Jobs

**Endpoint:** `GET /api/v1/jobs/`

**Query Parameters:**
- `category` (UUID): Filter by category ID
- `location` (string): Filter by location (case-insensitive partial match)
- `job_type` (string): `full-time` | `part-time` | `contract` | `internship` | `freelance`
- `status` (string): `draft` | `active` | `closed`
- `is_featured` (boolean): Filter featured jobs
- `min_salary` (number): Minimum salary filter
- `max_salary` (number): Maximum salary filter
- `search` (string): Search in title, description, requirements
- `ordering` (string): Order by field (prefix with `-` for descending)
  - Available: `created_at`, `-created_at`, `salary_min`, `-salary_min`, `title`, `-title`
- `page` (number): Page number (default: 1)
- `page_size` (number): Items per page (default: 20, max: 100)

**Example Request:**
```
GET /api/v1/jobs/?category=123e4567-e89b-12d3-a456-426614174000&location=New York&job_type=full-time&search=developer&page=1&page_size=20
```

**Response (200 OK):**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/jobs/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Senior Software Engineer",
      "description": "We are looking for...",
      "requirements": "Requirements:\n- 5+ years experience...",
      "category": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Technology",
        "slug": "technology"
      },
      "employer": {
        "id": "789e0123-e45b-67c8-d901-234567890abc",
        "username": "techcorp",
        "email": "hr@techcorp.com"
      },
      "location": "New York, NY",
      "job_type": "full-time",
      "salary_min": "80000.00",
      "salary_max": "120000.00",
      "status": "active",
      "approval_status": "approved",
      "is_featured": true,
      "view_count": 245,
      "application_deadline": "2026-03-01",
      "created_at": "2026-02-01T10:00:00Z",
      "updated_at": "2026-02-07T15:30:00Z"
    }
    // ... more jobs
  ]
}
```

#### Get Job Details

**Endpoint:** `GET /api/v1/jobs/{job_id}/`

**Example:**
```
GET /api/v1/jobs/550e8400-e29b-41d4-a716-446655440000/
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Senior Software Engineer",
  "description": "Full job description...",
  "requirements": "Detailed requirements...",
  "category": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Technology",
    "slug": "technology"
  },
  "employer": {
    "id": "789e0123-e45b-67c8-d901-234567890abc",
    "username": "techcorp",
    "email": "hr@techcorp.com",
    "first_name": "Tech",
    "last_name": "Corp"
  },
  "location": "New York, NY",
  "job_type": "full-time",
  "salary_min": "80000.00",
  "salary_max": "120000.00",
  "status": "active",
  "approval_status": "approved",
  "is_featured": true,
  "view_count": 245,
  "application_deadline": "2026-03-01",
  "created_at": "2026-02-01T10:00:00Z",
  "updated_at": "2026-02-07T15:30:00Z"
}
```

#### Create Job (Employer/Admin Only)

**Endpoint:** `POST /api/v1/jobs/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "Senior Software Engineer",
  "description": "We are looking for an experienced software engineer...",
  "requirements": "Requirements:\n- 5+ years of experience\n- Strong problem-solving skills",
  "category": "123e4567-e89b-12d3-a456-426614174000",
  "location": "New York, NY",
  "job_type": "full-time",
  "salary_min": "80000.00",
  "salary_max": "120000.00",
  "application_deadline": "2026-03-01",
  "is_featured": false
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Senior Software Engineer",
  // ... job fields
}
```

#### Update Job (Owner/Admin Only)

**Endpoint:** `PUT /api/v1/jobs/{job_id}/` or `PATCH /api/v1/jobs/{job_id}/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:** (Same as create, all fields optional for PATCH)

#### Delete Job (Owner/Admin Only)

**Endpoint:** `DELETE /api/v1/jobs/{job_id}/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

### Applications

#### List Applications

**Endpoint:** `GET /api/v1/jobs/applications/` or `GET /api/v1/applications/`

**Note:** Applications can be accessed at either endpoint:
- `/api/v1/jobs/applications/` (nested under jobs - recommended)
- `/api/v1/applications/` (standalone)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `job` (UUID): Filter by job ID
- `status` (string): `pending` | `reviewed` | `accepted` | `rejected`
- `ordering` (string): Order by field
- `page` (number): Page number
- `page_size` (number): Items per page

**For Applicants:** Returns only user's applications
**For Employers:** Returns applications for their jobs
**For Admins:** Returns all applications

**Response (200 OK):**
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "job": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Senior Software Engineer"
      },
      "applicant": {
        "id": "8dd98fbe-86dc-4c95-8d5f-eae043788543",
        "username": "johndoe",
        "email": "john@example.com"
      },
      "cover_letter": "Dear Hiring Manager...",
      "resume": "https://storage.example.com/resumes/johndoe_resume.pdf",
      "status": "pending",
      "applied_at": "2026-02-07T10:00:00Z",
      "reviewed_at": null
    }
    // ... more applications
  ]
}
```

#### Create Application

**Endpoint:** `POST /api/v1/jobs/applications/` or `POST /api/v1/applications/`

**Note:** Applications can be created at either endpoint:
- `/api/v1/jobs/applications/` (nested under jobs - recommended)
- `/api/v1/applications/` (standalone)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
job: "550e8400-e29b-41d4-a716-446655440000"
cover_letter: "Dear Hiring Manager, I am writing to express my interest..."
resume: <file> (PDF, DOC, DOCX, max 5MB)
```

**Response (201 Created):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "job": "550e8400-e29b-41d4-a716-446655440000",
  "applicant": "8dd98fbe-86dc-4c95-8d5f-eae043788543",
  "cover_letter": "Dear Hiring Manager...",
  "resume": "https://storage.example.com/resumes/johndoe_resume.pdf",
  "status": "pending",
  "applied_at": "2026-02-07T10:00:00Z"
}
```

#### Get Application Details

**Endpoint:** `GET /api/v1/jobs/applications/{application_id}/`

**Headers:**
```
Authorization: Bearer <access_token>
```

#### Update Application Status (Employer/Admin Only)

**Endpoint:** `PATCH /api/v1/jobs/applications/{application_id}/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "status": "reviewed"  // or "accepted" | "rejected"
}
```

#### Withdraw Application

**Endpoint:** `POST /api/v1/jobs/applications/{application_id}/withdraw/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "reason": "Found another position"  // Optional
}
```

### Categories

#### List Categories

**Endpoint:** `GET /api/v1/jobs/categories/`

**Response (200 OK):**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Technology",
    "slug": "technology",
    "description": "Software development, IT, and tech jobs",
    "parent": null,
    "job_count": 45
  },
  {
    "id": "223e4567-e89b-12d3-a456-426614174001",
    "name": "Software Development",
    "slug": "software-development",
    "description": null,
    "parent": "123e4567-e89b-12d3-a456-426614174000",
    "job_count": 30
  }
]
```

### User Profile

#### Get User Profile

**Endpoint:** `GET /api/v1/auth/profile/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "8dd98fbe-86dc-4c95-8d5f-eae043788543",
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "bio": "Software developer with 5 years of experience",
    "profile_picture": "https://storage.example.com/profiles/johndoe.jpg"
  },
  "skills": [
    {
      "id": "skill-uuid-1",
      "name": "Python",
      "level": "advanced",
      "years_of_experience": 5
    }
  ],
  "education": [
    {
      "id": "edu-uuid-1",
      "institution": "University of Technology",
      "degree": "Bachelor of Science",
      "field_of_study": "Computer Science",
      "start_date": "2015-09-01",
      "end_date": "2019-06-01",
      "is_current": false
    }
  ],
  "work_history": [
    {
      "id": "work-uuid-1",
      "company": "Tech Corp",
      "position": "Software Engineer",
      "start_date": "2019-07-01",
      "end_date": null,
      "is_current": true,
      "description": "Developed web applications...",
      "location": "New York, NY"
    }
  ],
  "social_links": [
    {
      "id": "social-uuid-1",
      "platform": "linkedin",
      "url": "https://linkedin.com/in/johndoe",
      "is_public": true
    }
  ],
  "preferences": {
    "id": "pref-uuid-1",
    "email_notifications": true,
    "job_alerts": true,
    "newsletter": false
  }
}
```

#### Update Skills

**Endpoint:** `POST /api/v1/auth/profile/skills/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "React",
  "level": "intermediate",
  "years_of_experience": 2
}
```

**Update/Delete:** `PUT /api/v1/auth/profile/skills/{skill_id}/` or `DELETE /api/v1/auth/profile/skills/{skill_id}/`

Similar endpoints exist for:
- Education: `/api/v1/auth/profile/education/`
- Work History: `/api/v1/auth/profile/work-history/`
- Social Links: `/api/v1/auth/profile/social-links/`
- Portfolio: `/api/v1/auth/profile/portfolio/`

### Saved Jobs

#### List Saved Jobs

**Endpoint:** `GET /api/v1/auth/profile/saved-jobs/`

**Headers:**
```
Authorization: Bearer <access_token>
```

#### Save Job

**Endpoint:** `POST /api/v1/auth/profile/saved-jobs/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "job": "550e8400-e29b-41d4-a716-446655440000",
  "notes": "Interested in this position"  // Optional
}
```

#### Unsave Job

**Endpoint:** `DELETE /api/v1/auth/profile/saved-jobs/{saved_job_id}/`

### Notifications

#### List Notifications

**Endpoint:** `GET /api/v1/core/notifications/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `is_read` (boolean): Filter by read status
- `notification_type` (string): Filter by type
- `page` (number): Page number
- `page_size` (number): Items per page

**Response (200 OK):**
```json
{
  "count": 10,
  "unread_count": 3,
  "results": [
    {
      "id": "notif-uuid-1",
      "title": "New Application",
      "message": "New application received for 'Senior Software Engineer'",
      "notification_type": "job_application",
      "is_read": false,
      "priority": "high",
      "action_url": "/api/applications/a1b2c3d4-e5f6-7890-abcd-ef1234567890/",
      "created_at": "2026-02-07T10:00:00Z"
    }
  ]
}
```

#### Mark Notification as Read

**Endpoint:** `POST /api/v1/core/notifications/{notification_id}/mark-read/`

**Headers:**
```
Authorization: Bearer <access_token>
```

#### Mark All as Read

**Endpoint:** `POST /api/v1/core/notifications/mark-all-read/`

**Headers:**
```
Authorization: Bearer <access_token>
```

### Search

#### Search Jobs

**Endpoint:** `GET /api/v1/jobs/search/`

**Query Parameters:**
- `q` (string): Search query
- `category` (UUID): Filter by category
- `location` (string): Filter by location
- `job_type` (string): Filter by job type
- `min_salary` (number): Minimum salary
- `max_salary` (number): Maximum salary
- `page` (number): Page number
- `page_size` (number): Items per page

**Response:** Same as job list endpoint

#### Save Search

**Endpoint:** `POST /api/v1/jobs/search/save/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "query": "software engineer",
  "filters": {
    "category": "123e4567-e89b-12d3-a456-426614174000",
    "location": "New York",
    "job_type": "full-time"
  },
  "name": "My Software Engineer Search"  // Optional
}
```

---

## Request/Response Formats

### UUID Format

All IDs are UUIDs (Universally Unique Identifiers) in the format:
```
550e8400-e29b-41d4-a716-446655440000
```

### Date/Time Format

All dates and times are in ISO 8601 format (UTC):
```
2026-02-07T10:00:00Z
```

### Decimal Format

Monetary values (salaries) are returned as strings with 2 decimal places:
```
"80000.00"
```

### File URLs

File URLs (resumes, profile pictures) are returned as full URLs:
```
https://storage.example.com/resumes/johndoe_resume.pdf
```

---

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message here",
  "code": "error_code"  // Optional
}
```

### HTTP Status Codes

- `200 OK`: Success
- `201 Created`: Resource created successfully
- `204 No Content`: Success (no content to return)
- `400 Bad Request`: Validation error or invalid request
- `401 Unauthorized`: Authentication required or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Validation Errors

**Response (400 Bad Request):**
```json
{
  "field_name": [
    "Error message for this field"
  ],
  "non_field_errors": [
    "General error message"
  ]
}
```

**Example:**
```json
{
  "email": [
    "A user with this email already exists."
  ],
  "password": [
    "This password is too common.",
    "This password is too short. It must contain at least 8 characters."
  ]
}
```

### Authentication Errors

**Response (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

or

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

### Permission Errors

**Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Not Found Errors

**Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

### Rate Limit Errors

**Response (429 Too Many Requests):**
```json
{
  "detail": "Request was throttled. Expected available in 60 seconds."
}
```

---

## Pagination

All list endpoints support pagination using the standard Django REST Framework pagination format.

### Request

Add query parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

### Response

```json
{
  "count": 150,  // Total number of items
  "next": "http://localhost:8000/api/v1/jobs/?page=3",
  "previous": "http://localhost:8000/api/v1/jobs/?page=1",
  "results": [
    // ... items
  ]
}
```

### Example Usage

```javascript
// Fetch first page
const response = await fetch('/api/v1/jobs/?page=1&page_size=20');

// Fetch next page
if (response.data.next) {
  const nextPage = await fetch(response.data.next);
}
```

---

## Filtering & Search

### Common Filters

Most list endpoints support:
- `search`: Full-text search
- `ordering`: Sort by field (prefix with `-` for descending)
- `page`: Page number
- `page_size`: Items per page

### Job Filters

- `category`: UUID
- `location`: String (case-insensitive partial match)
- `job_type`: `full-time` | `part-time` | `contract` | `internship` | `freelance`
- `status`: `draft` | `active` | `closed`
- `is_featured`: Boolean
- `min_salary`: Number
- `max_salary`: Number
- `search`: String (searches title, description, requirements)

### Application Filters

- `job`: UUID
- `status`: `pending` | `reviewed` | `accepted` | `rejected`
- `ordering`: `applied_at`, `-applied_at`, `status`

### User Filters (Admin Only)

- `role`: `admin` | `employer` | `user`
- `is_active`: Boolean
- `search`: String (searches username, email, first_name, last_name)

---

## File Uploads

### Upload Resume

**Endpoint:** `POST /api/v1/jobs/applications/`

**Content-Type:** `multipart/form-data`

**Form Data:**
```
job: "550e8400-e29b-41d4-a716-446655440000"
cover_letter: "Dear Hiring Manager..."
resume: <file>
```

**File Requirements:**
- Formats: PDF, DOC, DOCX
- Max size: 5MB
- Field name: `resume`

### Upload Profile Picture

**Endpoint:** `PATCH /api/v1/auth/me/update/`

**Content-Type:** `multipart/form-data`

**Form Data:**
```
profile_picture: <file>
```

**File Requirements:**
- Formats: JPG, JPEG, PNG
- Max size: 2MB
- Field name: `profile_picture`

### Download Files

**Resume Download:**
```
GET /api/v1/core/files/resumes/{application_id}/
Authorization: Bearer <access_token>
```

**Profile Picture Download:**
```
GET /api/v1/core/files/profiles/{user_id}/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `signed=true`: Get signed URL instead of direct download

---

## WebSocket/Real-time Updates

Currently, the API does not support WebSocket connections. Real-time updates can be achieved through:

1. **Polling**: Periodically fetch notifications/updates
2. **Server-Sent Events (SSE)**: Not currently implemented
3. **WebSocket**: Not currently implemented

**Recommended Approach:**
- Poll notifications endpoint every 30-60 seconds when user is active
- Use WebSocket libraries if you implement your own WebSocket server

---

## Code Examples

### JavaScript/TypeScript with Fetch API

```typescript
// API Client Class
class JobBoardAPI {
  private baseURL: string;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.loadTokens();
  }

  private loadTokens() {
    this.accessToken = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
  }

  private saveTokens(access: string, refresh: string) {
    this.accessToken = access;
    this.refreshToken = refresh;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  }

  private async request(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const url = `${this.baseURL}/api/v1${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle token refresh on 401
    if (response.status === 401 && this.refreshToken) {
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        // Retry original request
        headers['Authorization'] = `Bearer ${this.accessToken}`;
        return fetch(url, { ...options, headers });
      }
    }

    return response;
  }

  async login(username: string, password: string) {
    const response = await this.request('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    this.saveTokens(data.access, data.refresh);
    return data;
  }

  async register(userData: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
  }) {
    const response = await this.request('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw error;
    }

    return response.json();
  }

  async refreshAccessToken(): Promise<boolean> {
    if (!this.refreshToken) return false;

    try {
      const response = await fetch(`${this.baseURL}/api/v1/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: this.refreshToken }),
      });

      if (!response.ok) {
        // Refresh token expired, need to login again
        this.accessToken = null;
        this.refreshToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        return false;
      }

      const data = await response.json();
      this.accessToken = data.access;
      localStorage.setItem('access_token', data.access);
      return true;
    } catch (error) {
      return false;
    }
  }

  async getJobs(filters?: {
    category?: string;
    location?: string;
    job_type?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }) {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }

    const response = await this.request(`/jobs/?${params.toString()}`);
    if (!response.ok) throw new Error('Failed to fetch jobs');
    return response.json();
  }

  async getJob(jobId: string) {
    const response = await this.request(`/jobs/${jobId}/`);
    if (!response.ok) throw new Error('Failed to fetch job');
    return response.json();
  }

  async createApplication(jobId: string, coverLetter: string, resume: File) {
    const formData = new FormData();
    formData.append('job', jobId);
    formData.append('cover_letter', coverLetter);
    formData.append('resume', resume);

    const response = await fetch(
      `${this.baseURL}/api/v1/jobs/applications/`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
        },
        body: formData,
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw error;
    }

    return response.json();
  }

  async getCurrentUser() {
    const response = await this.request('/auth/me/');
    if (!response.ok) throw new Error('Failed to fetch user');
    return response.json();
  }

  async getNotifications(filters?: {
    is_read?: boolean;
    page?: number;
  }) {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }

    const response = await this.request(`/core/notifications/?${params.toString()}`);
    if (!response.ok) throw new Error('Failed to fetch notifications');
    return response.json();
  }
}

// Usage
const api = new JobBoardAPI('http://localhost:8000');

// Login
try {
  const loginData = await api.login('johndoe', 'password123');
  console.log('Logged in:', loginData.user);
} catch (error) {
  console.error('Login error:', error);
}

// Get jobs
try {
  const jobs = await api.getJobs({
    category: '123e4567-e89b-12d3-a456-426614174000',
    location: 'New York',
    page: 1,
    page_size: 20,
  });
  console.log('Jobs:', jobs.results);
} catch (error) {
  console.error('Error fetching jobs:', error);
}
```

### React Hook Example

```typescript
// useAuth.ts
import { useState, useEffect } from 'react';
import { JobBoardAPI } from './api';

export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const api = new JobBoardAPI();

  useEffect(() => {
    const loadUser = async () => {
      try {
        const userData = await api.getCurrentUser();
        setUser(userData);
      } catch (error) {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  const login = async (username: string, password: string) => {
    const data = await api.login(username, password);
    setUser(data.user);
    return data;
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  return { user, loading, login, logout };
}

// useJobs.ts
import { useState, useEffect } from 'react';
import { JobBoardAPI } from './api';

export function useJobs(filters?: any) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const api = new JobBoardAPI();

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true);
        const data = await api.getJobs(filters);
        setJobs(data.results);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, [JSON.stringify(filters)]);

  return { jobs, loading, error };
}
```

### Axios Example

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          'http://localhost:8000/api/v1/auth/refresh/',
          { refresh: refreshToken }
        );

        const { access } = response.data;
        localStorage.setItem('access_token', access);
        api.defaults.headers.common['Authorization'] = `Bearer ${access}`;

        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Usage
const jobs = await api.get('/jobs/', {
  params: { category: '123e4567-e89b-12d3-a456-426614174000' },
});
```

---

## Testing

### Test Credentials

After seeding, you can use these test credentials:

**Admin:**
- Username: `admin`
- Password: `admin123`

**Employer:**
- Username: `employer_techcorp_1`
- Password: `employer123`

**Regular User:**
- Username: `user_john_smith_1`
- Password: `user123`

### Postman Collection

You can import the API endpoints into Postman using the Swagger/OpenAPI documentation:

```
GET http://localhost:8000/api/docs/?format=openapi
```

### cURL Examples

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "johndoe", "password": "password123"}'
```

**Get Jobs:**
```bash
curl -X GET "http://localhost:8000/api/v1/jobs/?category=123e4567-e89b-12d3-a456-426614174000&page=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Create Application:**
```bash
curl -X POST http://localhost:8000/api/v1/jobs/applications/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "job=550e8400-e29b-41d4-a716-446655440000" \
  -F "cover_letter=Dear Hiring Manager..." \
  -F "resume=@/path/to/resume.pdf"
```

---

## Best Practices

1. **Token Storage**: Store tokens securely. Consider using httpOnly cookies for production.

2. **Error Handling**: Always handle errors gracefully and show user-friendly messages.

3. **Loading States**: Show loading indicators during API calls.

4. **Pagination**: Implement infinite scroll or pagination controls for list views.

5. **Caching**: Cache frequently accessed data (categories, user profile) to reduce API calls.

6. **Rate Limiting**: Be aware of rate limits and implement exponential backoff for retries.

7. **File Uploads**: Show upload progress and validate file size/type before upload.

8. **Offline Support**: Consider implementing offline support with service workers.

9. **Security**: Never expose access tokens in URLs or logs.

10. **Testing**: Write tests for your API integration code.

---

## Support

For API documentation and interactive testing, visit:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

For issues or questions, contact the development team.

---

## Changelog

### Version 1.0.0 (2026-02-07)
- Initial API release
- UUID-based IDs
- JWT authentication
- Full CRUD operations for jobs and applications
- User profiles and preferences
- Notifications system
- Search functionality
