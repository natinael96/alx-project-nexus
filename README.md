# Job Board Platform - Backend API

[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A robust, production-ready backend API for a Job Board Platform built with Django and PostgreSQL. This system provides comprehensive job posting management, role-based access control, optimized search capabilities, and complete API documentation.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Authentication & Authorization](#authentication--authorization)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Performance Optimization](#performance-optimization)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## 🎯 Overview

This backend system powers a Job Board Platform that enables:
- **Job Seekers** to search, view, and apply for job postings
- **Employers** to post, manage, and track job listings
- **Administrators** to oversee the platform, manage categories, and moderate content

The system is designed with scalability, security, and performance in mind, implementing best practices for Django development, database optimization, and API design.

### Real-World Application

This project prepares developers to build robust backend systems for platforms requiring:
- **Role-based access control** and secure authentication
- **Efficient database schemas** for complex data relationships
- **Optimized query performance** for large datasets
- **RESTful API design** following industry standards
- **Comprehensive API documentation** for frontend integration

## ✨ Features

### Core Functionality

#### Job Posting Management
- ✅ **CRUD Operations**: Create, Read, Update, and Delete job postings
- ✅ **Job Categorization**: Organize jobs by industry, location, and job type
- ✅ **Rich Job Details**: Support for job descriptions, requirements, salary ranges, and benefits
- ✅ **Status Management**: Track job posting status (active, closed, draft)
- ✅ **Application Tracking**: Monitor and manage job applications

#### Role-Based Access Control (RBAC)
- ✅ **Admin Role**: Full system access for managing jobs, categories, and users
- ✅ **Employer Role**: Post and manage their own job listings
- ✅ **User Role**: Search jobs and submit applications
- ✅ **JWT Authentication**: Secure token-based authentication
- ✅ **Permission System**: Granular permissions for different operations

#### Optimized Job Search
- ✅ **Advanced Filtering**: Filter by category, location, job type, salary range
- ✅ **Full-Text Search**: Search job titles and descriptions
- ✅ **Database Indexing**: Optimized queries with strategic indexes
- ✅ **Pagination**: Efficient handling of large result sets
- ✅ **Sorting Options**: Sort by date, salary, relevance

#### API Documentation
- ✅ **Swagger/OpenAPI**: Interactive API documentation
- ✅ **Endpoint Details**: Complete request/response schemas
- ✅ **Authentication Guide**: Clear authentication flow documentation
- ✅ **Code Examples**: Sample requests and responses

### Additional Features

- **Application Management**: Users can track their job applications
- **Category Management**: Hierarchical category system for job organization
- **Location Support**: Geographic filtering and location-based search
- **Audit Logging**: Track changes to job postings and applications
- **Data Validation**: Comprehensive input validation and error handling
- **Rate Limiting**: API rate limiting to prevent abuse
- **CORS Configuration**: Cross-origin resource sharing for frontend integration

## 🛠 Technology Stack

### Backend Framework
- **Django 4.2+**: High-level Python web framework
  - Django REST Framework for API development
  - Django ORM for database operations
  - Django Admin for content management

### Database
- **PostgreSQL 14+**: Advanced relational database
  - Support for complex queries and transactions
  - Full-text search capabilities
  - JSON field support for flexible data storage

### Authentication & Security
- **JWT (JSON Web Tokens)**: Secure token-based authentication
  - `djangorestframework-simplejwt` for JWT implementation
  - Token refresh mechanism
  - Secure token storage

### API Documentation
- **Swagger/OpenAPI**: Interactive API documentation
  - `drf-yasg` or `drf-spectacular` for Swagger integration
  - Auto-generated API schemas
  - Interactive API testing interface

### Additional Libraries
- **Python 3.9+**: Programming language
- **psycopg2**: PostgreSQL adapter for Python
- **python-decouple**: Environment variable management
- **django-cors-headers**: CORS handling
- **Pillow**: Image processing (if needed for company logos)

## 📁 Project Structure

```
alx-project-nexus/
│
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # Project documentation
│
├── config/                   # Project configuration
│   ├── __init__.py
│   ├── settings/             # Settings modules
│   │   ├── __init__.py
│   │   ├── base.py           # Base settings
│   │   ├── development.py    # Development settings
│   │   ├── production.py     # Production settings
│   │   └── testing.py        # Testing settings
│   ├── urls.py               # Main URL configuration
│   └── wsgi.py               # WSGI configuration
│
├── apps/                     # Django applications
│   ├── __init__.py
│   │
│   ├── accounts/             # User authentication & management
│   │   ├── __init__.py
│   │   ├── models.py         # User models
│   │   ├── views.py          # Authentication views
│   │   ├── serializers.py    # User serializers
│   │   ├── urls.py           # Account URLs
│   │   ├── permissions.py    # Custom permissions
│   │   └── admin.py          # Admin configuration
│   │
│   ├── jobs/                 # Job posting management
│   │   ├── __init__.py
│   │   ├── models.py         # Job, Category, Application models
│   │   ├── views.py          # Job CRUD views
│   │   ├── serializers.py    # Job serializers
│   │   ├── urls.py           # Job URLs
│   │   ├── filters.py        # Job filtering logic
│   │   ├── permissions.py    # Job permissions
│   │   └── admin.py          # Job admin
│   │
│   └── core/                 # Core utilities
│       ├── __init__.py
│       ├── utils.py          # Utility functions
│       └── pagination.py     # Custom pagination
│
├── static/                   # Static files
├── media/                    # User uploaded files
│
└── tests/                    # Test suite
    ├── __init__.py
    ├── test_accounts.py
    ├── test_jobs.py
    └── test_integration.py
```

## 📦 Prerequisites

Before you begin, ensure you have the following installed on your system:

### Required Software

1. **Python 3.9 or higher**
   ```bash
   python --version  # Should be 3.9+
   ```

2. **PostgreSQL 14 or higher**
   ```bash
   psql --version  # Should be 14+
   ```

3. **pip** (Python package manager)
   ```bash
   pip --version
   ```

4. **Git** (for version control)
   ```bash
   git --version
   ```

### Optional but Recommended

- **Virtual Environment**: `venv` or `virtualenv`
- **PostgreSQL Client Tools**: `pgAdmin` or `psql` command-line tool
- **API Testing Tool**: Postman, Insomnia, or Thunder Client
- **Code Editor**: VS Code, PyCharm, or your preferred IDE

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd alx-project-nexus
```

### Step 2: Create Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Set Up PostgreSQL Database

1. **Create PostgreSQL Database:**
   ```bash
   # Connect to PostgreSQL
   psql -U postgres
   
   # Create database
   CREATE DATABASE jobboard_db;
   
   # Create user (optional)
   CREATE USER jobboard_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE jobboard_db TO jobboard_user;
   \q
   ```

2. **Verify Database Connection:**
   ```bash
   psql -U jobboard_user -d jobboard_db -h localhost
   ```

### Step 5: Configure Environment Variables

1. **Copy Environment Template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file with your configuration:**
   ```env
   # Django Settings
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database Configuration
   DB_NAME=jobboard_db
   DB_USER=jobboard_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432

   # JWT Settings
   JWT_SECRET_KEY=your-jwt-secret-key
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_LIFETIME=60  # minutes
   REFRESH_TOKEN_LIFETIME=1440  # minutes (24 hours)

   # CORS Settings
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

   # Email Configuration (Optional)
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

### Step 6: Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user:
- Username
- Email address
- Password

### Step 8: Load Initial Data (Optional)

```bash
python manage.py loaddata initial_data.json  # If available
```

### Step 9: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

## ⚙️ Configuration

### Django Settings

The project uses environment-based settings. Key configuration files:

#### Base Settings (`config/settings/base.py`)
- Core Django configuration
- Installed apps
- Middleware configuration
- Database settings
- Authentication backends

#### Development Settings (`config/settings/development.py`)
- Debug mode enabled
- Detailed error pages
- Development-specific middleware
- Local database configuration

#### Production Settings (`config/settings/production.py`)
- Debug mode disabled
- Security middleware enabled
- Production database configuration
- Static file serving configuration
- HTTPS enforcement

### Database Configuration

The database connection is configured via environment variables:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

### JWT Configuration

JWT settings are configured in `config/settings/base.py`:

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

## 🗄️ Database Setup

### Database Schema Overview

The system uses the following main models:

#### User Model (Custom)
- Extends Django's AbstractUser
- Role field (admin, employer, user)
- Profile information
- Timestamps

#### Job Model
- Title, description, requirements
- Category (ForeignKey)
- Location
- Job type (full-time, part-time, contract)
- Salary range
- Status (active, closed, draft)
- Employer (ForeignKey to User)
- Created/updated timestamps

#### Category Model
- Name, description
- Parent category (for hierarchy)
- Slug (for URLs)

#### Application Model
- Job (ForeignKey)
- Applicant (ForeignKey to User)
- Cover letter
- Resume (FileField)
- Status (pending, reviewed, accepted, rejected)
- Applied date

### Creating Database Indexes

The system includes optimized indexes for performance:

```python
class Job(models.Model):
    # ... fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['category', 'location']),
            models.Index(fields=['job_type', 'status']),
            GinIndex(fields=['title', 'description']),  # For full-text search
        ]
```

### Running Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

## 🏃 Running the Application

### Development Server

```bash
# Run development server
python manage.py runserver

# Run on specific port
python manage.py runserver 8000

# Run on all interfaces
python manage.py runserver 0.0.0.0:8000
```

The API will be available at:
- **API Base URL**: `http://localhost:8000/api/`
- **Admin Panel**: `http://localhost:8000/admin/`
- **Swagger Documentation**: `http://localhost:8000/api/docs/`

### Running with Docker (Optional)

If Docker is configured:

```bash
# Build containers
docker-compose build

# Start services
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📚 API Documentation

### Swagger Documentation

The API documentation is available at `/api/docs/` when the server is running.

#### Accessing Swagger UI

1. Start the development server
2. Navigate to `http://localhost:8000/api/docs/`
3. Explore available endpoints
4. Test endpoints directly from the browser

#### Swagger Features

- **Interactive API Testing**: Test endpoints directly from the documentation
- **Request/Response Schemas**: View detailed data structures
- **Authentication**: Authenticate and test protected endpoints
- **Code Examples**: Generate code snippets for different languages

### API Endpoints Overview

#### Authentication Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login (get JWT tokens)
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/me/` - Get current user profile

#### Job Endpoints
- `GET /api/jobs/` - List all jobs (with filtering)
- `POST /api/jobs/` - Create new job (employer/admin only)
- `GET /api/jobs/{id}/` - Get job details
- `PUT /api/jobs/{id}/` - Update job (owner/admin only)
- `PATCH /api/jobs/{id}/` - Partial update job
- `DELETE /api/jobs/{id}/` - Delete job (owner/admin only)

#### Category Endpoints
- `GET /api/categories/` - List all categories
- `POST /api/categories/` - Create category (admin only)
- `GET /api/categories/{id}/` - Get category details
- `PUT /api/categories/{id}/` - Update category (admin only)
- `DELETE /api/categories/{id}/` - Delete category (admin only)

#### Application Endpoints
- `GET /api/applications/` - List user's applications
- `POST /api/applications/` - Submit job application
- `GET /api/applications/{id}/` - Get application details
- `PATCH /api/applications/{id}/` - Update application status (employer/admin)

## 🔐 Authentication & Authorization

### Authentication Flow

#### 1. User Registration

```bash
POST /api/auth/register/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123",
  "password2": "secure_password123",
  "role": "user",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "user"
  },
  "message": "User registered successfully"
}
```

#### 2. User Login

```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "user"
  }
}
```

#### 3. Using Access Token

Include the token in the Authorization header:

```bash
GET /api/jobs/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

