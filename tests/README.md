# Testing Suite Documentation

## Overview

This directory contains comprehensive tests for the Job Board Platform backend. The test suite includes unit tests, integration tests, and model validation tests.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures and configuration
├── factories.py         # Factory classes for test data
├── test_accounts.py     # Account app tests
├── test_jobs.py         # Jobs app tests
├── test_models.py       # Model validation tests
└── test_integration.py  # Integration tests
```

## Running Tests

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_accounts.py
```

### Run with Coverage

```bash
pytest --cov=apps --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`

### Run Specific Test

```bash
pytest tests/test_accounts.py::TestUserRegistration::test_register_user_success
```

## Test Categories

### 1. Unit Tests

#### Account Tests (`test_accounts.py`)
- User registration (success, validation, duplicates)
- Login/logout (username, email, invalid credentials)
- Password change
- User profile updates
- Permission tests for different roles
- JWT token validation
- Admin user management

#### Job Tests (`test_jobs.py`)
- Category CRUD operations
- Job CRUD operations
- Job filtering and search
- Job permissions (owner, admin, public)
- Application submission
- Application status updates
- Status transition validation

#### Model Tests (`test_models.py`)
- Model validation (clean methods)
- Model methods (increment_views, get_full_path, etc.)
- Database constraints (unique_together)
- File upload validation
- Circular reference prevention

### 2. Integration Tests (`test_integration.py`)

- Complete authentication flow
- Job creation and application workflow
- Role-based access control
- End-to-end user workflows
- Database constraint tests
- Cascade delete tests

## Test Fixtures

Fixtures are defined in `conftest.py`:

- `api_client`: Unauthenticated API client
- `user`: Regular user instance
- `employer`: Employer user instance
- `admin_user`: Admin user instance
- `authenticated_client`: Authenticated API client (user)
- `employer_client`: Authenticated API client (employer)
- `admin_client`: Authenticated API client (admin)
- `category`: Test category
- `job`: Test job
- `application`: Test application

## Test Factories

Factory classes in `factories.py` for creating test data:

- `UserFactory`: Create user instances
- `EmployerFactory`: Create employer instances
- `AdminFactory`: Create admin instances
- `CategoryFactory`: Create category instances
- `JobFactory`: Create job instances
- `ApplicationFactory`: Create application instances

## Coverage

Coverage configuration is in `.coveragerc`. Target coverage is 80%.

To view coverage report:

```bash
pytest --cov=apps --cov-report=html
open htmlcov/index.html
```

## CI/CD Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=apps --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Best Practices

1. **Isolation**: Each test is independent and doesn't rely on other tests
2. **Fixtures**: Use fixtures for common test data
3. **Factories**: Use factories for generating test data
4. **Assertions**: Clear and specific assertions
5. **Naming**: Descriptive test names following `test_<what>_<expected_result>`
6. **Coverage**: Maintain at least 80% code coverage

## Troubleshooting

### Database Issues

If you encounter database-related errors:

```bash
# Clear test database
pytest --create-db

# Or manually
rm db.sqlite3
```

### Import Errors

Ensure you're running tests from the project root:

```bash
cd /path/to/project
pytest
```

### Fixture Errors

Make sure all fixtures are properly defined in `conftest.py` and imported correctly.
