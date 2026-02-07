# ERD Quick Reference Guide
## Job Board Platform - Database Schema

### Entity Count Summary
- **Total Entities**: 35
- **Core Entities**: 2 (User, Category)
- **User Profile Entities**: 7
- **Job & Application Entities**: 11
- **Search & Analytics Entities**: 8
- **System & Security Entities**: 7

---

## Core Entities (2)

| Entity | Table Name | Primary Key | Key Relationships |
|--------|-----------|-------------|-------------------|
| **User** | `users` | id (UUID) | Central entity - connects to most others |
| **Category** | `categories` | id (UUID) | Self-referential (parent-child), connects to Jobs |

---

## User Profile Entities (7)

| Entity | Table Name | Relationship to User |
|--------|-----------|---------------------------|
| Skill | `user_skills` | Many-to-One |
| Education | `user_education` | Many-to-One |
| WorkHistory | `user_work_history` | Many-to-One |
| Portfolio | `user_portfolio` | Many-to-One |
| SocialLink | `user_social_links` | Many-to-One |
| UserPreferences | `user_preferences` | One-to-One |
| SavedJob | `saved_jobs` | Many-to-One (also connects to Job) |

---

## Job & Application Entities (11)

| Entity | Table Name | Key Relationships |
|--------|-----------|-------------------|
| **Job** | `jobs` | Many-to-One: Category, Employer (User), ApprovedBy (User) |
| **Application** | `jobs` | Many-to-One: Job, Applicant (User) |
| ApplicationNote | `application_notes` | Many-to-One: Application, Author (User) |
| ApplicationStatusHistory | `application_status_history` | Many-to-One: Application, ChangedBy (User) |
| ScreeningQuestion | `screening_questions` | Many-to-One: Job |
| ScreeningAnswer | `screening_answers` | Many-to-One: Application, Question |
| ApplicationStage | `application_stages` | Many-to-One: Application |
| Interview | `interviews` | Many-to-One: Application, Interviewer (User) |
| ApplicationScore | `application_scores` | One-to-One: Application |
| ApplicationTemplate | `application_templates` | Many-to-One: Employer (User) |
| ApplicationSource | `application_sources` | One-to-One: Application |

---

## Search & Analytics Entities (8)

| Entity | Table Name | Key Relationships |
|--------|-----------|-------------------|
| JobView | `job_views` | Many-to-One: Job, User (optional) |
| JobShare | `job_shares` | Many-to-One: Job, User (optional) |
| JobRecommendation | `job_recommendations` | Many-to-One: User, Job |
| JobAnalytics | `job_analytics` | One-to-One: Job |
| SearchHistory | `search_history` | Many-to-One: User (optional) |
| SavedSearch | `saved_searches` | Many-to-One: User |
| SearchAlert | `search_alerts` | Many-to-One: User, SavedSearch (optional) |
| PopularSearchTerm | `popular_search_terms` | None (standalone) |

---

## System & Security Entities (7)

| Entity | Table Name | Key Relationships |
|--------|-----------|-------------------|
| Notification | `notifications` | Many-to-One: User |
| NotificationPreference | `notification_preferences` | One-to-One: User |
| AuditLog | `audit_logs` | Many-to-One: User (optional), Generic FK |
| ChangeHistory | `change_history` | Many-to-One: ChangedBy (User, optional), Generic FK |
| APIKey | `api_keys` | Many-to-One: User |
| IPWhitelist | `ip_whitelist` | Many-to-One: CreatedBy (User, optional) |
| SecurityEvent | `security_events` | Many-to-One: User (optional) |

---

## Key Relationships Diagram