#### 4. Refreshing Token

```bash
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Role-Based Permissions

#### Admin Permissions
- Full access to all endpoints
- Create, update, delete any job
- Manage categories
- View all applications
- Manage users

#### Employer Permissions
- Create, update, delete own jobs
- View applications for own jobs
- Update application status for own jobs
- View own profile

#### User Permissions
- View all active jobs
- Apply for jobs
- View own applications
- Update own profile

### Permission Examples

```python
# Admin only
@permission_classes([IsAdminUser])
def create_category(request):
    ...

# Employer or Admin
@permission_classes([IsEmployerOrAdmin])
def create_job(request):
    ...

# Authenticated users
@permission_classes([IsAuthenticated])
def apply_for_job(request):
    ...
```

## 🔌 API Endpoints

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string",
  "password2": "string",
  "role": "user|employer|admin",
  "first_name": "string",
  "last_name": "string"
}
```

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

#### Get Current User
```http
GET /api/auth/me/
Authorization: Bearer {token}
```

### Job Endpoints

#### List Jobs (with filtering)
```http
GET /api/jobs/?category=1&location=New+York&job_type=full-time&min_salary=50000&search=developer
Authorization: Bearer {token}  # Optional
```

**Query Parameters:**
- `category`: Filter by category ID
- `location`: Filter by location
- `job_type`: Filter by job type (full-time, part-time, contract)
- `min_salary`: Minimum salary
- `max_salary`: Maximum salary
- `search`: Search in title and description
- `status`: Filter by status (active, closed, draft)
- `page`: Page number for pagination
- `page_size`: Items per page

