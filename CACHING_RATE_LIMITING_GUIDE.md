# Caching & Rate Limiting System - Implementation Guide

## ✅ Caching & Rate Limiting - Fully Implemented

### Overview

A comprehensive caching and rate limiting system has been implemented for the Job Board Platform, including Redis integration, intelligent cache invalidation, and multi-level rate limiting.

---

## 🗄️ Caching System

### ✅ Redis Integration

**Location**: `config/settings/base.py`, `config/settings/production.py`, `config/settings/development.py`

**Features:**
- **Redis Backend**: Production uses Redis for distributed caching
- **Local Memory Fallback**: Development uses local memory cache if Redis unavailable
- **Connection Pooling**: Optimized connection management in production
- **Compression**: Zlib compression for large cache entries
- **Error Handling**: Graceful degradation if Redis unavailable

**Configuration:**
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'jobboard',
        'TIMEOUT': 300,  # 5 minutes default
    }
}
```

### ✅ Cache Key Naming Strategy

**Location**: `apps/core/cache_utils.py`

**CacheKeyBuilder Class:**
- Consistent key naming: `{prefix}:{type}:{identifier}`
- Hash-based keys for complex queries
- Version support for cache invalidation
- Predefined key builders for common resources

**Key Examples:**
- `jobboard:categories:list`
- `jobboard:jobs:featured:10`
- `jobboard:jobs:detail:123`
- `jobboard:jobs:list:{hash}`

### ✅ Cache Timeouts

**Configurable Timeouts:**
- `CACHE_TIMEOUT_SHORT`: 60 seconds (1 minute)
- `CACHE_TIMEOUT_MEDIUM`: 300 seconds (5 minutes)
- `CACHE_TIMEOUT_LONG`: 3600 seconds (1 hour)
- `CACHE_TIMEOUT_VERY_LONG`: 86400 seconds (24 hours)

### ✅ Caching Implementation

**1. Category List Caching**
- **Location**: `apps/jobs/views.py` - `CategoryViewSet.list()`
- **Cache Key**: `jobboard:categories:list`
- **Timeout**: 1 hour
- **Invalidation**: On create/update/delete

**2. Featured Jobs Caching**
- **Location**: `apps/jobs/views.py` - `JobViewSet.featured()`
- **Cache Key**: `jobboard:jobs:featured:10`
- **Timeout**: 5 minutes
- **Invalidation**: On job create/update/delete

**3. Job List Caching**
- **Location**: `apps/jobs/views.py` - `JobViewSet.list()`
- **Cache Key**: Hash-based from filters
- **Timeout**: 5 minutes
- **Note**: Search queries are not cached (too dynamic)

**4. User Session Caching**
- **Location**: Django sessions (configured via `SESSION_ENGINE`)
- **Backend**: Redis (if configured)
- **Timeout**: Session lifetime

### ✅ Cache Invalidation Strategy

**Automatic Invalidation via Signals:**
- **Location**: `apps/jobs/signals.py`
- **Triggers**:
  - Category create/update/delete → Invalidate category cache
  - Job create/update/delete → Invalidate job cache
  - Featured jobs cache invalidated on any job change

**Manual Invalidation Functions:**
- `invalidate_category_cache(category_id=None)`
- `invalidate_job_cache(job_id=None)`
- `invalidate_user_cache(user_id=None)`
- `invalidate_cache_pattern(pattern)` - Pattern-based invalidation

**Cache Warming:**
- **Function**: `warm_cache()` in `apps/core/cache_utils.py`
- **Purpose**: Pre-populate commonly accessed cache entries
- **Usage**: Can be called on application startup or via management command

---

## 🚦 Rate Limiting System

### ✅ Rate Limiting Middleware

**Location**: `apps/core/middleware_rate_limit.py`

**GlobalRateLimitMiddleware:**
- Applies global rate limits to all API requests
- Different limits for authenticated vs. unauthenticated users
- Skips health checks and static files
- Adds rate limit headers to all responses

**Rate Limits:**
- **Authenticated Users**: 200 requests per minute
- **Unauthenticated Users**: 100 requests per minute

### ✅ Per-Endpoint Rate Limiting

**Location**: `apps/core/rate_limit.py`

**Decorator**: `@rate_limit(limit, period, key_func, scope)`

**Predefined Rate Limits:**
```python
RATE_LIMITS = {
    'login': {'limit': 5, 'period': 300},  # 5 attempts per 5 minutes
    'register': {'limit': 3, 'period': 3600},  # 3 registrations per hour
    'job_create': {'limit': 10, 'period': 3600},  # 10 jobs per hour
    'application_submit': {'limit': 20, 'period': 3600},  # 20 applications per hour
    'search': {'limit': 60, 'period': 60},  # 60 searches per minute
    'api_default': {'limit': 100, 'period': 60},  # 100 requests per minute
    'api_authenticated': {'limit': 200, 'period': 60},  # 200 requests per minute
}
```

### ✅ Specific Rate Limits Implemented

**1. Login Rate Limiting**
- **Location**: `apps/accounts/views.py` - `login_user()`
- **Limit**: 5 attempts per 5 minutes
- **Key**: Based on user ID or IP address
- **Purpose**: Prevent brute force attacks

**2. Registration Rate Limiting**
- **Location**: `apps/accounts/views.py` - `register_user()`
- **Limit**: 3 registrations per hour
- **Key**: Based on IP address
- **Purpose**: Prevent spam registrations

**3. Job Creation Rate Limiting**
- **Location**: `apps/jobs/views.py` - `JobViewSet.create()`
- **Limit**: 10 jobs per hour
- **Key**: Based on user ID
- **Purpose**: Prevent job spam

**4. Application Submission Rate Limiting**
- **Location**: `apps/jobs/views.py` - `ApplicationViewSet.create()`
- **Limit**: 20 applications per hour
- **Key**: Based on user ID
- **Purpose**: Prevent application spam

**5. Search Rate Limiting**
- **Location**: `apps/jobs/views.py` - `JobViewSet.list()`
- **Limit**: 60 searches per minute
- **Key**: Based on user ID or IP
- **Purpose**: Prevent search abuse

### ✅ Rate Limit Headers

**Response Headers:**
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current period
- `X-RateLimit-Reset`: Unix timestamp when limit resets
- `Retry-After`: Seconds to wait before retrying (when exceeded)

### ✅ Rate Limit Error Handling

**429 Too Many Requests Response:**
```json
{
    "error": "Rate limit exceeded",
    "detail": "You have exceeded the rate limit of X requests per Y seconds.",
    "retry_after": 60
}
```

**Headers Included:**
- All standard rate limit headers
- `Retry-After` header for client guidance

---

## 🔧 Configuration

### Environment Variables

Add to `.env` file:

```env
# Cache Configuration
CACHE_BACKEND=django_redis.cache.RedisCache
CACHE_LOCATION=redis://127.0.0.1:6379/1
CACHE_KEY_PREFIX=jobboard
CACHE_TIMEOUT=300

