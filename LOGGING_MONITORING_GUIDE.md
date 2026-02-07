# Logging & Monitoring System - Implementation Guide

## ✅ Logging & Monitoring - Fully Implemented

### Overview

A comprehensive logging and monitoring system has been implemented for the Job Board Platform, including structured logging, performance monitoring, health checks, analytics, and error tracking integration.

---

## 📊 Application Logging

### ✅ Structured Logging Configuration

**Location**: `config/settings/base.py`

**Features:**
- **Multiple Formatters**:
  - `verbose`: Detailed format with timestamp, module, process, thread
  - `simple`: Basic format
  - `json`: JSON format for structured logging
  - `django.server`: Django server format

- **Log Rotation**:
  - Rotating file handlers (10MB max, 5 backups)
  - Separate log files for different purposes:
    - `django.log`: General application logs
    - `errors.log`: Error-level logs only
    - `api.log`: API request/response logs (JSON format)
    - `performance.log`: Performance metrics (JSON format)

- **Log Levels per Environment**:
  - Configurable via `LOG_LEVEL` environment variable
  - Default: INFO
  - Database queries: Configurable via `DB_LOG_LEVEL` (default: WARNING)

### ✅ Log Handlers

1. **Console Handler**: Outputs to console (all environments)
2. **File Handler**: Rotating file handler for general logs
3. **Error File Handler**: Separate file for errors only
4. **API File Handler**: JSON-formatted API logs
5. **Performance File Handler**: JSON-formatted performance logs

### ✅ Logger Configuration

**Loggers:**
- `django`: Django framework logs
- `django.server`: Django development server logs
- `django.db.backends`: Database query logs
- `django.request`: Request error logs
- `apps`: Application-specific logs
- `apps.api`: API request/response logs
- `apps.performance`: Performance monitoring logs

---

## 🔍 Monitoring & Analytics

### ✅ Analytics Service (`apps/core/analytics.py`)

**Features:**
- User statistics (total, active, by role, recent registrations)
- Job statistics (total, active, by status/type, views, featured)
- Application statistics (total, by status, recent, top jobs)
- Category statistics (total, with jobs, top categories)
- User activity tracking (employer/user specific)

**Methods:**
- `get_user_statistics()` - User metrics
- `get_job_statistics()` - Job metrics
- `get_application_statistics()` - Application metrics
- `get_category_statistics()` - Category metrics
- `get_overall_statistics()` - Comprehensive statistics
- `get_user_activity()` - Individual user activity

### ✅ Analytics Endpoints

**Admin Only Endpoints:**
- `GET /health/statistics/` - Overall platform statistics
- `GET /health/statistics/users/` - User statistics
- `GET /health/statistics/jobs/` - Job statistics
- `GET /health/statistics/applications/` - Application statistics
- `GET /health/statistics/user-activity/?user_id=X&days=30` - User activity

---

## 🏥 Health Checks

### ✅ Health Check Endpoints

**Location**: `apps/core/health.py` and `apps/core/views.py`

**Endpoints:**
1. **`GET /health/`** - Comprehensive health check
   - Checks: Database, Cache, Disk, Memory
   - Returns: 200 if healthy, 503 if unhealthy
   - Public access

2. **`GET /health/liveness/`** - Liveness check
   - Simple check if application is running
   - Returns: 200 if alive
   - Public access

3. **`GET /health/readiness/`** - Readiness check
   - Checks if application is ready to serve traffic
   - Validates database connectivity
   - Returns: 200 if ready, 503 if not ready
   - Public access

### ✅ Health Check Components

**Database Check:**
- Tests database connectivity
- Measures response time
- Returns status and response time

**Cache Check:**
- Tests cache read/write operations
- Measures response time
- Returns status and response time

**Disk Space Check:**
- Monitors disk usage (requires psutil)
- Warns at 90% usage
- Critical at 95% usage
- Returns: total, used, free, percent used

**Memory Check:**
- Monitors system memory (requires psutil)
- Warns at 85% usage
- Critical at 95% usage
- Returns: total, used, available, percent used

---

## 🔧 Middleware

### ✅ API Logging Middleware (`apps/core/middleware.py`)

**APILoggingMiddleware:**
- Logs all API requests and responses
- Tracks: method, path, query params, status code, duration, user, IP
- JSON format for structured logging
- Different log levels based on status code (error/warning/info)
- Skips health checks and static files

**PerformanceMonitoringMiddleware:**
- Tracks request duration
- Monitors database query count and time
- Identifies slow requests (> 1 second)
- Logs performance metrics in JSON format

**DatabaseQueryLoggingMiddleware:**
- Logs database queries when DEBUG=True or DB_LOG_LEVEL=DEBUG
- Tracks query count and total query time
- Useful for debugging N+1 query problems

---

## 🚨 Error Tracking

### ✅ Sentry Integration

**Location**: `config/settings/production.py`

**Features:**
- Automatic error tracking
- Performance monitoring
- User context tracking
- Environment and release tracking
- Configurable sample rate

**Configuration:**
```python
SENTRY_DSN = config('SENTRY_DSN', default='')
SENTRY_TRACES_SAMPLE_RATE = config('SENTRY_TRACES_SAMPLE_RATE', default=0.1, cast=float)
ENVIRONMENT = config('ENVIRONMENT', default='production')
RELEASE_VERSION = config('RELEASE_VERSION', default='1.0.0')
```

**Integrations:**
- Django Integration (transactions, middleware spans, signals)
- Logging Integration (breadcrumbs and events)

---

## 📈 Performance Logging

### ✅ Performance Metrics Tracked

- **Request Duration**: Total time to process request
- **Database Query Count**: Number of queries per request
- **Database Query Time**: Total time spent on queries
- **Slow Request Detection**: Flags requests > 1 second

