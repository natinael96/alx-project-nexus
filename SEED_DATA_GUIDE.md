# Seed Data Guide

This guide explains how to populate your database with test data for development and testing.

## Quick Start

### Basic Usage (Default Settings)

```bash
# With Docker
docker-compose exec web python manage.py seed_data

# Locally
python manage.py seed_data
```

This will create:
- 1 admin user
- 10 employer users
- 20 regular users
- 8+ categories (with subcategories)
- 50 jobs
- 30 applications
- User profiles (skills, education, work history, social links)
- Saved jobs/bookmarks

### Custom Amounts

```bash
# Create more data
docker-compose exec web python manage.py seed_data \
    --users 50 \
    --employers 20 \
    --jobs 100 \
    --applications 50
```

### Clear and Reseed

```bash
# WARNING: This deletes all existing data!
docker-compose exec web python manage.py seed_data --clear
```

## What Gets Created

### 1. Admin User
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@jobboard.com`
- **Role**: Admin (superuser)

### 2. Employer Users
- **Username pattern**: `employer_{company}_{number}`
- **Password**: `employer123`
- **Role**: Employer
- **Companies**: TechCorp, InnovateLabs, GlobalSolutions, etc.

### 3. Regular Users
- **Username pattern**: `user_{firstname}_{lastname}_{number}`
- **Password**: `user123`
- **Role**: User
- **Names**: Random combinations of common first/last names

### 4. Categories
- Technology (with subcategories: Software Development, Data Science, DevOps, Cybersecurity)
- Healthcare
- Finance
- Education
- Marketing
- Sales
- Design
- Engineering

### 5. Jobs
- Various job titles (Software Engineer, Product Manager, Designer, etc.)
- Multiple locations (New York, San Francisco, Remote, etc.)
- Different job types (full-time, part-time, contract, internship, freelance)
- Mix of statuses (draft, active, closed)
- Some featured jobs (25%)
- Salary ranges ($50k - $150k)
- Application deadlines

### 6. Applications
- Applications from users to active approved jobs
- Various statuses (pending, reviewed, accepted, rejected)
- Cover letters included

### 7. User Profiles
Each user gets:
- **Skills**: 2-5 skills (Python, JavaScript, React, etc.) with proficiency levels
- **Education**: 1-2 education entries with degrees and fields of study
- **Work History**: 1-3 work experiences with companies and positions
- **Social Links**: 1-2 social media links (LinkedIn, GitHub, Twitter)
- **Preferences**: Default user preferences

### 8. Saved Jobs
- Half of users have saved jobs (1-5 saved jobs per user)
- Notes included for saved jobs

## Default Credentials

### Admin
- Username: `admin`
- Password: `admin123`
- URL: http://localhost:8000/admin/

### Employers
- Username: `employer_{company}_{number}` (e.g., `employer_techcorp_1`)
- Password: `employer123`

### Regular Users
- Username: `user_{firstname}_{lastname}_{number}` (e.g., `user_john_smith_1`)
- Password: `user123`

## Examples

### Minimal Data Set
```bash
docker-compose exec web python manage.py seed_data \
    --users 5 \
    --employers 3 \
    --jobs 10 \
    --applications 5
```

### Large Data Set
```bash
docker-compose exec web python manage.py seed_data \
    --users 100 \
    --employers 50 \
    --jobs 200 \
    --applications 100
```

### Reset and Reseed
```bash
# Clear everything and start fresh
docker-compose exec web python manage.py seed_data --clear \
    --users 30 \
    --employers 15 \
    --jobs 75 \
    --applications 40
```

## Testing with Seed Data

After seeding, you can:

1. **Test Login**: Use any of the created user credentials
2. **Test Job Search**: Search for jobs by category, location, or keyword
3. **Test Applications**: Submit applications as different users
4. **Test Admin Panel**: Login as admin to manage jobs and users
5. **Test Employer Features**: Login as employer to manage job postings
6. **Test User Profiles**: View and edit user profiles with skills, education, etc.

## Notes

- All passwords are simple for testing (change in production!)
- Jobs are randomly assigned to employers
- Applications are randomly assigned to users and jobs
- Dates are randomized within realistic ranges
- Some jobs are featured, some are drafts, some are closed
- User profiles are automatically created with realistic data

## Troubleshooting

### "User already exists" errors
Use `--clear` flag to remove existing data first:
```bash
docker-compose exec web python manage.py seed_data --clear
```

### Not enough jobs for applications
The command automatically limits applications to available active jobs. Increase `--jobs` if you want more applications.

### Database connection errors
Make sure your database is running and migrations are applied:
```bash
docker-compose exec web python manage.py migrate
```
