# Frontend Integration Guide — Job Board Platform

**Base URL:** `https://alx-nexus-a5a0e2db51ca.herokuapp.com`
**API Docs:** `https://alx-nexus-a5a0e2db51ca.herokuapp.com/api/docs/`

---

## Table of Contents

1. [Authentication Setup](#1-authentication-setup)
2. [Role System](#2-role-system)
3. [Pages & Flows by Role](#3-pages--flows-by-role)
4. [Page-by-Page Breakdown](#4-page-by-page-breakdown)
5. [Global Components](#5-global-components)
6. [API Quick Reference](#6-api-quick-reference)
7. [Error Handling](#7-error-handling)

---

## 1. Authentication Setup

### How Auth Works

Every protected API call needs a JWT token in the header:

```
Authorization: Bearer <access_token>
```

**Token lifecycle:**
- `access` token → short-lived (use for API calls)
- `refresh` token → long-lived (use to get a new access token when it expires)

**Store tokens** in `localStorage` or a secure cookie. Create an Axios/fetch interceptor that:
1. Attaches `Authorization: Bearer <access>` to every request
2. On `401` response → call `/api/auth/refresh/` with the refresh token
3. If refresh fails → redirect to `/login`

---

## 2. Role System

There are **3 roles**. The role comes back in the user object after login/register.

| Role | Value | Can Do |
|------|-------|--------|
| **Job Seeker** | `"user"` | Browse jobs, apply, manage profile, save jobs |
| **Employer** | `"employer"` | Post jobs, manage applications, view analytics |
| **Admin** | `"admin"` | Everything + user management, statistics, audit logs, exports |

**Frontend routing should check `user.role`** and redirect/guard pages accordingly.

---

## 3. Pages & Flows by Role

### 3.1 — Unauthenticated User (Public)

```
Landing Page  →  Browse Jobs (list)  →  Job Detail  →  [Login/Register to Apply]
                  Search Jobs
                  View Categories
```

### 3.2 — Job Seeker (`role: "user"`)

```
Login/Register
    ↓
Dashboard (home)
    ├── My Applications (list + status)
    ├── Saved Jobs
    ├── Profile Completion %
    ├── Recent Activity
    ↓
Browse Jobs → Job Detail → Apply (form + resume upload)
    ↓
My Applications → Application Detail → Withdraw
    ↓
My Profile → Edit Profile / Skills / Education / Work History / Portfolio / Social Links
    ↓
Notifications → Mark Read
    ↓
Settings → Change Password / Preferences
```

### 3.3 — Employer (`role: "employer"`)

```
Login/Register (role: "employer")
    ↓
Employer Dashboard (home)
    ├── Job Stats (active/draft/closed)
    ├── Application Stats (pending/accepted/rejected)
    ├── View Stats (total/unique)
    ├── Top Performing Jobs
    ├── Recent Applications
    ↓
My Jobs → Create Job → Job Detail (edit/close/delete)
    ↓
Job Applications → Application Detail → Review → Accept/Reject
    ├── Add Notes
    ├── Score Applicant
    ├── Schedule Interview
    ↓
Job Analytics (per job)
    ↓
Screening Questions (create/manage per job)
    ↓
Application Templates (reusable templates)
    ↓
Export Data (CSV/JSON)
```

### 3.4 — Admin (`role: "admin"`)

```
Admin Dashboard
    ├── Platform Statistics (users, jobs, applications)
    ├── User Management (list/edit/delete users)
    ├── All Jobs (approve/reject/manage)
    ├── All Applications
    ├── Audit Logs
    ├── Change History
    ├── Export (users/jobs/applications)
    ├── Search Statistics
```

---

## 4. Page-by-Page Breakdown

---

### PAGE: Landing Page `/`

**Purpose:** First thing users see. Showcase the platform.

**UI Components:**
- Hero section with search bar (job title + location)
- "Featured Jobs" carousel/grid (max 10 cards)
- Category cards grid
- Stats counters (total jobs, companies, etc.)
- CTA buttons: "Find Jobs" / "Post a Job"

**API Calls on Load:**
```
GET /api/jobs/?is_featured=true&status=active    → featured jobs
GET /api/categories/                              → all categories
GET /health/                                      → platform status (optional)
```

**User Actions:**
- Click search → navigate to `/jobs?search=<query>&location=<loc>`
- Click featured job card → `/jobs/<id>`
- Click category card → `/jobs?category=<uuid>`
- Click "Post a Job" → `/register` (with employer pre-selected) or `/employer/jobs/new`

---

### PAGE: Register `/register`

**Purpose:** Create a new account.

**UI Components:**
- Form with fields:
  - `username` (text, min 3 chars, alphanumeric + _ .)
  - `email` (email input)
  - `first_name` (text, required)
  - `last_name` (text, required)
  - `password` (password, min 8 chars)
  - `password2` (confirm password)
  - `role` (radio/select: "user" or "employer") — **cannot select "admin"**
  - `phone_number` (optional, format: +999999999)
  - `bio` (optional textarea, max 500 chars)
- "Already have an account? Login" link

**API Call:**
```
POST /api/auth/register/
Body: {
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "role": "user",           // or "employer"
    "phone_number": "+1234567890",  // optional
    "bio": "Software developer"     // optional
}
```

**Success Response (201):**
```json
{
    "user": {
        "id": "uuid",
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "role": "user",
        ...
    },
    "message": "User registered successfully"
}
```

**After Success:** Redirect to `/login` with a success toast.

**Validation Errors to Handle:**
- `"A user with this email already exists."`
- `"Username must be at least 3 characters long."`
- `"Password fields didn't match."`
- `"Cannot register as admin."`

---

### PAGE: Login `/login`

**Purpose:** Authenticate user.

**UI Components:**
- Form:
  - `username` (accepts username OR email)
  - `password`
- "Forgot Password?" link
- "Don't have an account? Register" link
- OAuth buttons (Google, etc.) — optional

**API Call:**
```
POST /api/auth/login/
Body: {
    "username": "johndoe",     // or "john@example.com"
    "password": "SecurePass123!"
}
```

**Success Response (200):**
```json
{
    "access": "eyJ...",       // ← Store this
    "refresh": "eyJ...",      // ← Store this
    "user": {
        "id": "uuid",
        "username": "johndoe",
        "role": "user",
        ...
    }
}
```

**After Success:**
1. Store `access` and `refresh` tokens
2. Store `user` object in state/context
3. Redirect based on role:
   - `"user"` → `/dashboard`
   - `"employer"` → `/employer/dashboard`
   - `"admin"` → `/admin/dashboard`

---

### PAGE: Forgot Password `/forgot-password`

**UI Components:**
- Email input
- Submit button

**API Call:**
```
POST /api/auth/password-reset/
Body: { "email": "john@example.com" }
```

**Then:** Show "Check your email" message.

**Reset Confirm (from email link):**
```
POST /api/auth/password-reset/confirm/
Body: {
    "token": "<from_email_link>",
    "new_password": "NewPass123!",
    "new_password2": "NewPass123!"
}
```

---

### PAGE: Browse Jobs `/jobs`

**Purpose:** Main job listing with filters and search. Accessible to everyone.

**UI Components:**
- **Search bar** at top (text input + location input)
- **Filter sidebar** (left side or collapsible on mobile):
  - Category dropdown (from `/api/categories/`)
  - Job Type checkboxes: Full Time, Part Time, Contract, Internship, Freelance
  - Location text input
  - Salary range slider (min_salary, max_salary)
  - Featured only toggle
- **Job cards grid/list** (each card shows):
  - Job title
  - Employer name
  - Location
  - Job type badge
  - Salary range
  - Posted date (relative: "2 days ago")
  - "Featured" badge if `is_featured: true`
  - Application count
- **Pagination** (page numbers or infinite scroll)
- **Sort dropdown**: Newest, Salary (High→Low), Most Viewed

**API Call:**
```
GET /api/jobs/?search=developer&location=remote&category=<uuid>&job_type=full-time&min_salary=50000&max_salary=100000&is_featured=true&ordering=-created_at&page=1
```

**Response shape:**
```json
{
    "count": 42,
    "next": "...?page=2",
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "title": "Senior Developer",
            "description": "...",
            "category": { "id": "uuid", "name": "Engineering", ... },
            "employer": { "id": "uuid", "username": "techcorp" },
            "location": "Remote",
            "job_type": "full-time",
            "salary_min": "80000.00",
            "salary_max": "120000.00",
            "status": "active",
            "is_featured": true,
            "views_count": 234,
            "application_count": 15,
            "created_at": "2026-02-05T10:30:00Z"
        }
    ]
}
```

**Filter Parameters Summary:**

| Param | Type | Example |
|-------|------|---------|
| `search` | string | `"python developer"` |
| `category` | UUID | `"abc-123-..."` |
| `location` | string | `"Remote"` |
| `job_type` | enum | `"full-time"`, `"part-time"`, `"contract"`, `"internship"`, `"freelance"` |
| `status` | enum | `"active"`, `"draft"`, `"closed"` |
| `min_salary` | number | `50000` |
| `max_salary` | number | `100000` |
| `is_featured` | boolean | `true` |
| `ordering` | string | `-created_at`, `salary_min`, `-salary_max`, `-views_count` |
| `page` | number | `1` |

---

### PAGE: Job Detail `/jobs/:id`

**Purpose:** Full job information + apply button.

**UI Components:**
- **Job header:**
  - Title (large)
  - Employer name + link
  - Location with icon
  - Job type badge
  - Posted date
  - Views count
  - "Featured" badge
- **Job body:**
  - Full description (rendered markdown/HTML)
  - Requirements section
  - Salary range (formatted: "$80,000 — $120,000")
  - Application deadline (with countdown if near)
- **Sidebar / sticky bar:**
  - **"Apply Now"** button (if `has_applied: false` and user role is `"user"`)
  - **"Already Applied"** badge (if `has_applied: true`)
  - **"Save Job"** bookmark button (heart icon)
  - **"Share"** button (share modal)
- **Similar Jobs** section at bottom

**API Calls on Load:**
```
GET /api/jobs/<uuid>/                                     → job details
GET /api/jobs/similar/?job_id=<uuid>&limit=5              → similar jobs
```

**Response (Job Detail):**
```json
{
    "id": "uuid",
    "title": "Senior Developer",
    "description": "Full description...",
    "requirements": "Requirements list...",
    "category": { "id": "uuid", "name": "Engineering", "full_path": "Tech > Engineering" },
    "employer": { "id": "uuid", "username": "techcorp", "email": "hr@tech.com" },
    "location": "San Francisco, CA",
    "job_type": "full-time",
    "salary_min": "80000.00",
    "salary_max": "120000.00",
    "status": "active",
    "application_deadline": "2026-03-15",
    "is_featured": true,
    "views_count": 235,
    "application_count": 15,
    "has_applied": false,
    "created_at": "2026-02-05T10:30:00Z"
}
```

**Save Job Action:**
```
POST /api/auth/profile/saved-jobs/save_job/
Body: { "job_id": "<uuid>", "notes": "Great opportunity" }
```

**Share Job Action:**
```
POST /api/jobs/share/
Body: { "job_id": "<uuid>", "method": "link" }  // or "email", "social"
```

---

### PAGE: Apply for Job `/jobs/:id/apply`

**Purpose:** Submit an application. (Can also be a modal on the Job Detail page)

**Who can access:** Only authenticated users with `role: "user"`

**UI Components:**
- Job title + company (read-only header)
- **Cover letter** textarea (required)
- **Resume upload** (file input — PDF, DOC, DOCX, max 5MB) (required)
- Optional: Screening questions (if employer set them up)
- Submit button

**API Call:**
```
POST /api/applications/
Content-Type: multipart/form-data

Form Data:
  job_id: "<uuid>"
  cover_letter: "I am writing to express my interest in..."
  resume: <file>
```

**Success (201):**
```json
{
    "id": "uuid",
    "job": { ... },
    "applicant": { "id": "uuid", "username": "johndoe" },
    "cover_letter": "...",
    "resume": "/media/resumes/2026/02/08/resume.pdf",
    "status": "pending",
    "applied_at": "2026-02-08T..."
}
```

**After Success:** Show success toast + redirect to `/applications` or `/jobs/<id>` with "Applied" badge.

**Errors:**
- `"You have already applied for this job."` → show message, disable button
- `"Application deadline has passed."` → show expired message
- `"Cannot apply to a closed job."` → show job closed message

---

### PAGE: Job Seeker Dashboard `/dashboard`

**Purpose:** Home page for logged-in job seekers. Overview of everything.

**UI Components:**
- **Welcome header:** "Welcome back, {first_name}!"
- **Profile completion bar** (e.g., 65% — "Complete your profile to stand out!")
- **Stats cards** (grid of 4):
  - Total Applications
  - Pending Applications
  - Accepted Applications
  - Saved Jobs
- **Recent Applications** table/list (last 5):
  - Job title | Company | Status badge | Applied date
  - Click → `/applications/<id>`
- **Recent Saved Jobs** list (last 5):
  - Job title | Company | Saved date
  - Click → `/jobs/<id>`
- **Recommended Jobs** section (personalized):
  - Job cards (3-4)

**API Calls on Load:**
```
GET /api/auth/profile/dashboard/       → dashboard data (all stats in one call)
GET /api/jobs/recommendations/?limit=4 → recommended jobs
GET /api/notifications/unread_count/   → notification badge count
```

**Dashboard Response:**
```json
{
    "statistics": {
        "total_applications": 12,
        "pending_applications": 3,
        "accepted_applications": 2,
        "rejected_applications": 5,
        "saved_jobs_count": 8,
        "applications_last_30_days": 4
    },
    "recent_applications": [ ... ],
    "recent_saved_jobs": [ ... ],
    "profile_completion": 65
}
```

---

### PAGE: My Applications `/applications`

**Purpose:** View all submitted applications.

**UI Components:**
- **Filter tabs:** All | Pending | Reviewed | Accepted | Rejected
- **Application list/table:**
  - Job title
  - Company
  - Applied date
  - Status badge (color-coded: pending=yellow, reviewed=blue, accepted=green, rejected=red)
  - Actions: View | Withdraw
- **Pagination**

**API Call:**
```
GET /api/applications/?status=pending&ordering=-applied_at&page=1
```

**Withdraw Application:**
```
POST /api/applications/<uuid>/withdraw/
Body: { "reason": "Found another opportunity" }
```

**Status Flow (what the user sees):**
```
pending → reviewed → accepted
                   → rejected

User can "Withdraw" from pending or reviewed status.
```

---

### PAGE: My Profile `/profile`

**Purpose:** View and edit full profile.

**UI Components — Tabbed layout or sections:**

#### Tab 1: Basic Info
- Profile picture (upload/change)
- First name, Last name
- Email (read-only or editable)
- Phone number
- Bio (textarea)

```
GET  /api/auth/profile/profile/       → full profile
PUT  /api/auth/me/update/             → update basic info
```

#### Tab 2: Skills
- List of skills with level badges (Beginner/Intermediate/Expert)
- "Add Skill" button → modal/form
- Delete/edit each skill

```
GET    /api/auth/profile/skills/              → list skills
POST   /api/auth/profile/skills/              → add skill
PUT    /api/auth/profile/skills/<id>/         → edit skill
DELETE /api/auth/profile/skills/<id>/         → delete skill

Body: { "name": "Python", "level": "expert", "years_of_experience": 5 }
```

#### Tab 3: Education
- List of education entries (institution, degree, dates)
- "Add Education" button

```
GET    /api/auth/profile/education/           → list education
POST   /api/auth/profile/education/           → add
PUT    /api/auth/profile/education/<id>/      → edit
DELETE /api/auth/profile/education/<id>/      → delete

Body: {
    "institution": "MIT",
    "degree": "B.Sc",
    "field_of_study": "Computer Science",
    "start_date": "2020-09-01",
    "end_date": "2024-06-01",
    "is_current": false,
    "description": "..."
}
```

#### Tab 4: Work History
- List of work history (company, position, dates)
- "Add Experience" button

```
GET    /api/auth/profile/work-history/
POST   /api/auth/profile/work-history/
PUT    /api/auth/profile/work-history/<id>/
DELETE /api/auth/profile/work-history/<id>/

Body: {
    "company": "Google",
    "position": "Software Engineer",
    "start_date": "2022-01-01",
    "end_date": null,
    "is_current": true,
    "description": "Working on...",
    "location": "Mountain View, CA"
}
```

#### Tab 5: Portfolio
- Project cards (title, description, URL, technologies)
- "Add Project" button

```
GET    /api/auth/profile/portfolio/
POST   /api/auth/profile/portfolio/
PUT    /api/auth/profile/portfolio/<id>/
DELETE /api/auth/profile/portfolio/<id>/

Body: {
    "title": "E-commerce Platform",
    "description": "Built a full-stack...",
    "url": "https://github.com/...",
    "technologies": "React, Django, PostgreSQL",
    "is_featured": true
}
```

#### Tab 6: Social Links
- List of social links (GitHub, LinkedIn, Twitter, etc.)
- "Add Link" button

```
GET    /api/auth/profile/social-links/
POST   /api/auth/profile/social-links/
PUT    /api/auth/profile/social-links/<id>/
DELETE /api/auth/profile/social-links/<id>/

Body: {
    "platform": "github",     // github, linkedin, twitter, website, other
    "url": "https://github.com/johndoe",
    "is_public": true
}
```

---

### PAGE: Saved Jobs `/saved-jobs`

**UI Components:**
- List/grid of saved job cards
- Each card: Job title, company, saved date, notes
- Actions: View Job | Remove from Saved
- Empty state: "No saved jobs yet. Browse jobs to save interesting ones."

```
GET    /api/auth/profile/saved-jobs/                → list saved jobs
DELETE /api/auth/profile/saved-jobs/<id>/unsave/     → remove
```

---

### PAGE: Settings `/settings`

**UI Components:**

#### Section: Change Password
```
POST /api/auth/change-password/
Body: {
    "old_password": "...",
    "new_password": "...",
    "new_password2": "..."
}
```

#### Section: Notification Preferences
- Toggle switches for:
  - Email job alerts
  - Application update emails
  - New jobs email
  - Newsletter
- Alert frequency dropdown (daily/weekly/monthly)
- Profile visibility (public/private)
- Show email / phone / location toggles

```
GET /api/auth/profile/preferences/        → current preferences
PUT /api/auth/profile/preferences/<id>/   → update preferences

Body: {
    "email_job_alerts": true,
    "email_application_updates": true,
    "email_new_jobs": false,
    "email_newsletter": false,
    "alert_frequency": "weekly",
    "profile_visibility": "public",
    "show_email": false,
    "show_phone": false
}
```

---

### PAGE: Notifications `/notifications`

**UI Components:**
- Notification list (latest first)
- Each notification: icon (based on type) + message + timestamp + read/unread indicator
- "Mark All as Read" button at top
- Filter by: All | Unread | Type (application, job, system)
- Click notification → navigate to relevant page

```
GET  /api/notifications/?is_read=false                → unread notifications
GET  /api/notifications/summary/                      → summary + recent 10
GET  /api/notifications/unread_count/                 → badge count
POST /api/notifications/<id>/mark_read/               → mark single as read
POST /api/notifications/mark_all_read/                → mark all as read
```

---

## EMPLOYER PAGES

---

### PAGE: Employer Dashboard `/employer/dashboard`

**Purpose:** Home page for employers. Overview of their hiring pipeline.

**UI Components:**
- **Stats cards** (2 rows):
  - Row 1 — Jobs: Active | Draft | Closed | Pending Approval
  - Row 2 — Applications: Total | Pending | Accepted | Rejected
- **Views stats**: Total Views | Unique Views
- **Recent Jobs** table (last 5): Title | Status | Applications | Views | Created
- **Recent Applications** table (last 5): Applicant | Job | Status | Date
- **Top Performing Jobs** (by views) — bar chart or list

**API Call (single call returns everything):**
```
GET /api/jobs/employer/dashboard/
```

**Response:**
```json
{
    "statistics": {
        "jobs": {
            "total": 15,
            "active": 8,
            "draft": 3,
            "closed": 4,
            "pending_approval": 1
        },
        "applications": {
            "total": 120,
            "pending": 25,
            "accepted": 30,
            "rejected": 50
        },
        "views": {
            "total": 5400,
            "unique": 3200
        }
    },
    "recent_jobs": [ ... ],
    "recent_applications": [ ... ],
    "top_jobs": [ ... ]
}
```

---

### PAGE: My Jobs (Employer) `/employer/jobs`

**Purpose:** Manage all posted jobs.

**UI Components:**
- **"Create New Job"** button (prominent, top-right)
- **Filter tabs:** All | Active | Draft | Closed
- **Jobs table:**
  - Title
  - Category
  - Status badge
  - Applications count
  - Views count
  - Created date
  - Actions: Edit | View | Close | Delete
- **Pagination**

**API Call:**
```
GET /api/jobs/?ordering=-created_at&page=1
```
(Employers automatically only see their own jobs)

---

### PAGE: Create/Edit Job `/employer/jobs/new` or `/employer/jobs/:id/edit`

**Purpose:** Post a new job or edit an existing one.

**UI Components — Multi-step form or single page form:**
- **Title** (text, required, max 200 chars)
- **Category** (dropdown — populated from categories API, required)
- **Description** (rich text editor, required)
- **Requirements** (rich text editor, required)
- **Location** (text + location autocomplete, required, max 100 chars)
- **Job Type** (dropdown: Full Time, Part Time, Contract, Internship, Freelance)
- **Salary Range** (two number inputs: min and max — optional)
- **Application Deadline** (date picker — must be future date, optional)
- **Status** (dropdown: Draft / Active)
- **Featured** toggle (checkbox)
- **Screening Questions** (add/manage — optional, see below)
- Submit: "Publish Job" or "Save as Draft"

**Create:**
```
POST /api/jobs/
Body: {
    "title": "Senior Python Developer",
    "category": "<category-uuid>",
    "description": "We are looking for...",
    "requirements": "5+ years Python, Django...",
    "location": "Remote",
    "job_type": "full-time",
    "salary_min": 80000,
    "salary_max": 120000,
    "application_deadline": "2026-03-15",
    "status": "active",
    "is_featured": false
}
```

**Update:**
```
PATCH /api/jobs/<uuid>/
Body: { "title": "Updated Title", "status": "closed" }
```

**Delete:**
```
DELETE /api/jobs/<uuid>/
```

**Load categories for dropdown:**
```
GET /api/categories/
```

---

### PAGE: Job Applications (Employer) `/employer/jobs/:id/applications`

**Purpose:** View and manage applications for a specific job.

**UI Components:**
- **Job header** (title, status, deadline)
- **Pipeline view** (Kanban-style columns):
  ```
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │  Pending  │  │ Reviewed │  │ Accepted │  │ Rejected │
  │  (25)     │  │  (10)    │  │  (5)     │  │  (12)    │
  │           │  │          │  │          │  │          │
  │ Card      │  │ Card     │  │ Card     │  │ Card     │
  │ Card      │  │ Card     │  │          │  │ Card     │
  │ Card      │  │          │  │          │  │          │
  └──────────┘  └──────────┘  └──────────┘  └──────────┘
  ```
- **Or table view** with:
  - Applicant name + email
  - Applied date
  - Status badge
  - Resume download link
  - Cover letter (expandable)
  - Actions: Review | Accept | Reject
- **Application detail modal/page:**
  - Full cover letter
  - Download resume
  - Applicant profile link
  - Status change dropdown
  - Notes section (add notes)
  - Score applicant
  - Schedule interview

**API Calls:**
```
GET  /api/applications/?job=<uuid>&status=pending    → filter applications
```

**Change Application Status:**
```
PATCH /api/applications/<uuid>/
Body: { "status": "reviewed" }
```

**Valid status transitions:**
```
pending  →  reviewed  |  accepted  |  rejected
reviewed →  accepted  |  rejected
accepted →  (final - no further changes)
rejected →  (final - no further changes)
```

**Add Note to Application:**
```
POST /api/applications/notes/
Body: {
    "application": "<application-uuid>",
    "content": "Strong candidate, good technical skills",
    "is_private": true
}
```

**Score Application:**
```
POST /api/applications/scores/
Body: {
    "application": "<application-uuid>",
    "technical_score": 8,
    "communication_score": 9,
    "experience_score": 7,
    "overall_score": 8,
    "comments": "Excellent problem solver"
}
```

**Schedule Interview:**
```
POST /api/applications/interviews/
Body: {
    "application": "<application-uuid>",
    "interview_type": "video",
    "scheduled_at": "2026-02-15T14:00:00Z",
    "duration_minutes": 60,
    "location": "https://zoom.us/j/...",
    "notes": "Technical interview - round 1"
}
```

**Download Resume:**
```
GET /health/files/resumes/<application-uuid>/
```

---

### PAGE: Job Analytics `/employer/jobs/:id/analytics`

**Purpose:** View performance metrics for a specific job.

**UI Components:**
- **Metrics cards:** Total Views | Unique Views | Applications | Shares
- **Views chart** (line chart — views over time)
- **Application sources** (pie chart — where applicants came from)
- **Conversion rate** (views → applications %)

```
GET /api/jobs/<uuid>/analytics/
```

---

### PAGE: Screening Questions `/employer/jobs/:id/screening`

**Purpose:** Set up questions applicants must answer.

**UI Components:**
- List of existing questions (drag to reorder)
- "Add Question" form:
  - Question text
  - Question type (text, multiple_choice, yes_no)
  - Is required toggle
  - Order number

```
GET  /api/applications/screening-questions/?job_id=<uuid>
POST /api/applications/screening-questions/
Body: {
    "job": "<job-uuid>",
    "question_text": "Do you have experience with Django?",
    "question_type": "yes_no",
    "is_required": true,
    "order": 1
}
```

---

### PAGE: Export Data `/employer/export`

**Purpose:** Download data in CSV or JSON.

**UI Components:**
- Export cards:
  - "Export Jobs" — dropdown (CSV/JSON) + download button
  - "Export Applications" — dropdown + optional job filter + download button

```
GET /api/export/jobs/?format=csv                    → downloads CSV
GET /api/export/jobs/?format=json                   → downloads JSON
GET /api/export/applications/?format=csv&job=<uuid> → filtered export
```

---

## ADMIN PAGES

---

### PAGE: Admin Dashboard `/admin-panel/dashboard`

**Purpose:** Platform-wide overview.

**UI Components:**
- **Platform stats cards:**
  - Total Users | Employers | Job Seekers | Active Today
  - Total Jobs | Active Jobs | Pending Approval
  - Total Applications | Pending Review
- **Charts:**
  - New users over time (line chart)
  - Jobs posted over time (bar chart)
  - Applications by status (donut chart)
- **Quick actions:** Approve pending jobs, Review flagged users

```
GET /health/statistics/              → overall platform stats
GET /health/statistics/users/        → user breakdown
GET /health/statistics/jobs/         → job breakdown
GET /health/statistics/applications/ → application breakdown
```

---

### PAGE: User Management `/admin-panel/users`

**Purpose:** View, edit, deactivate, delete users.

**UI Components:**
- **Search bar** (search by username, email, name)
- **Filter:** Role dropdown (All, Admin, Employer, User) + Active toggle
- **Users table:**
  - Avatar | Username | Email | Full Name | Role badge | Active? | Joined Date | Actions
  - Actions: Edit | Deactivate | Delete
- **User detail modal/page:**
  - Edit role, active status
  - View user's activity

```
GET    /api/auth/users/?role=employer&search=john&is_active=true  → list users
GET    /api/auth/users/<uuid>/                                     → user detail
PUT    /api/auth/users/<uuid>/                                     → update user
DELETE /api/auth/users/<uuid>/                                     → delete user
GET    /health/statistics/user-activity/?user_id=<uuid>&days=30   → user activity
```

---

### PAGE: Audit Logs `/admin-panel/audit`

**Purpose:** View all system activity.

**UI Components:**
- **Filters:** User | Action type | Content type | Date range
- **Audit logs table:**
  - Timestamp | User | Action | Object Type | Object ID | Details
- **Change history** (what changed in each record):
  - Field name | Old value | New value | Changed by | Date

```
GET /api/audit/logs/?action=create&content_type=job&date_from=2026-02-01
GET /api/audit/history/?content_type=job&object_id=<uuid>
GET /api/audit/object-history/?content_type=job&object_id=<uuid>
```

---

### PAGE: Search Analytics `/admin-panel/search`

**Purpose:** View what users are searching for.

**UI Components:**
- Popular search terms (word cloud or ranked list)
- Search volume over time (line chart)
- Zero-result searches

```
GET /api/search/statistics/?days=30
GET /api/search/popular-terms/?limit=20&days=30
```

---

## 5. Global Components

### 5.1 — Navbar

**For all users:**
- Logo (→ `/`)
- "Jobs" (→ `/jobs`)

**For unauthenticated:**
- "Login" button (→ `/login`)
- "Register" button (→ `/register`)

**For Job Seeker (`user`):**
- "Dashboard" (→ `/dashboard`)
- "My Applications" (→ `/applications`)
- Notification bell with unread count badge
- User avatar dropdown:
  - Profile
  - Saved Jobs
  - Settings
  - Logout

**For Employer (`employer`):**
- "Dashboard" (→ `/employer/dashboard`)
- "My Jobs" (→ `/employer/jobs`)
- "Post Job" button (→ `/employer/jobs/new`)
- Notification bell
- User avatar dropdown:
  - Profile
  - Export
  - Settings
  - Logout

**For Admin (`admin`):**
- "Dashboard" (→ `/admin-panel/dashboard`)
- "Users" (→ `/admin-panel/users`)
- "Jobs" (→ `/jobs`)
- Notification bell
- User avatar dropdown:
  - Statistics
  - Audit Logs
  - Export
  - Settings
  - Logout

### 5.2 — Notification Bell (Global)

Always visible in the navbar for authenticated users.

```
GET /api/notifications/unread_count/    → poll every 30 seconds or use it on page load
```

Shows number badge. Click → dropdown with recent 5 notifications. "View All" → `/notifications`

### 5.3 — Search Bar (Global)

Used on landing page and job listing. Should have autocomplete.

```
GET /api/search/autocomplete/?q=pyth&limit=5    → as user types (debounce 300ms)
```

Response:
```json
{
    "query": "pyth",
    "suggestions": ["python", "python developer", "python django"],
    "count": 3
}
```

### 5.4 — Toast Notifications

Show success/error toasts for:
- Login success / failure
- Registration success
- Application submitted / failed
- Job created / updated / deleted
- Password changed
- Any API error

---

## 6. API Quick Reference

### Auth Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register/` | No | Register new user |
| POST | `/api/auth/login/` | No | Login, get tokens |
| POST | `/api/auth/refresh/` | No | Refresh access token |
| GET | `/api/auth/me/` | Yes | Get current user |
| PUT/PATCH | `/api/auth/me/update/` | Yes | Update current user |
| POST | `/api/auth/change-password/` | Yes | Change password |
| POST | `/api/auth/password-reset/` | No | Request password reset |
| POST | `/api/auth/password-reset/confirm/` | No | Confirm password reset |
| GET | `/api/auth/users/` | Admin | List all users |
| GET/PUT/DELETE | `/api/auth/users/<uuid>/` | Admin | Manage user |

### Profile Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/auth/profile/profile/` | Yes | Full profile |
| GET | `/api/auth/profile/dashboard/` | Yes | User dashboard |
| CRUD | `/api/auth/profile/skills/` | Yes | Manage skills |
| CRUD | `/api/auth/profile/education/` | Yes | Manage education |
| CRUD | `/api/auth/profile/work-history/` | Yes | Manage work history |
| CRUD | `/api/auth/profile/portfolio/` | Yes | Manage portfolio |
| CRUD | `/api/auth/profile/social-links/` | Yes | Manage social links |
| CRUD | `/api/auth/profile/preferences/` | Yes | Notification prefs |
| CRUD | `/api/auth/profile/saved-jobs/` | Yes | Manage saved jobs |

### Job Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/jobs/` | No | List jobs (with filters) |
| POST | `/api/jobs/` | Employer/Admin | Create job |
| GET | `/api/jobs/<uuid>/` | No | Job detail |
| PUT/PATCH | `/api/jobs/<uuid>/` | Owner/Admin | Update job |
| DELETE | `/api/jobs/<uuid>/` | Owner/Admin | Delete job |
| GET | `/api/jobs/featured/` | No | Featured jobs |
| GET | `/api/categories/` | No | List categories |
| POST | `/api/categories/` | Admin | Create category |

### Application Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/applications/` | Yes | List (role-filtered) |
| POST | `/api/applications/` | User only | Apply for job |
| GET | `/api/applications/<uuid>/` | Yes | Application detail |
| PATCH | `/api/applications/<uuid>/` | Employer/Admin | Update status |
| POST | `/api/applications/<uuid>/withdraw/` | User | Withdraw application |

### Job Enhancements
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/jobs/share/` | No | Share a job |
| GET | `/api/jobs/similar/?job_id=<uuid>` | No | Similar jobs |
| GET | `/api/jobs/recommendations/` | Yes | Recommended jobs |
| GET | `/api/jobs/<uuid>/analytics/` | Employer/Admin | Job analytics |
| GET | `/api/jobs/employer/dashboard/` | Employer/Admin | Employer dashboard |

### Application Enhancements
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| CRUD | `/api/applications/notes/` | Employer/Admin | Application notes |
| GET | `/api/applications/status-history/` | Yes | Status change history |
| CRUD | `/api/applications/screening-questions/` | Employer/Admin | Screening questions |
| CRUD | `/api/applications/screening-answers/` | Yes | Screening answers |
| CRUD | `/api/applications/stages/` | Employer/Admin | Application stages |
| CRUD | `/api/applications/interviews/` | Yes | Interviews |
| CRUD | `/api/applications/scores/` | Employer/Admin | Application scores |
| CRUD | `/api/applications/templates/` | Employer/Admin | App templates |

### Search
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/search/autocomplete/?q=...` | No | Search autocomplete |
| GET | `/api/search/suggestions/?q=...` | No | Similar searches |
| GET | `/api/search/history/` | Yes | User search history |
| GET | `/api/search/popular-terms/` | No | Popular searches |
| GET | `/api/search/statistics/` | Admin | Search analytics |
| CRUD | `/api/search/saved-searches/` | Yes | Saved searches |
| CRUD | `/api/search/search-alerts/` | Yes | Search alerts |

### Notifications
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/notifications/` | Yes | List notifications |
| GET | `/api/notifications/summary/` | Yes | Summary + recent |
| GET | `/api/notifications/unread_count/` | Yes | Unread count |
| POST | `/api/notifications/<id>/mark_read/` | Yes | Mark one read |
| POST | `/api/notifications/mark_all_read/` | Yes | Mark all read |
| CRUD | `/api/notifications/preferences/` | Yes | Notification prefs |

### Export & Audit (Admin/Employer)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/export/jobs/?format=csv` | Employer/Admin | Export jobs |
| GET | `/api/export/applications/?format=csv` | Employer/Admin | Export applications |
| GET | `/api/export/users/?format=csv` | Admin | Export users |
| GET | `/api/audit/logs/` | Admin | Audit logs |
| GET | `/api/audit/history/` | Admin | Change history |
| GET | `/api/audit/object-history/` | Admin | Object history |

### Health & Stats
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health/` | No | Health check |
| GET | `/health/liveness/` | No | Liveness check |
| GET | `/health/readiness/` | No | Readiness check |
| GET | `/health/statistics/` | Admin | Platform stats |
| GET | `/health/statistics/users/` | Admin | User stats |
| GET | `/health/statistics/jobs/` | Admin | Job stats |
| GET | `/health/statistics/applications/` | Admin | App stats |
| GET | `/health/statistics/user-activity/` | Admin | User activity |

---

## 7. Error Handling

### Standard Error Response Format

```json
{
    "field_name": ["Error message 1", "Error message 2"],
    "non_field_errors": ["General error message"]
}
```

Or for single errors:
```json
{
    "error": "Descriptive error message"
}
```

### HTTP Status Codes

| Code | Meaning | Frontend Action |
|------|---------|----------------|
| 200 | Success | Show data |
| 201 | Created | Show success toast + redirect |
| 204 | Deleted | Show success toast + redirect |
| 400 | Validation error | Show field-level errors under inputs |
| 401 | Unauthorized | Redirect to `/login` (try refresh first) |
| 403 | Forbidden | Show "access denied" message |
| 404 | Not found | Show 404 page |
| 429 | Rate limited | Show "too many requests, try again later" |
| 500 | Server error | Show generic error toast |

### Token Refresh Flow

```
1. Make API call
2. If 401 response:
   a. Call POST /api/auth/refresh/ with refresh token
   b. If 200 → store new access token, retry original request
   c. If 400/401 → refresh token expired → clear tokens → redirect to /login
```

---

## Suggested Tech Stack

| Layer | Recommendation |
|-------|---------------|
| Framework | Next.js 14+ (App Router) or React + Vite |
| State Management | Zustand or React Context + useReducer |
| HTTP Client | Axios with interceptors |
| Forms | React Hook Form + Zod validation |
| UI Library | shadcn/ui or Ant Design or Chakra UI |
| Tables | TanStack Table |
| Charts | Recharts or Chart.js |
| Rich Text | TipTap or React Quill |
| File Upload | react-dropzone |
| Date Picker | react-day-picker or date-fns |
| Notifications | react-hot-toast or sonner |
| Routing | Next.js App Router or React Router v6 |

---

## Suggested Folder Structure (React/Next.js)

```
src/
├── app/ (or pages/)
│   ├── (public)/              # Public routes
│   │   ├── page.tsx           # Landing page
│   │   ├── login/
│   │   ├── register/
│   │   ├── forgot-password/
│   │   └── jobs/
│   │       ├── page.tsx       # Job listing
│   │       └── [id]/
│   │           └── page.tsx   # Job detail
│   │
│   ├── (user)/                # Job seeker routes (role: "user")
│   │   ├── dashboard/
│   │   ├── applications/
│   │   ├── profile/
│   │   ├── saved-jobs/
│   │   ├── notifications/
│   │   └── settings/
│   │
│   ├── (employer)/            # Employer routes (role: "employer")
│   │   ├── employer/
│   │   │   ├── dashboard/
│   │   │   ├── jobs/
│   │   │   │   ├── page.tsx       # My jobs list
│   │   │   │   ├── new/           # Create job
│   │   │   │   └── [id]/
│   │   │   │       ├── edit/      # Edit job
│   │   │   │       ├── applications/ # Manage applicants
│   │   │   │       ├── analytics/ # Job analytics
│   │   │   │       └── screening/ # Screening questions
│   │   │   └── export/
│   │
│   └── (admin)/               # Admin routes (role: "admin")
│       └── admin-panel/
│           ├── dashboard/
│           ├── users/
│           ├── audit/
│           └── search/
│
├── components/
│   ├── ui/                    # Base UI (buttons, inputs, cards, badges)
│   ├── layout/
│   │   ├── Navbar.tsx
│   │   ├── Sidebar.tsx
│   │   ├── Footer.tsx
│   │   └── AuthGuard.tsx      # Route protection by role
│   ├── jobs/
│   │   ├── JobCard.tsx
│   │   ├── JobFilters.tsx
│   │   ├── JobForm.tsx
│   │   └── JobDetail.tsx
│   ├── applications/
│   │   ├── ApplicationCard.tsx
│   │   ├── ApplicationPipeline.tsx  # Kanban view
│   │   ├── ApplicationForm.tsx
│   │   └── StatusBadge.tsx
│   ├── profile/
│   │   ├── SkillForm.tsx
│   │   ├── EducationForm.tsx
│   │   ├── WorkHistoryForm.tsx
│   │   └── ProfileCompletion.tsx
│   └── common/
│       ├── SearchBar.tsx
│       ├── NotificationBell.tsx
│       ├── Pagination.tsx
│       ├── FileUpload.tsx
│       └── StatCard.tsx
│
├── lib/
│   ├── api.ts                 # Axios instance + interceptors
│   ├── auth.ts                # Token management
│   └── utils.ts               # Formatters, helpers
│
├── hooks/
│   ├── useAuth.ts             # Auth context hook
│   ├── useJobs.ts             # Job data hooks
│   ├── useApplications.ts
│   └── useNotifications.ts
│
├── types/
│   ├── user.ts                # User, UserProfile types
│   ├── job.ts                 # Job, Category types
│   ├── application.ts         # Application types
│   └── notification.ts
│
└── store/
    ├── authStore.ts           # Auth state (Zustand)
    └── notificationStore.ts
```

---

**Questions? Hit the Swagger docs:** `https://alx-nexus-a5a0e2db51ca.herokuapp.com/api/docs/`