### ✅ Performance Log Format

```json
{
  "path": "/api/jobs/",
  "method": "GET",
  "duration_ms": 245.67,
  "query_count": 3,
  "query_time_ms": 12.34,
  "slow_request": false
}
```

---

## 🔐 Security Considerations

### ✅ Logging Security

- **Sensitive Data**: Passwords and tokens are never logged
- **User Information**: Only logged for authenticated requests
- **IP Addresses**: Logged for security monitoring
- **Error Details**: Full error context for debugging (production-safe)

---

## 📋 Environment Configuration

### Development

- Console logging enabled
- File logging enabled
- Debug-level logging for apps
- Database query logging (if DEBUG=True)

### Production

- Console logging (for container logs)
- File logging with rotation
- Error tracking via Sentry
- Performance monitoring enabled
- Structured JSON logging

### Testing

- Logging disabled (`LOGGING_CONFIG = None`)
- Fast test execution

---

## 🚀 Usage Examples

### Check Application Health

```bash
# Comprehensive health check
curl http://localhost:8000/health/

# Liveness check
curl http://localhost:8000/health/liveness/

# Readiness check
curl http://localhost:8000/health/readiness/
```

### Get Statistics (Admin Only)

```bash
# Overall statistics
curl -H "Authorization: Bearer {token}" http://localhost:8000/health/statistics/

# User statistics
curl -H "Authorization: Bearer {token}" http://localhost:8000/health/statistics/users/

# Job statistics
curl -H "Authorization: Bearer {token}" http://localhost:8000/health/statistics/jobs/
```

### View Logs

```bash
# General logs
tail -f logs/django.log

# Error logs
tail -f logs/errors.log

# API logs (JSON format)
tail -f logs/api.log

# Performance logs (JSON format)
tail -f logs/performance.log
```

---

## ⚙️ Configuration

### Environment Variables

Add to `.env` file:

```env
# Logging
LOG_LEVEL=INFO
DB_LOG_LEVEL=WARNING

# Sentry (Optional)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_TRACES_SAMPLE_RATE=0.1
ENVIRONMENT=production
RELEASE_VERSION=1.0.0
```

---

## 📊 Log File Locations

All log files are stored in `logs/` directory:

- `logs/django.log` - General application logs
- `logs/errors.log` - Error-level logs
- `logs/api.log` - API request/response logs (JSON)
- `logs/performance.log` - Performance metrics (JSON)

**Log Rotation:**
- Maximum file size: 10MB
- Backup count: 5 files
- Automatic rotation when size limit reached

---

## 🔍 Monitoring Best Practices

### ✅ Implemented Practices

1. **Structured Logging**: JSON format for easy parsing
2. **Log Rotation**: Prevents disk space issues
3. **Separate Log Files**: Organized by purpose
4. **Performance Tracking**: Identifies slow requests
5. **Error Tracking**: Sentry integration for production
6. **Health Checks**: Kubernetes/Docker ready
7. **Analytics**: Comprehensive statistics for admins

---

## 🎯 Health Check Response Examples

### Healthy Response (200)

```json
{
  "status": "healthy",
  "timestamp": 1704067200.0,
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 2.45
    },
    "cache": {
      "status": "healthy",
      "response_time_ms": 1.23
    },
    "disk": {
      "status": "healthy",
      "total_gb": 100.0,
      "used_gb": 45.2,
      "free_gb": 54.8,
      "percent_used": 45.2
    },
    "memory": {
      "status": "healthy",
      "total_gb": 8.0,
      "used_gb": 4.5,
      "available_gb": 3.5,
      "percent_used": 56.25
    }
  }
}
```

### Unhealthy Response (503)

```json
{
  "status": "unhealthy",
  "timestamp": 1704067200.0,
  "checks": {
    "database": {
      "status": "unhealthy",
      "error": "Connection refused"
    }
  }
}
```

---

## 📈 Analytics Response Example

```json
{
  "users": {
    "total_users": 150,
    "active_users": 145,
    "inactive_users": 5,
    "users_by_role": {
      "user": 100,
      "employer": 40,
      "admin": 10
    },
    "recent_registrations_30d": 25
  },
  "jobs": {
    "total_jobs": 500,
    "active_jobs": 350,
    "jobs_by_status": {
      "active": 350,
      "draft": 100,
      "closed": 50
    },
    "total_views": 15000,
    "average_views_per_job": 30.0
  },
  "applications": {
    "total_applications": 1200,
    "applications_by_status": {
      "pending": 400,
      "reviewed": 300,
      "accepted": 300,
      "rejected": 200
    }
  }
}
```

---

## ✅ Implementation Status

### Fully Implemented ✅

- ✅ Structured logging configuration
- ✅ Log rotation (10MB, 5 backups)
- ✅ Multiple log files (django, errors, api, performance)
- ✅ Log levels per environment
- ✅ API request/response logging
- ✅ Performance monitoring middleware
- ✅ Database query monitoring
- ✅ Health check endpoints
- ✅ Analytics service
- ✅ Statistics endpoints
- ✅ Sentry error tracking integration
- ✅ System resource monitoring (disk, memory)

### Ready for Production ✅

- ✅ Production-ready logging
- ✅ Error tracking configured
- ✅ Health checks for orchestration
- ✅ Performance monitoring
- ✅ Analytics dashboard data

---

## 🔮 Future Enhancements (Optional)

### Advanced Monitoring
- APM integration (New Relic, Datadog)
- Custom metrics dashboard
- Real-time alerting
- Log aggregation (ELK stack)

### Enhanced Analytics
- Time-series analytics
- User behavior tracking
- Conversion funnel analysis
- A/B testing support

---

**Status**: ✅ **COMPLETE** - Comprehensive logging and monitoring system fully implemented and ready for production use!
