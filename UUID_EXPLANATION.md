# Why IDs Are Not UUIDs

## Current Implementation

The project currently uses Django's default **auto-incrementing integer primary keys** for all models (User, Job, Application, Category, etc.) instead of UUIDs.

## Why Integer IDs Are Used

### 1. **Django Default Behavior**
- Django's `models.Model` uses `AutoField` (integer) as the default primary key
- This is the standard Django convention and requires no additional configuration
- Most Django projects use integer IDs by default

### 2. **Performance Benefits**
- **Faster database queries**: Integer comparisons are faster than string comparisons
- **Smaller index size**: Integer indexes take less space than UUID indexes
- **Better for foreign keys**: Integer foreign keys are more efficient
- **Database optimization**: Most databases are optimized for integer primary keys

### 3. **Simplicity**
- Easier to work with in URLs: `/api/jobs/123/` vs `/api/jobs/550e8400-e29b-41d4-a716-446655440000/`
- Simpler debugging and testing
- More readable in logs and database dumps

### 4. **Sequential Ordering**
- Integer IDs provide natural ordering (newer records have higher IDs)
- Useful for pagination and chronological sorting
- Can be used as a rough timestamp indicator

## When to Use UUIDs

UUIDs are beneficial when:

1. **Distributed Systems**: Multiple databases or services generating IDs independently
2. **Security**: Hiding record counts and preventing enumeration attacks
3. **Data Merging**: Combining data from multiple sources without ID conflicts
4. **Privacy**: Not exposing sequential information about data volume

## How to Switch to UUIDs (If Needed)

If you want to switch to UUIDs, you would need to:

1. **Update Models**:
```python
import uuid
from django.db import models

class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # ... other fields
```

2. **Create Migrations**: Generate and run migrations to change primary key types

3. **Update Foreign Keys**: All related models would need UUID foreign keys

4. **Update Serializers**: Ensure serializers handle UUIDs correctly

5. **Update URLs**: URL patterns would need to accept UUID format

## Recommendation

For this job board application, **integer IDs are appropriate** because:
- Single database instance
- No distributed system requirements
- Better performance for high-traffic job listings
- Simpler API URLs
- Standard Django practice

If you need UUIDs for security or distributed system reasons, we can implement them, but it requires significant migration work.