**Response:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/jobs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Senior Python Developer",
      "description": "We are looking for...",
      "requirements": "5+ years experience...",
      "category": {
        "id": 1,
        "name": "Software Development"
      },
      "location": "New York, NY",
      "job_type": "full-time",
      "salary_min": 80000,
      "salary_max": 120000,
      "status": "active",
      "employer": {
        "id": 2,
        "username": "tech_company"
      },
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Create Job
```http
POST /api/jobs/
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Senior Python Developer",
  "description": "We are looking for an experienced Python developer...",
  "requirements": "5+ years of Python experience, Django knowledge...",
  "category": 1,
  "location": "New York, NY",
  "job_type": "full-time",
  "salary_min": 80000,
  "salary_max": 120000
}
```

#### Get Job Details
```http
GET /api/jobs/{id}/
Authorization: Bearer {token}  # Optional
```

#### Update Job
```http
PUT /api/jobs/{id}/
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Updated Job Title",
  "description": "Updated description...",
  ...
}
```

#### Delete Job
```http
DELETE /api/jobs/{id}/
Authorization: Bearer {token}
```

### Category Endpoints

#### List Categories
```http
GET /api/categories/
```

#### Create Category (Admin Only)
```http
POST /api/categories/
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "name": "Software Development",
  "description": "Jobs related to software development",
  "parent": null
}
```