# Redis Configuration (if using Redis)
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=1
```

### Docker Compose (Redis Service)

Add to `docker-compose.yml`:

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

---

## 📊 Usage Examples

### Cache Operations

```python
from apps.core.cache_utils import CacheKeyBuilder, cache
from django.core.cache import cache

# Get cached data
cache_key = CacheKeyBuilder.category_list()
categories = cache.get(cache_key)

# Set cache
cache.set(cache_key, data, timeout=3600)

# Invalidate cache
from apps.core.cache_utils import invalidate_category_cache
invalidate_category_cache()
```

### Rate Limiting

```python
from apps.core.rate_limit import rate_limit, RATE_LIMITS

@rate_limit(
    limit=RATE_LIMITS['custom']['limit'],
    period=RATE_LIMITS['custom']['period'],
    scope='custom'
)
def my_view(request):
    # View logic
    pass
```

### Check Rate Limit Status

```python
from apps.core.rate_limit import check_rate_limit

is_allowed, rate_info = check_rate_limit('key', 100, 60)
print(f"Remaining: {rate_info['remaining']}")
```

---

## 🎯 Best Practices

### ✅ Caching Best Practices

1. **Cache Frequently Accessed Data**: Categories, featured jobs
2. **Don't Cache Dynamic Data**: Search results with queries
3. **Use Appropriate Timeouts**: Short for dynamic, long for static
4. **Invalidate on Updates**: Always invalidate related cache on model changes
5. **Monitor Cache Hit Rates**: Track cache performance

### ✅ Rate Limiting Best Practices

1. **Different Limits for Different Users**: Authenticated users get higher limits
2. **Protect Sensitive Endpoints**: Login, registration have stricter limits
3. **Provide Clear Error Messages**: Help users understand limits
4. **Include Rate Limit Headers**: Help clients implement backoff
5. **Log Rate Limit Violations**: Monitor for abuse patterns

---

## 🔍 Monitoring

### Cache Metrics

- **Hit Rate**: Percentage of cache hits vs. misses
- **Cache Size**: Memory usage in Redis
- **Eviction Rate**: How often cache entries are evicted

### Rate Limit Metrics

- **Rate Limit Violations**: Number of 429 responses
- **Per-Endpoint Violations**: Which endpoints are most limited
- **User Violations**: Users hitting rate limits frequently

---

## ✅ Implementation Status

### Fully Implemented ✅

- ✅ Redis integration and configuration
- ✅ Cache key naming strategy
- ✅ Category list caching
- ✅ Featured jobs caching
- ✅ Job list caching (filtered)
- ✅ Cache invalidation via signals
- ✅ Cache warming function
- ✅ Global rate limiting middleware
- ✅ Per-endpoint rate limiting
- ✅ Login rate limiting
- ✅ Registration rate limiting
- ✅ Job creation rate limiting
- ✅ Application submission rate limiting
- ✅ Search rate limiting
- ✅ Rate limit headers
- ✅ Rate limit error handling

### Ready for Production ✅

- ✅ Production-ready caching with Redis
- ✅ Comprehensive rate limiting
- ✅ Automatic cache invalidation
- ✅ Graceful degradation if Redis unavailable

---

## 🚀 Performance Impact

### Caching Benefits

- **Reduced Database Load**: Frequently accessed data served from cache
- **Faster Response Times**: Cache hits are significantly faster
- **Better Scalability**: Redis can handle high concurrent requests

### Rate Limiting Benefits

- **DoS Protection**: Prevents abuse and DoS attacks
- **Fair Resource Usage**: Ensures fair access for all users
- **API Stability**: Prevents single users from overwhelming the system

---

**Status**: ✅ **COMPLETE** - Comprehensive caching and rate limiting system fully implemented and ready for production use!
