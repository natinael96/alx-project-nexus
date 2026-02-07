# Simplified Mermaid ERD
## Job Board Platform - Core Relationships

This is a simplified version focusing on the most important entities and relationships. Use this if the full diagram is too complex to render.

```mermaid
erDiagram
    %% Core Entities
    User {
        uuid id PK
        string username UK
        string email
        string role
        datetime created_at
    }

    Category {
        uuid id PK
        string name UK
        uuid parent_id FK
        string slug UK
    }

    %% User Profile
    Skill {
        uuid id PK
        uuid user_id FK
        string name
        string level
    }

    Education {
        uuid id PK
        uuid user_id FK
        string institution
        string degree
    }

    WorkHistory {
        uuid id PK
        uuid user_id FK
        string company
        string position
    }

    Portfolio {
        uuid id PK
        uuid user_id FK
        string title
        text description
    }

    UserPreferences {
        uuid id PK
        uuid user_id FK
        boolean email_job_alerts
    }

    %% Job & Application
    Job {
        uuid id PK
        string title
        text description
        uuid category_id FK
        uuid employer_id FK
        string status
        string job_type
    }

    Application {
        uuid id PK
        uuid job_id FK
        uuid applicant_id FK
        string status
        text cover_letter
    }

    ScreeningQuestion {
        uuid id PK
        uuid job_id FK
        text question
    }

    Interview {
        uuid id PK
        uuid application_id FK
        datetime scheduled_at
    }

    %% Search & Analytics
    SavedJob {
        uuid id PK
        uuid user_id FK
        uuid job_id FK
    }

    SearchHistory {
        uuid id PK
        uuid user_id FK
        string search_query
    }

    JobAnalytics {
        uuid id PK
        uuid job_id FK
        integer total_views
    }

    %% System
    Notification {
        uuid id PK
        uuid user_id FK
        string notification_type
    }

    %% Relationships - User Profile
    User ||--o{ Skill : "has"
    User ||--o{ Education : "has"
    User ||--o{ WorkHistory : "has"
    User ||--o{ Portfolio : "has"
    User ||--|| UserPreferences : "has"
    User ||--o{ SavedJob : "saves"
    User ||--o{ SearchHistory : "searches"
    User ||--o{ Notification : "receives"

    %% Relationships - Category
    Category ||--o{ Category : "parent"
    Category ||--o{ Job : "contains"

    %% Relationships - Job
    User ||--o{ Job : "posts"
    Job ||--o{ Application : "receives"
    Job ||--o{ SavedJob : "saved_by"
    Job ||--|| JobAnalytics : "has"
    Job ||--o{ ScreeningQuestion : "has"

    %% Relationships - Application
    User ||--o{ Application : "applies"
    Application ||--o{ Interview : "has"
```

---

## How to Use

1. **Copy the Mermaid code above**
2. **Go to https://mermaid.live/**
3. **Paste and view the diagram**
4. **Export as PNG/SVG**
5. **Insert into Google Doc**

---

## Full Version Available

For the complete ERD with all 35 entities, see `ERD_MERMAID.md`