### Application Endpoints

#### Submit Application
```http
POST /api/applications/
Authorization: Bearer {token}
Content-Type: multipart/form-data

{
  "job": 1,
  "cover_letter": "I am interested in this position...",
  "resume": <file>
}
```

#### List User Applications
```http
GET /api/applications/
Authorization: Bearer {token}
```

#### Get Application Details
```http
GET /api/applications/{id}/
Authorization: Bearer {token}
```

## 🗃️ Database Schema

### Entity Relationship Diagram

```
┌─────────────┐
│    User     │
│─────────────│
│ id (PK)     │
│ username    │
│ email       │
│ role        │
│ password    │
│ created_at  │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────▼──────┐      ┌──────────────┐
│    Job      │      │  Application │
│─────────────│      │──────────────│
│ id (PK)     │◄─────┤ id (PK)      │
│ title       │ 1:N  │ job (FK)     │
│ description │      │ applicant(FK)│
│ category(FK)│      │ cover_letter │
│ employer(FK)│      │ resume       │
│ location    │      │ status       │
│ job_type    │      │ applied_at   │
│ salary_min  │      └──────────────┘
│ salary_max  │
│ status      │
│ created_at  │
└──────┬──────┘
       │
       │ N:1
       │
┌──────▼──────┐
│  Category   │
│─────────────│
│ id (PK)     │
│ name        │
│ description │
│ parent (FK) │
│ slug        │
└─────────────┘
```

### Model Definitions