```
                    ┌─────────┐
                    │  User   │
                    └────┬────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   ┌─────────┐      ┌─────────┐      ┌─────────┐
   │ Skills  │      │Education │      │WorkHist │
   └─────────┘      └─────────┘      └─────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   ┌─────────┐      ┌─────────┐      ┌─────────┐
   │Portfolio│      │SocialLink│      │Preferences│
   └─────────┘      └─────────┘      └─────────┘

                    ┌─────────┐
                    │Category  │◄───┐
                    └────┬─────┘    │ (self-ref)
                         │           │
                         ▼           │
                    ┌─────────┐      │
                    │   Job   │      │
                    └────┬────┘      │
                         │           │
                         ▼           │
                 ┌──────────────┐    │
                 │ Application  │    │
                 └──────────────┘    │
                         │            │
        ┌────────────────┼────────────┘
        │                │
        ▼                ▼
   ┌─────────┐      ┌─────────┐
   │  Notes  │      │  Stages  │
   └─────────┘      └─────────┘
```

---

## ERD Creation Checklist

### Step 1: Setup
- [ ] Choose tool (Draw.io or Lucidchart)
- [ ] Create new ERD diagram
- [ ] Set up color scheme for entity groups

### Step 2: Core Entities
- [ ] Add User entity (center)
- [ ] Add Category entity (top)
- [ ] Add self-referential relationship for Category

### Step 3: User Profile Entities
- [ ] Add all 7 profile entities around User
- [ ] Connect to User with 1:N relationships
- [ ] Add UserPreferences as 1:1 relationship

### Step 4: Job & Application Entities
- [ ] Add Job entity (below Category)
- [ ] Connect Category → Job (1:N)
- [ ] Connect User → Job as Employer (1:N)
- [ ] Add Application entity (below Job)
- [ ] Connect Job → Application (1:N)
- [ ] Connect User → Application as Applicant (1:N)
- [ ] Add all application enhancement entities
- [ ] Connect to Application appropriately

### Step 5: Search & Analytics
- [ ] Add search-related entities
- [ ] Add analytics entities
- [ ] Connect to User and Job

### Step 6: System & Security
- [ ] Add notification entities
- [ ] Add audit/security entities
- [ ] Connect to User

### Step 7: Final Touches
- [ ] Add all primary keys (marked with PK)
- [ ] Add all foreign keys (marked with FK)
- [ ] Add cardinality indicators (1, N, 0..1)
- [ ] Add unique constraints where applicable
- [ ] Add indexes notation
- [ ] Add legend/color key
- [ ] Review for clarity and completeness

### Step 8: Export
- [ ] Export as PNG/PDF
- [ ] Insert into Google Doc
- [ ] Set sharing permissions
- [ ] Add link to documentation

---

## Color Coding Scheme

| Color | Entity Group | Examples |
|-------|-------------|----------|
| **Blue** | Core Entities | User, Category |
| **Green** | User Profile | Skills, Education, Portfolio |
| **Orange** | Job & Application | Job, Application, Interview |
| **Purple** | Search & Analytics | SearchHistory, JobAnalytics |
| **Red** | System & Security | Notification, AuditLog, APIKey |

---

## Cardinality Notation

- **1** = One (required)
- **N** = Many
- **0..1** = Zero or One (optional)
- **1..N** = One or Many (at least one)

### Examples:
- User → Skills: **1** to **N**
- User → UserPreferences: **1** to **0..1**
- Job → Application: **1** to **N**
- Application → ApplicationScore: **1** to **0..1**

---

## Important Notes

1. **All primary keys are UUIDs** - Not auto-incrementing integers
2. **Cascade deletes** - Deleting User deletes related profile data
3. **SET_NULL** - Used for optional relationships (e.g., approved_by)
4. **Generic Foreign Keys** - Used in AuditLog and ChangeHistory
5. **Self-referential** - Category has parent-child relationships
6. **Unique constraints** - Prevent duplicates (e.g., user+job in SavedJob)

---

## Quick Stats

- **Total Tables**: 35
- **One-to-Many Relationships**: 29
- **One-to-One Relationships**: 5
- **Many-to-Many Relationships**: 4 (including Django auth)
- **Self-Referential**: 1 (Category)
- **Generic Foreign Keys**: 2 (AuditLog, ChangeHistory)

---

**Use this guide alongside the detailed documentation to create your ERD!**
