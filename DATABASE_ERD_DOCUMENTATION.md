# Database ERD Documentation
## Job Board Platform - Entity Relationship Diagram

### Overview
This document provides a comprehensive overview of the database design for the Job Board Platform, including all entities, their attributes, and relationships.

---

## Table of Contents
1. [Core Entities](#core-entities)
2. [User Profile Entities](#user-profile-entities)
3. [Job & Application Entities](#job--application-entities)
4. [Search & Analytics Entities](#search--analytics-entities)
5. [System & Security Entities](#system--security-entities)
6. [Relationship Summary](#relationship-summary)
7. [ERD Creation Instructions](#erd-creation-instructions)

---

## Core Entities

### 1. User
**Table:** `users`  
**Primary Key:** `id` (UUID)  
**Description:** Custom user model extending Django's AbstractUser with role-based access control.

**Key Attributes:**
- `id` (UUID, PK)
- `username` (String, Unique, Indexed)
- `email` (String, Indexed)
- `password` (String, Hashed)
- `first_name` (String)
- `last_name` (String)
- `role` (String: 'admin', 'employer', 'user')
- `phone_number` (String, Optional)
- `profile_picture` (Image, Optional)
- `bio` (Text, Max 500 chars, Optional)
- `is_active` (Boolean)
- `is_staff` (Boolean)
- `is_superuser` (Boolean)
- `date_joined` (DateTime)
- `last_login` (DateTime)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Indexes:**
- `role`, `is_active` (Composite)
- `email`
- `username`

**Relationships:**
- One-to-Many: Skills, Education, WorkHistory, Portfolio, SocialLinks, SavedJobs, PostedJobs, JobApplications
- One-to-One: UserPreferences, NotificationPreferences
- Many-to-Many: Groups, Permissions (via Django auth)

---

### 2. Category
**Table:** `categories`  
**Primary Key:** `id` (UUID)  
**Description:** Hierarchical category system for organizing jobs.

**Key Attributes:**
- `id` (UUID, PK)
- `name` (String, Unique, Indexed)
- `description` (Text, Optional)
- `parent` (FK to Category, Self-referential, Optional)
- `slug` (String, Unique, Indexed)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Indexes:**
- `slug`
- `parent`
- `name`, `parent` (Composite)

**Relationships:**
- Self-referential: Parent → Children (One-to-Many)
- One-to-Many: Jobs

---

## User Profile Entities

### 3. Skill
**Table:** `user_skills`  
**Primary Key:** `id` (UUID)  
**Description:** User skills with proficiency levels.

**Key Attributes:**
- `id` (UUID, PK)
- `user` (FK to User)
- `name` (String, Indexed)
- `level` (String: 'beginner', 'intermediate', 'advanced', 'expert')
- `years_of_experience` (Integer, Optional)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Unique Constraints:**
- `user`, `name` (Composite)

**Relationships:**
- Many-to-One: User

---

### 4. Education
**Table:** `user_education`  
**Primary Key:** `id` (UUID)  
**Description:** User education history.

**Key Attributes:**
- `id` (UUID, PK)
- `user` (FK to User)
- `institution` (String)
- `degree` (String)
- `field_of_study` (String)
- `start_date` (Date)
- `end_date` (Date, Optional)
- `is_current` (Boolean)
- `description` (Text, Optional)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships:**
- Many-to-One: User

---

### 5. WorkHistory
**Table:** `user_work_history`  
**Primary Key:** `id` (UUID)  
**Description:** User work experience history.

**Key Attributes:**
- `id` (UUID, PK)
- `user` (FK to User)
- `company` (String)
- `position` (String)
- `start_date` (Date)
- `end_date` (Date, Optional)
- `is_current` (Boolean)
- `description` (Text, Optional)
- `location` (String, Optional)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships:**
- Many-to-One: User

---

### 6. Portfolio
**Table:** `user_portfolio`  
**Primary Key:** `id` (UUID)  
**Description:** User portfolio/projects.

**Key Attributes:**
- `id` (UUID, PK)
- `user` (FK to User)
- `title` (String)
- `description` (Text)
- `url` (URL, Optional)
- `technologies` (String, Optional)
- `start_date` (Date, Optional)
- `end_date` (Date, Optional)
- `is_featured` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships:**
- Many-to-One: User

---

### 7. SocialLink
**Table:** `user_social_links`  
**Primary Key:** `id` (UUID)  
**Description:** User social media links.

**Key Attributes:**
- `id` (UUID, PK)
- `user` (FK to User)
- `platform` (String: 'linkedin', 'github', 'twitter', etc.)
- `url` (URL)
- `is_public` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Unique Constraints:**
- `user`, `platform` (Composite)

**Relationships:**
- Many-to-One: User

---

### 8. UserPreferences
**Table:** `user_preferences`  
**Primary Key:** `id` (UUID)  
**Description:** User preferences and settings.

**Key Attributes:**
- `id` (UUID, PK)
- `user` (FK to User, One-to-One)
- `email_job_alerts` (Boolean)
- `email_application_updates` (Boolean)
- `email_new_jobs` (Boolean)
- `email_newsletter` (Boolean)
- `alert_frequency` (String: 'immediate', 'daily', 'weekly')
- `profile_visibility` (String: 'public', 'employers', 'private')
- `show_email` (Boolean)
- `show_phone` (Boolean)
- `show_location` (Boolean)
- `resume_visibility` (String)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships:**
- One-to-One: User

---

### 9. SavedJob
**Table:** `saved_jobs`  
**Primary Key:** `id` (UUID)  
**Description:** User saved jobs/bookmarks.

**Key Attributes:**
- `id` (UUID, PK)
- `user` (FK to User)
- `job` (FK to Job)
- `notes` (Text, Optional)
- `created_at` (DateTime, Indexed)

**Unique Constraints:**
- `user`, `job` (Composite)

**Relationships:**
- Many-to-One: User, Job

---

## Job & Application Entities

### 10. Job
**Table:** `jobs`  
**Primary Key:** `id` (UUID)  
**Description:** Job postings with comprehensive details.

**Key Attributes:**
- `id` (UUID, PK)
- `title` (String, Indexed)
- `description` (Text)
- `requirements` (Text)
- `category` (FK to Category)
- `employer` (FK to User)
- `location` (String, Indexed)
- `job_type` (String: 'full-time', 'part-time', 'contract', etc.)
- `salary_min` (Decimal, Optional)
- `salary_max` (Decimal, Optional)
- `status` (String: 'draft', 'active', 'closed')
- `approval_status` (String: 'pending', 'approved', 'rejected')
- `approved_by` (FK to User, Optional)
- `approved_at` (DateTime, Optional)
- `scheduled_publish_date` (DateTime, Optional, Indexed)
- `expires_at` (DateTime, Optional, Indexed)
- `auto_renew` (Boolean)
- `renewal_count` (Integer)
- `application_deadline` (Date, Optional)
- `is_featured` (Boolean, Indexed)
- `views_count` (Integer)
- `created_at` (DateTime, Indexed)
- `updated_at` (DateTime)

**Indexes:**
- `status`, `-created_at` (Composite)
- `category`, `location` (Composite)
- `job_type`, `status` (Composite)
- `is_featured`, `status` (Composite)

**Relationships:**
- Many-to-One: Category, Employer (User), ApprovedBy (User)
- One-to-Many: Applications, JobViews, JobShares, Recommendations, SavedJobs, ScreeningQuestions
- One-to-One: JobAnalytics

---

### 11. Application
**Table:** `applications`  
**Primary Key:** `id` (UUID)  
**Description:** Job applications submitted by users.

**Key Attributes:**
- `id` (UUID, PK)
- `job` (FK to Job)
- `applicant` (FK to User)
- `cover_letter` (Text)
- `resume` (File)
- `status` (String: 'pending', 'reviewed', 'accepted', 'rejected')
- `applied_at` (DateTime, Indexed)
- `reviewed_at` (DateTime, Optional)
- `notes` (Text, Optional)
- `is_withdrawn` (Boolean, Indexed)
- `withdrawn_at` (DateTime, Optional)
- `withdrawal_reason` (Text, Optional)
- `template` (FK to ApplicationTemplate, Optional)

**Unique Constraints:**
- `job`, `applicant` (Composite)

**Indexes:**
- `status`, `-applied_at` (Composite)
- `job`, `status` (Composite)
- `applicant`, `status` (Composite)

**Relationships:**
- Many-to-One: Job, Applicant (User), ApplicationTemplate
- One-to-Many: ApplicationNotes, StatusHistory, ScreeningAnswers, Stages, Interviews
- One-to-One: ApplicationScore, ApplicationSource

---

### 12. ApplicationNote
**Table:** `application_notes`  
**Primary Key:** `id` (UUID)  
**Description:** Employer notes and ratings on applications.

**Key Attributes:**
- `id` (UUID, PK)
- `application` (FK to Application)
- `author` (FK to User)
- `note` (Text)
- `rating` (Integer 1-5, Optional)
- `is_internal` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships:**
- Many-to-One: Application, Author (User)

---

### 13. ApplicationStatusHistory
**Table:** `application_status_history`  
**Primary Key:** `id` (UUID)  
**Description:** Tracks application status changes.

**Key Attributes:**
- `id` (UUID, PK)
- `application` (FK to Application)
- `old_status` (String, Optional)
- `new_status` (String)
- `changed_by` (FK to User, Optional)
- `reason` (Text, Optional)
- `changed_at` (DateTime, Indexed)

**Relationships:**
- Many-to-One: Application, ChangedBy (User)

---

### 14. ScreeningQuestion
**Table:** `screening_questions`  
**Primary Key:** `id` (UUID)  
**Description:** Job screening questions.

**Key Attributes:**
- `id` (UUID, PK)
- `job` (FK to Job)
- `question` (Text)
- `question_type` (String: 'text', 'multiple_choice', 'yes_no', etc.)
- `is_required` (Boolean)
- `order` (Integer)
- `options` (JSON, Optional)
- `created_at` (DateTime)

**Relationships:**
- Many-to-One: Job
- One-to-Many: ScreeningAnswers

---

### 15. ScreeningAnswer
**Table:** `screening_answers`  
**Primary Key:** `id` (UUID)  
**Description:** Answers to screening questions.

**Key Attributes:**
- `id` (UUID, PK)
- `application` (FK to Application)
- `question` (FK to ScreeningQuestion)
- `answer` (Text)
- `created_at` (DateTime)

**Unique Constraints:**
- `application`, `question` (Composite)

**Relationships:**
- Many-to-One: Application, Question (ScreeningQuestion)

---

### 16. ApplicationStage
**Table:** `application_stages`  
**Primary Key:** `id` (UUID)  
**Description:** Multi-stage application process.

**Key Attributes:**
- `id` (UUID, PK)
- `application` (FK to Application)
- `stage_type` (String: 'application', 'screening', 'interview', etc.)
- `stage_name` (String)
- `order` (Integer)
- `is_completed` (Boolean)
- `completed_at` (DateTime, Optional)
- `notes` (Text, Optional)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships:**
- Many-to-One: Application

---

### 17. Interview
**Table:** `interviews`  
**Primary Key:** `id` (UUID)  
**Description:** Interview scheduling.

**Key Attributes:**
- `id` (UUID, PK)
- `application` (FK to Application)
- `scheduled_at` (DateTime)
- `duration` (Integer, minutes)
- `interview_type` (String: 'phone', 'video', 'in_person', etc.)
- `location` (String, Optional)
- `video_link` (URL, Optional)
- `interviewer` (FK to User, Optional)
- `notes` (Text, Optional)
- `is_confirmed` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships:**
- Many-to-One: Application, Interviewer (User)

---

### 18. ApplicationScore
**Table:** `application_scores`  
**Primary Key:** `id` (UUID)  
**Description:** Application scoring/ranking.

**Key Attributes:**
- `id` (UUID, PK)
- `application` (FK to Application, One-to-One)
- `overall_score` (Float)
- `experience_score` (Float)
- `skills_score` (Float)
- `education_score` (Float)
- `screening_score` (Float)
- `notes` (Text, Optional)
- `scored_by` (FK to User, Optional)
- `scored_at` (DateTime)
- `updated_at` (DateTime)

**Relationships:**
- One-to-One: Application
- Many-to-One: ScoredBy (User)

---

### 19. ApplicationTemplate
**Table:** `application_templates`  
**Primary Key:** `id` (UUID)  
**Description:** Application templates for employers.

**Key Attributes:**
- `id` (UUID, PK)
- `employer` (FK to User)
- `name` (String)
- `description` (Text, Optional)
- `default_notes` (Text, Optional)
- `is_active` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships:**
- Many-to-One: Employer (User)
- One-to-Many: Applications

---

### 20. ApplicationSource
**Table:** `application_sources`  
**Primary Key:** `id` (UUID)  
**Description:** Tracks where applications come from.

**Key Attributes:**
- `id` (UUID, PK)
- `application` (FK to Application, One-to-One)
- `source_type` (String: 'direct', 'referral', 'job_board', etc.)
- `referrer_url` (URL, Optional)
- `campaign` (String, Optional)
- `utm_source` (String, Optional)
- `utm_medium` (String, Optional)
- `utm_campaign` (String, Optional)
- `created_at` (DateTime)

**Relationships:**
- One-to-One: Application

---

## Search & Analytics Entities

### 21. JobView
**Table:** `job_views`  
**Primary Key:** `id` (UUID)  
**Description:** Tracks job views for analytics.

**Key Attributes:**
- `id` (UUID, PK)
- `job` (FK to Job)
- `user` (FK to User, Optional)
- `ip_address` (IP Address, Optional)
- `user_agent` (String, Optional)
- `referrer` (URL, Optional)
- `viewed_at` (DateTime, Indexed)

**Relationships:**
- Many-to-One: Job, User (Optional)

---

### 22. JobShare
**Table:** `job_shares`  
**Primary Key:** `id` (UUID)  
**Description:** Tracks job shares.

**Key Attributes:**
- `id` (UUID, PK)
- `job` (FK to Job)
- `user` (FK to User, Optional)
- `method` (String: 'email', 'link', 'social', etc.)
- `shared_with` (String, Optional)
- `shared_at` (DateTime, Indexed)

**Relationships:**
- Many-to-One: Job, User (Optional)

---

### 23. JobRecommendation
**Table:** `job_recommendations`  
**Primary Key:** `id` (UUID)  
**Description:** Job recommendations to users.

**Key Attributes:**
- `id` (UUID, PK)
- `user` (FK to User)
- `job` (FK to Job)
- `score` (Float)
- `reason` (String, Optional)
- `created_at` (DateTime, Indexed)
- `viewed` (Boolean)
- `clicked` (Boolean)

**Unique Constraints:**
- `user`, `job` (Composite)

**Relationships:**
- Many-to-One: User, Job

---

### 24. JobAnalytics
**Table:** `job_analytics`  
**Primary Key:** `id` (UUID)  
**Description:** Job performance analytics.

**Key Attributes:**
- `id` (UUID, PK)
- `job` (FK to Job, One-to-One)
- `total_views` (Integer)
- `unique_views` (Integer)
- `total_applications` (Integer)
- `shares_count` (Integer)
- `saved_count` (Integer)
- `last_updated` (DateTime)

**Relationships:**
- One-to-One: Job

---

### 25. SearchHistory
**Table:** `search_history`  
**Primary Key:** `id` (UUID)  
**Description:** Tracks user search history.

**Key Attributes:**
- `id` (UUID, PK)
- `user` (FK to User, Optional)
- `search_query` (String, Indexed)
- `filters` (JSON)
- `result_count` (Integer)
- `ip_address` (IP Address, Optional)
- `created_at` (DateTime, Indexed)

**Relationships:**
- Many-to-One: User (Optional)

---

### 26. SavedSearch
**Table:** `saved_searches`  
**Primary Key:** `id` (UUID)  
**Description:** Saved searches that users can revisit.

**Key Attributes:**
- `id` (UUID, PK)
- `user` (FK to User)
- `name` (String)
- `search_query` (String)
- `filters` (JSON)
- `is_active` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `last_searched_at` (DateTime, Optional)

**Unique Constraints:**
- `user`, `name` (Composite)

**Relationships:**
- Many-to-One: User
- One-to-Many: SearchAlerts

---

### 27. SearchAlert
**Table:** `search_alerts`  
**Primary Key:** `id` (UUID)  
**Description:** Search alerts that notify users of new matching jobs.

**Key Attributes:**
- `id` (UUID, PK)
- `user` (FK to User)
- `saved_search` (FK to SavedSearch, Optional)
- `name` (String)
- `search_query` (String)
- `filters` (JSON)
- `frequency` (String: 'daily', 'weekly', 'immediate')
- `is_active` (Boolean)
- `last_notified_at` (DateTime, Optional)
- `last_job_id` (Integer, Optional)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships:**
- Many-to-One: User, SavedSearch (Optional)

---

### 28. PopularSearchTerm
**Table:** `popular_search_terms`  
**Primary Key:** `id` (UUID)  
**Description:** Tracks popular search terms for analytics.

**Key Attributes:**
- `id` (UUID, PK)
- `term` (String, Unique, Indexed)
- `search_count` (Integer)
- `last_searched_at` (DateTime, Indexed)
- `first_searched_at` (DateTime)

**Relationships:**
- None (Standalone entity)

---

## System & Security Entities

### 29. Notification
**Table:** `notifications`  
**Primary Key:** `id` (UUID)  
**Description:** In-app notifications.

**Key Attributes:**
- `id` (UUID, PK)
- `user` (FK to User)
- `notification_type` (String, Indexed)
- `title` (String)
- `message` (Text)
- `priority` (String: 'low', 'normal', 'high', 'urgent')
- `is_read` (Boolean, Indexed)
- `read_at` (DateTime, Optional)
- `action_url` (URL, Optional)
- `related_object_type` (String, Optional)
- `related_object_id` (String, Optional)
- `metadata` (JSON)
- `created_at` (DateTime, Indexed)

**Relationships:**
- Many-to-One: User

---

### 30. NotificationPreference
**Table:** `notification_preferences`  
**Primary Key:** `id` (UUID)  
**Description:** User notification preferences.

**Key Attributes:**
- `id` (UUID, PK)
- `user` (FK to User, One-to-One)
- `in_app_job_applications` (Boolean)
- `in_app_application_updates` (Boolean)
- `in_app_new_jobs` (Boolean)
- `in_app_messages` (Boolean)
- `in_app_system` (Boolean)
- `notification_frequency` (String)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships:**
- One-to-One: User

---

### 31. AuditLog
**Table:** `audit_logs`  
**Primary Key:** `id` (UUID)  
**Description:** Audit logging for all system changes.

**Key Attributes:**
- `id` (UUID, PK)
- `user` (FK to User, Optional)
- `action` (String, Indexed)
- `content_type` (FK to ContentType, Optional)
- `object_id` (String, Optional)
- `object_repr` (String)
- `changes` (JSON)
- `ip_address` (IP Address, Optional)
- `user_agent` (String, Optional)
- `request_path` (String, Optional)
- `request_method` (String, Optional)
- `metadata` (JSON)
- `created_at` (DateTime, Indexed)

**Relationships:**
- Many-to-One: User (Optional)
- Generic Foreign Key: ContentType, ObjectId

---

### 32. ChangeHistory
**Table:** `change_history`  
**Primary Key:** `id` (UUID)  
**Description:** Detailed change history of specific objects.

**Key Attributes:**
- `id` (UUID, PK)
- `content_type` (FK to ContentType)
- `object_id` (String)
- `changed_by` (FK to User, Optional)
- `field_name` (String)
- `old_value` (Text)
- `new_value` (Text)
- `change_reason` (Text, Optional)
- `created_at` (DateTime, Indexed)

**Relationships:**
- Many-to-One: ChangedBy (User, Optional)
- Generic Foreign Key: ContentType, ObjectId

---

### 33. APIKey
**Table:** `api_keys`  
**Primary Key:** `id` (UUID)  
**Description:** API keys for programmatic access.

**Key Attributes:**
- `id` (UUID, PK)
- `name` (String)
- `key` (String, Unique, Indexed)
- `user` (FK to User)
- `is_active` (Boolean)
- `last_used_at` (DateTime, Optional)
- `expires_at` (DateTime, Optional)
- `rate_limit` (Integer)
- `allowed_ips` (Text, Optional)
- `scopes` (JSON)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships:**
- Many-to-One: User

---

### 34. IPWhitelist
**Table:** `ip_whitelist`  
**Primary Key:** `id` (UUID)  
**Description:** IP whitelisting for admin access.

**Key Attributes:**
- `id` (UUID, PK)
- `ip_address` (IP Address, Unique)
- `description` (String, Optional)
- `is_active` (Boolean)
- `created_by` (FK to User, Optional)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Relationships:**
- Many-to-One: CreatedBy (User, Optional)

---

### 35. SecurityEvent
**Table:** `security_events`  
**Primary Key:** `id` (UUID)  
**Description:** Tracks security events.

**Key Attributes:**
- `id` (UUID, PK)
- `event_type` (String, Indexed)
- `user` (FK to User, Optional)
- `ip_address` (IP Address, Optional)
- `user_agent` (String, Optional)
- `details` (JSON)
- `created_at` (DateTime, Indexed)

**Relationships:**
- Many-to-One: User (Optional)

---

## Relationship Summary

### One-to-Many Relationships
1. **User → Skills** (1:N)
2. **User → Education** (1:N)
3. **User → WorkHistory** (1:N)
4. **User → Portfolio** (1:N)
5. **User → SocialLinks** (1:N)
6. **User → SavedJobs** (1:N)
7. **User → PostedJobs** (1:N)
8. **User → JobApplications** (1:N)
9. **User → ApplicationNotes** (1:N)
10. **User → Notifications** (1:N)
11. **User → SearchHistory** (1:N)
12. **User → SavedSearches** (1:N)
13. **User → SearchAlerts** (1:N)
14. **User → APIKeys** (1:N)
15. **Category → Jobs** (1:N)
16. **Category → Children** (Self-referential, 1:N)
17. **Job → Applications** (1:N)
18. **Job → JobViews** (1:N)
19. **Job → JobShares** (1:N)
20. **Job → Recommendations** (1:N)
21. **Job → ScreeningQuestions** (1:N)
22. **Application → ApplicationNotes** (1:N)
23. **Application → StatusHistory** (1:N)
24. **Application → ScreeningAnswers** (1:N)
25. **Application → Stages** (1:N)
26. **Application → Interviews** (1:N)
27. **ScreeningQuestion → ScreeningAnswers** (1:N)
28. **ApplicationTemplate → Applications** (1:N)
29. **SavedSearch → SearchAlerts** (1:N)

### One-to-One Relationships
1. **User ↔ UserPreferences** (1:1)
2. **User ↔ NotificationPreferences** (1:1)
3. **Job ↔ JobAnalytics** (1:1)
4. **Application ↔ ApplicationScore** (1:1)
5. **Application ↔ ApplicationSource** (1:1)

### Many-to-Many Relationships
1. **User ↔ Groups** (via Django auth, M:N)
2. **User ↔ Permissions** (via Django auth, M:N)
3. **User ↔ Jobs** (via SavedJob, M:N)
4. **User ↔ Jobs** (via JobRecommendation, M:N)

### Self-Referential Relationships
1. **Category → Parent Category** (Self-referential, 1:N)

---

## ERD Creation Instructions

### Using Draw.io (Recommended)

1. **Access Draw.io:**
   - Go to https://app.diagrams.net/ (formerly draw.io)
   - Or use the desktop application

2. **Create New Diagram:**
   - Click "Create New Diagram"
   - Select "Entity Relationship" template
   - Or start with a blank diagram

3. **Add Entities:**
   - Use rectangles for entities
   - Label each entity with the table name
   - Add attributes inside each entity box
   - Use different colors for different entity groups:
     - **Blue**: Core entities (User, Category)
     - **Green**: User Profile entities
     - **Orange**: Job & Application entities
     - **Purple**: Search & Analytics entities
     - **Red**: System & Security entities

4. **Add Relationships:**
   - Use lines to connect entities
   - Add cardinality indicators:
     - **1** (One)
     - **N** (Many)
     - **0..1** (Zero or One)
   - Label relationships with foreign key names
   - Use different line styles:
     - **Solid line**: Required relationship
     - **Dashed line**: Optional relationship

5. **Key Symbols:**
   - **PK**: Primary Key (underline or mark with key icon)
   - **FK**: Foreign Key (mark with FK icon)
   - **U**: Unique constraint
   - **I**: Indexed field

6. **Layout Tips:**
   - Place User entity in the center
   - Group related entities together
   - Use hierarchical layout for Category (parent-child)
   - Keep relationships clear and avoid crossing lines when possible

### Using Lucidchart

1. **Access Lucidchart:**
   - Go to https://www.lucidchart.com/
   - Sign in or create account

2. **Create ERD:**
   - Click "Create" → "Entity Relationship Diagram"
   - Or use "Database" template

3. **Add Entities:**
   - Drag "Entity" shapes onto canvas
   - Double-click to edit entity name
   - Add attributes in the entity properties panel

4. **Add Relationships:**
   - Use "Relationship" connector
   - Set cardinality in relationship properties
   - Add labels for foreign keys

5. **Export:**
   - File → Export → PNG/PDF/SVG
   - Or share via link with viewing permissions

### ERD Structure Recommendations

**Suggested Layout:**
```
Top Section: System & Security Entities
  - Notification, NotificationPreference
  - AuditLog, ChangeHistory
  - APIKey, IPWhitelist, SecurityEvent

Center-Left: User & Profile Entities
  - User (center)
  - UserPreferences, NotificationPreference (attached to User)
  - Skills, Education, WorkHistory, Portfolio, SocialLinks (around User)
  - SavedJobs (connecting User to Jobs)

Center-Right: Job & Application Entities
  - Category (top, with self-referential arrows)
  - Job (below Category)
  - Application (below Job)
  - Application enhancements (around Application)
  - Job enhancements (around Job)

Bottom: Search & Analytics
  - SearchHistory, SavedSearch, SearchAlert
  - PopularSearchTerm
  - JobView, JobShare, JobRecommendation, JobAnalytics
```

### Key Relationships to Highlight

1. **User is central** - Most entities relate to User
2. **Category → Job → Application** - Main workflow
3. **Application has many enhancements** - Notes, Stages, Interviews, etc.
4. **Job has analytics** - Views, Shares, Recommendations
5. **Search system** - Independent but connects to User and Job

---

## Export and Sharing

### Export Formats
- **PNG**: For documents and presentations
- **PDF**: For printing and documentation
- **SVG**: For scalable vector graphics
- **XML**: For Draw.io format (editable)

### Sharing Options
1. **Google Docs:**
   - Insert → Image → Upload from computer
   - Or insert as a link to the ERD file

2. **Google Drive:**
   - Upload ERD file
   - Set sharing permissions to "Anyone with the link can view"
   - Insert link in Google Doc

3. **Lucidchart:**
   - Publish diagram
   - Get shareable link
   - Insert link in Google Doc

---

## Notes for Mentors

- All models use **UUID** as primary keys for better scalability
- **Indexes** are strategically placed for query optimization
- **Unique constraints** prevent data duplication
- **Foreign keys** maintain referential integrity
- **Cascade deletes** are used appropriately (e.g., deleting User deletes related profile data)
- **SET_NULL** is used for optional relationships (e.g., approved_by can be null)
- **Generic Foreign Keys** are used in AuditLog and ChangeHistory for flexible tracking

---

## Version History

- **Version 1.0** - Initial ERD documentation
- Created: 2026-02-07
- Total Entities: 35
- Total Relationships: 50+

---

**End of Documentation**