#### User Model
```python
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('employer', 'Employer'),
        ('user', 'User'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Job Model
```python
class Job(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
    
    JOB_TYPE_CHOICES = [
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Category Model
```python
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Application Model
```python
class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
```

## ⚡ Performance Optimization

### Database Indexing

Strategic indexes are created for frequently queried fields:

```python
class Job(models.Model):
    # ... fields ...
    
    class Meta:
        indexes = [
            # Composite index for status and date filtering
            models.Index(fields=['status', '-created_at']),
            
            # Index for category and location filtering
            models.Index(fields=['category', 'location']),
            
            # Index for job type and status
            models.Index(fields=['job_type', 'status']),
            
            # Full-text search index (PostgreSQL specific)
            GinIndex(fields=['title', 'description']),
            
            # Salary range queries
            models.Index(fields=['salary_min', 'salary_max']),
        ]
```

### Query Optimization

#### Select Related & Prefetch Related
```python
# Optimize foreign key queries
jobs = Job.objects.select_related('category', 'employer').prefetch_related('applications')

# Optimize reverse foreign key queries
applications = Application.objects.select_related('job', 'applicant')
```

#### Query Filtering
```python
# Efficient filtering with indexes
jobs = Job.objects.filter(
    status='active',
    category_id=category_id,
    location__icontains=location
).select_related('category', 'employer')
```

#### Pagination
```python
# Limit query results
from rest_framework.pagination import PageNumberPagination

class JobPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
```

### Caching Strategy

```python
# Cache frequently accessed data
from django.core.cache import cache

def get_categories():
    categories = cache.get('categories')
    if categories is None:
        categories = Category.objects.all()
        cache.set('categories', categories, 3600)  # Cache for 1 hour
    return categories
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.jobs

# Run specific test file
python manage.py test apps.jobs.tests.test_views

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Structure

```python
# Example test
from django.test import TestCase
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.jobs.models import Job

class JobAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='employer'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_job(self):
        response = self.client.post('/api/jobs/', {
            'title': 'Test Job',
            'description': 'Test Description',
            # ... other fields
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Job.objects.count(), 1)
```

### Test Coverage Goals

- Unit tests for models: >90%
- API endpoint tests: >85%
- Integration tests: Critical paths covered
- Authentication tests: 100%

## 🚢 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in production settings
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set secure `SECRET_KEY` in environment variables
- [ ] Configure PostgreSQL database
- [ ] Set up static file serving (WhiteNoise or CDN)
- [ ] Configure media file storage (AWS S3 recommended)
- [ ] Set up SSL/HTTPS
- [ ] Configure CORS for frontend domain
- [ ] Set up error logging and monitoring
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

### Deployment Options

#### Heroku

```bash
# Install Heroku CLI
# Create Procfile
echo "web: gunicorn config.wsgi --log-file -" > Procfile

# Deploy
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

#### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init

# Create environment
eb create production

# Deploy
eb deploy
```

#### Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000"]
```

### Environment Variables for Production

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_NAME=production_db
DB_USER=production_user
DB_PASSWORD=secure_password
DB_HOST=your-db-host
DB_PORT=5432

CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 🤝 Contributing

### Contribution Guidelines

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Follow coding standards**
   - Use PEP 8 style guide
   - Write docstrings for functions and classes
   - Follow Django best practices

4. **Write tests**
   - Add tests for new features
   - Ensure all tests pass

5. **Commit changes**
   ```bash
   git commit -m "feat: add new feature"
   ```

6. **Push to branch**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**

### Commit Message Convention

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks
- `perf:` Performance improvements

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Error

**Problem:** Cannot connect to PostgreSQL

**Solution:**
```bash
# Check PostgreSQL is running
sudo service postgresql status  # Linux
brew services list  # macOS

# Verify connection settings in .env
# Test connection
psql -U your_user -d your_database -h localhost
```

#### Migration Errors

**Problem:** Migration conflicts or errors

**Solution:**
```bash
# Reset migrations (development only)
python manage.py migrate --fake-initial

# Show migration status
python manage.py showmigrations

# Rollback specific migration
python manage.py migrate app_name migration_number
```

#### JWT Token Issues

**Problem:** Token expired or invalid

**Solution:**
- Check token expiration time in settings
- Use refresh token to get new access token
- Verify JWT_SECRET_KEY matches in settings

#### CORS Errors

**Problem:** CORS policy blocking requests

**Solution:**
```python
# In settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://yourdomain.com",
]
```

#### Static Files Not Loading

**Problem:** Static files return 404

**Solution:**
```bash
# Collect static files
python manage.py collectstatic

# Check STATIC_URL and STATIC_ROOT in settings
# Verify static files configuration in production
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- **Email:** support@jobboard.com
- **Issues:** [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation:** [Full Documentation](https://docs.jobboard.com)

## 🙏 Acknowledgments

- Django REST Framework team
- PostgreSQL community
- All contributors to this project

---

**Built with ❤️ for the ALX Project Nexus**

