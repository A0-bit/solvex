# Implementation Plan — Garbage Reporting & Management System

## Phase 1: Project Scaffolding

- [-] 1.1 Initialize Django project
  - Create `backend/` directory and virtual environment
  - Install core packages: `django`, `djangorestframework`, `djangorestframework-simplejwt`, `django-cors-headers`, `django-jazzmin`, `psycopg2-binary`, `python-decouple`, `Pillow`, `shapely`, `django-storages`, `boto3`, `celery`, `redis`
  - Run `django-admin startproject config .` inside `backend/`
  - Split settings into `config/settings/base.py`, `development.py`, `production.py`
  - Configure `DJANGO_SETTINGS_MODULE` via `.env`
  - _Requirements: 1.1_

- [~] 1.2 Create Django apps
  - `python manage.py startapp accounts`
  - `python manage.py startapp areas`
  - `python manage.py startapp reports`
  - `python manage.py startapp cleaners`
  - `python manage.py startapp assignments`
  - `python manage.py startapp stats`
  - Register all apps in `INSTALLED_APPS` (jazzmin first, then django.contrib.admin)
  - _Requirements: 1.2_


- [~] 1.3 Configure PostgreSQL and base settings
  - Set `DATABASES` using `dj-database-url` or `python-decouple` in `base.py`
  - Configure `MEDIA_ROOT`, `MEDIA_URL` for local dev
  - Configure `STATIC_ROOT`, `STATICFILES_DIRS`
  - Set `CORS_ALLOWED_ORIGINS` and `REST_FRAMEWORK` defaults
  - Add `SimpleJWT` token settings (15 min access, 7 day refresh)
  - _Requirements: 1.3_

- [~] 1.4 Initialize Next.js frontend
  - Run `npx create-next-app@latest frontend --typescript --tailwind --app --src-dir`
  - Install packages: `axios`, `zustand`, `react-leaflet`, `leaflet`, `@types/leaflet`, `shadcn-ui` (or manual Radix/Tailwind components)
  - Create directory structure as per design section 4: `(auth)`, `(user)`, `(supervisor)` route groups
  - Create `src/lib/`, `src/components/`, `src/store/`, `src/types/` directories
  - Configure `next.config.ts` with API base URL env variable
  - _Requirements: 1.4_

- [~] 1.5 Create Docker Compose development environment
  - Write `docker-compose.yml` with services: `db` (postgres:16), `redis` (redis:7-alpine), `api`, `frontend`
  - Write `backend/Dockerfile` and `frontend/Dockerfile`
  - Create `.env.example` with all required environment variable keys
  - Verify `docker compose up` brings all services online
  - _Requirements: 1.5_


---

## Phase 2: Django Models & Database Schema

- [~] 2.1 Implement custom User model
  - In `accounts/models.py`, extend `AbstractUser` with `role`, `phone`, `avatar`, `created_at`, `updated_at`
  - Define `Role` TextChoices: `superadmin`, `supervisor`, `user`
  - Set `db_table = "auth_user_extended"`
  - Point `AUTH_USER_MODEL = "accounts.User"` in settings
  - _Requirements: 2.1_

- [~] 2.2 Implement Area model
  - In `areas/models.py`, create `Area` with `name`, `boundary` (JSONField), `supervisor` (OneToOneField to User, limit_choices_to supervisor role), `created_at`
  - _Requirements: 2.2_

- [~] 2.3 Implement Cleaner model
  - In `cleaners/models.py`, create `Cleaner` with `user` (OneToOneField), `area` (ForeignKey to Area), `is_active`, `created_at`
  - _Requirements: 2.3_

- [~] 2.4 Implement Report model
  - In `reports/models.py`, create `Report` with all fields from design: `reporter`, `area`, `title`, `description`, `latitude`, `longitude`, `before_photo`, `after_photo`, `status`, `created_at`, `updated_at`, `resolved_at`
  - Define `Status` TextChoices: `pending`, `assigned`, `in_progress`, `resolved`, `rejected`
  - Add `Meta` ordering and indexes on `status` and `(area, status)`
  - _Requirements: 2.4_

- [~] 2.5 Implement Assignment model
  - In `assignments/models.py`, create `Assignment` with `report` (OneToOneField), `cleaner`, `assigned_by`, `notes`, `assigned_at`, `completed_at`
  - _Requirements: 2.5_

- [~] 2.6 Run initial migrations
  - `python manage.py makemigrations accounts areas cleaners reports assignments`
  - `python manage.py migrate`
  - Verify schema in PostgreSQL (all tables present, indexes applied)
  - _Requirements: 2.6_


---

## Phase 3: Authentication System (JWT)

- [~] 3.1 Implement permission classes
  - In `accounts/permissions.py`, implement `IsSuperAdmin`, `IsSupervisor`, `IsReporter`, `IsOwnerOrSupervisorOrAdmin` as per design section 5
  - `IsOwnerOrSupervisorOrAdmin.has_object_permission` checks role and area ownership
  - _Requirements: 3.1_

- [~] 3.2 Implement auth serializers
  - `RegisterSerializer`: validates username, email, password, role; creates user via `User.objects.create_user()`
  - `LoginSerializer`: validates credentials, returns tokens via SimpleJWT
  - `UserProfileSerializer`: read/update own profile (phone, avatar, excluding role)
  - `ChangePasswordSerializer`: validates old password, sets new password
  - _Requirements: 3.2_

- [~] 3.3 Implement auth views
  - `RegisterView` (CreateAPIView, AllowAny)
  - `LoginView` (wraps `TokenObtainPairView`, returns access + refresh)
  - `LogoutView` (BlacklistRefreshToken, IsAuthenticated)
  - `MeView` (RetrieveUpdateAPIView, IsAuthenticated — GET/PATCH own profile)
  - `ChangePasswordView` (UpdateAPIView, IsAuthenticated)
  - _Requirements: 3.3_

- [~] 3.4 Configure auth URLs
  - In `accounts/urls.py` wire all auth views
  - In `config/urls.py` include at `api/v1/auth/`
  - Also include `api/v1/auth/token/refresh/` from SimpleJWT
  - _Requirements: 3.4_

- [~] 3.5 Configure JWT settings
  - In `base.py` set `ACCESS_TOKEN_LIFETIME = timedelta(minutes=15)`, `REFRESH_TOKEN_LIFETIME = timedelta(days=7)`
  - Enable `ROTATE_REFRESH_TOKENS = True` and `BLACKLIST_AFTER_ROTATION = True`
  - Add `rest_framework_simplejwt.token_blacklist` to `INSTALLED_APPS`
  - _Requirements: 3.5_


---

## Phase 4: Area Routing Utility & Reports Core

- [~] 4.1 Implement area resolver utility
  - In `reports/utils.py`, implement `resolve_area(lat, lng) -> Area | None` using `shapely.geometry.Point` and `Polygon`
  - Iterate `Area.objects.exclude(boundary=[])` and check if point falls within each polygon
  - Return first matching area or `None`
  - _Requirements: 4.1_

- [~] 4.2 Implement Report serializers
  - `ReportCreateSerializer`: includes `before_photo` ImageField with extension validator (jpg, jpeg, png, webp) and max 10 MB validation; calls `resolve_area()` in `create()`; sets `reporter` from `request.user`
  - `ReportDetailSerializer`: full read-only representation including nested reporter, area, assignment
  - `ReportStatusSerializer`: only `status` field, enforces transition rules
  - `AfterPhotoSerializer`: only `after_photo` field with same validation as before_photo
  - `strip_exif()` called on image save (design section 12)
  - _Requirements: 4.2_

- [~] 4.3 Implement Report views
  - `UserReportListCreateView` (GET list own reports, POST create) — `IsReporter`
  - `ReportDetailView` (GET single report) — `IsOwnerOrSupervisorOrAdmin`
  - `AfterPhotoUploadView` (PATCH `reports/{id}/after-photo/`) — `IsSupervisor`
  - `SupervisorAreaReportsView` (GET all reports in supervisor's area) — `IsSupervisor`, filter by `request.user.managed_area`
  - `SuperAdminAllReportsView` (GET all reports) — `IsSuperAdmin`
  - `ReportStatusUpdateView` (PATCH `reports/{id}/status/`) — `IsSupervisor | IsSuperAdmin`, enforces state machine rules
  - _Requirements: 4.3_

- [~] 4.4 Wire report URLs
  - In `reports/urls.py` map all endpoints as per design table in section 3
  - Include in `config/urls.py` at `api/v1/reports/`
  - _Requirements: 4.4_


---

## Phase 5: Areas, Cleaners, Assignments APIs

- [~] 5.1 Implement Area serializers and views
  - `AreaSerializer`: all fields including `boundary` JSONField
  - `AreaListCreateView` (GET/POST) — `IsSuperAdmin`
  - `AreaDetailView` (GET/PATCH/DELETE) — `IsSuperAdmin` for write, `IsSuperAdmin | IsSupervisor` for read
  - Wire in `areas/urls.py` and include at `api/v1/areas/`
  - _Requirements: 5.1_

- [~] 5.2 Implement Cleaner serializers and views
  - `CleanerSerializer`: nested user representation
  - `CleanerListCreateView` (GET/POST) — `IsSupervisor | IsSuperAdmin`; supervisor list filtered to own area
  - `CleanerDetailView` (GET/PATCH/DELETE) — `IsSupervisor | IsSuperAdmin`; DELETE sets `is_active=False`
  - Wire in `cleaners/urls.py` and include at `api/v1/cleaners/`
  - _Requirements: 5.2_

- [~] 5.3 Implement Assignment serializers and views
  - `AssignmentSerializer`: includes report, cleaner, assigned_by, notes, timestamps
  - `AssignmentCreateView` (POST) — `IsSupervisor`; sets `assigned_by = request.user`; transitions report to `assigned`
  - `AssignmentDetailView` (GET/PATCH) — `IsSupervisor | IsSuperAdmin`
  - Wire in `assignments/urls.py` and include at `api/v1/assignments/`
  - _Requirements: 5.3_

- [~] 5.4 Implement Users API (SuperAdmin)
  - `UserListView` (GET) — `IsSuperAdmin`
  - `UserDetailView` (GET/PATCH/DELETE) — `IsSuperAdmin`; DELETE sets `is_active=False`; PATCH allows changing role
  - Wire in `accounts/urls.py` at `api/v1/users/`
  - _Requirements: 5.4_

- [~] 5.5 Implement Dashboard Stats views
  - `SuperAdminStatsView`: count reports by status, user counts, areas count, trend data
  - `SupervisorStatsView`: counts scoped to `request.user.managed_area`
  - `UserStatsView`: counts scoped to `request.user`
  - Wire in `stats/urls.py` and include at `api/v1/stats/`
  - _Requirements: 5.5_


---

## Phase 6: Jazzmin Admin Configuration

- [~] 6.1 Configure Jazzmin settings
  - In `config/settings/base.py`, add `jazzmin` before `django.contrib.admin` in `INSTALLED_APPS`
  - Add `JAZZMIN_SETTINGS` dict with `site_title`, `site_header`, `site_brand`, icons per model (as per design section 8)
  - Set `JAZZMIN_UI_TWEAKS` for color scheme and sidebar style
  - _Requirements: 6.1_

- [~] 6.2 Register models in Django admin
  - `accounts/admin.py`: register `User` with `UserAdmin`, display `role`, `phone`, `is_active` in list_display; add role filter
  - `areas/admin.py`: register `Area` with `list_display = ["name", "supervisor"]`; inline for cleaners
  - `reports/admin.py`: register `Report` with `list_display = ["id", "title", "status", "reporter", "area", "created_at"]`; add status filter and date_hierarchy; readonly `before_photo`, `after_photo` with image previews
  - `cleaners/admin.py`: register `Cleaner` with supervisor and area display
  - `assignments/admin.py`: register `Assignment` with report, cleaner, assigned_by display
  - _Requirements: 6.2_

- [~] 6.3 Create superuser and verify admin
  - `python manage.py createsuperuser`
  - Navigate to `/admin/` and confirm Jazzmin theme, all models registered, icons visible
  - _Requirements: 6.3_


---

## Phase 7: Media & Image Storage

- [~] 7.1 Configure local media storage (development)
  - In `development.py` set `MEDIA_ROOT = BASE_DIR / "media"` and `MEDIA_URL = "/media/"`
  - Serve media files via `urlpatterns += static(settings.MEDIA_URL, ...)` in `config/urls.py`
  - _Requirements: 7.1_

- [~] 7.2 Configure AWS S3 storage (production)
  - In `production.py` set `DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"` with all S3 env vars (as per design section 7)
  - Set `AWS_DEFAULT_ACL = "private"`, `AWS_S3_FILE_OVERWRITE = False`, `AWS_S3_SIGNATURE_VERSION = "s3v4"`
  - _Requirements: 7.2_

- [~] 7.3 Implement EXIF stripping
  - In `reports/utils.py`, add `strip_exif(image_file) -> bytes` using Pillow (as per design section 12)
  - Call `strip_exif()` in `ReportCreateSerializer.validate_before_photo()` and `AfterPhotoSerializer.validate_after_photo()` before saving
  - Also apply to avatar uploads in `UserProfileSerializer`
  - _Requirements: 7.3_

- [~] 7.4 Test image upload end-to-end
  - POST a multipart form to `api/v1/reports/` with an image file
  - Verify image saved to `media/reports/before/` locally
  - Verify EXIF data is stripped from saved image
  - Verify file extension and size validation rejects invalid uploads
  - _Requirements: 7.4_


---

## Phase 8: Next.js Foundation & Auth

- [~] 8.1 Set up TypeScript types
  - Create `src/types/user.ts`: `User`, `Role`, `AuthTokens` interfaces
  - Create `src/types/report.ts`: `Report`, `ReportStatus`, `CreateReportPayload` interfaces
  - Create `src/types/area.ts`: `Area` interface with boundary array type
  - Create `src/types/assignment.ts`: `Assignment` interface
  - _Requirements: 8.1_

- [~] 8.2 Set up Axios API client with JWT interceptors
  - In `src/lib/api/client.ts`, create Axios instance with `baseURL = process.env.NEXT_PUBLIC_API_URL`
  - Add request interceptor: attach `Authorization: Bearer <access_token>` from store
  - Add response interceptor: on 401, attempt token refresh via `POST /auth/token/refresh/`, retry original request; on refresh failure, clear tokens and redirect to `/login`
  - _Requirements: 8.2_

- [~] 8.3 Implement Zustand auth store
  - In `src/store/authStore.ts`, store `user: User | null`, `accessToken`, `refreshToken`
  - Actions: `setTokens()`, `setUser()`, `logout()` (clears all state)
  - Persist tokens to `localStorage` using Zustand persist middleware
  - _Requirements: 8.3_

- [~] 8.4 Implement useAuth hook and withRole HOC
  - In `src/lib/auth/useAuth.ts`, expose `user`, `loading`, `login()`, `logout()` from store
  - `login()` calls `POST /auth/login/`, stores tokens, fetches `/auth/me/`, sets user
  - In `src/lib/auth/withRole.tsx`, implement HOC that redirects unauthenticated users and users with wrong role to `/login` (as per design section 5)
  - _Requirements: 8.4_

- [~] 8.5 Build login and register pages
  - `src/app/(auth)/login/page.tsx`: form with username/password fields, calls `useAuth().login()`, shows error on failure, redirects to role-appropriate dashboard on success
  - `src/app/(auth)/register/page.tsx`: form with username, email, password, phone; calls `POST /auth/register/`; on success redirects to `/login`
  - _Requirements: 8.5_


---

## Phase 9: Shared UI Components

- [~] 9.1 Build primitive UI components
  - `src/components/ui/Button.tsx`: variants (primary, secondary, danger, ghost), loading state with spinner
  - `src/components/ui/Input.tsx`: labeled input with error message slot
  - `src/components/ui/Badge.tsx`: colored badge mapped from ReportStatus values
  - `src/components/ui/Modal.tsx`: accessible dialog using `dialog` element or Radix Dialog, with overlay and close button
  - _Requirements: 9.1_

- [~] 9.2 Build ReportStatusBadge component
  - In `src/components/reports/ReportStatusBadge.tsx`, map each status string to a color class (pending=yellow, assigned=blue, in_progress=orange, resolved=green, rejected=red)
  - Use `src/lib/utils/statusColor.ts` for the mapping logic
  - _Requirements: 9.2_

- [~] 9.3 Build layout components
  - `src/components/layout/Navbar.tsx`: top bar with app title, user avatar, logout button
  - `src/components/layout/Sidebar.tsx`: vertical nav for supervisor/admin with route links
  - `src/components/layout/BottomNav.tsx`: mobile-first bottom tab bar for user dashboard (Dashboard, Reports, Profile)
  - _Requirements: 9.3_

- [~] 9.4 Build User layout shell
  - `src/app/(user)/layout.tsx`: wraps all user pages with `withRole(["user"])`, renders `Navbar` + `BottomNav`, applies mobile-centric max-width container
  - _Requirements: 9.4_

- [~] 9.5 Build Supervisor layout shell
  - `src/app/(supervisor)/layout.tsx`: wraps all supervisor pages with `withRole(["supervisor"])`, renders `Navbar` + `Sidebar`
  - _Requirements: 9.5_


---

## Phase 10: Map & Location Components

- [~] 10.1 Build LocationPicker component
  - In `src/components/map/LocationPicker.tsx`, implement dynamic import of `react-leaflet` (SSR disabled)
  - Props: `onChange(lat, lng)`, optional `initialPosition`
  - Render `MapContainer` with OpenStreetMap `TileLayer`
  - `DraggableMarker` sub-component: places marker on map click, supports drag; calls `onChange` on both click and dragend (as per design section 6)
  - Default center: `[23.8103, 90.4125]` (Dhaka) if no initialPosition
  - _Requirements: 10.1_

- [~] 10.2 Build ReportMapView component (read-only)
  - In `src/components/map/ReportMapView.tsx`, render a non-interactive `MapContainer` with a fixed `Marker` at given coordinates
  - Props: `lat: number`, `lng: number`
  - Used in report detail pages for both User and Supervisor
  - _Requirements: 10.2_

- [~] 10.3 Add GPS auto-detection in report form
  - In `ReportForm.tsx`, call `navigator.geolocation.getCurrentPosition()` on mount
  - On success, set initial coords and pass as `initialPosition` to `LocationPicker`
  - On denial or error, leave map at default center with no marker — user must place pin manually
  - Show a "Using your location" indicator when GPS is active
  - _Requirements: 10.3_


---

## Phase 11: User Dashboard

- [~] 11.1 Build User Dashboard page
  - `src/app/(user)/dashboard/page.tsx`: fetch `/api/v1/stats/user/` and display count cards (total reports, pending, resolved)
  - Show "Submit New Report" CTA button linking to `/user/reports/new`
  - Show last 3 reports as `ReportCard` components with status badge
  - _Requirements: 11.1_

- [~] 11.2 Build ReportCard component
  - `src/components/reports/ReportCard.tsx`: displays report title, status badge, created date, thumbnail of `before_photo`
  - Clicking navigates to report detail page
  - _Requirements: 11.2_

- [~] 11.3 Build User Reports list page
  - `src/app/(user)/reports/page.tsx`: fetch paginated `GET /api/v1/reports/` and render list of `ReportCard`
  - Add status filter tabs (All, Pending, Resolved, etc.)
  - Handle empty state with a "No reports yet" message and CTA
  - _Requirements: 11.3_

- [~] 11.4 Build New Report page and ReportForm component
  - `src/app/(user)/reports/new/page.tsx`: renders `ReportForm`
  - `src/components/reports/ReportForm.tsx`:
    - Title and description text inputs
    - `LocationPicker` map component (GPS auto-detect on mount)
    - File input for `before_photo` (accept `image/*`, preview thumbnail before upload)
    - On submit: POST `multipart/form-data` to `/api/v1/reports/`
    - On success: redirect to `/user/reports/{id}`
    - Show validation errors inline
  - _Requirements: 11.4_

- [~] 11.5 Build User Report Detail page
  - `src/app/(user)/reports/[id]/page.tsx`: fetch `GET /api/v1/reports/{id}/`
  - Display: title, description, status badge, `ReportMapView`, before photo, after photo (if present), timestamps
  - Show status history/timeline (created, assigned, resolved dates)
  - _Requirements: 11.5_

- [~] 11.6 Build User Profile page
  - `src/app/(user)/profile/page.tsx`: fetch `/auth/me/`, show and allow editing of `phone`, `avatar`
  - Avatar upload preview before submit
  - Change password section calling `POST /auth/change-password/`
  - _Requirements: 11.6_


---

## Phase 12: Supervisor Dashboard

- [~] 12.1 Build Supervisor Dashboard page
  - `src/app/(supervisor)/dashboard/page.tsx`: fetch `/api/v1/stats/supervisor/`
  - Display count cards: total area reports, pending, in-progress, resolved
  - Show list of most recent pending reports needing attention
  - _Requirements: 12.1_

- [~] 12.2 Build Supervisor Reports list page
  - `src/app/(supervisor)/reports/page.tsx`: fetch paginated `GET /api/v1/reports/area/`
  - Display reports table with: ID, title, reporter name, status badge, created date, action button
  - Add status filter and search by title
  - _Requirements: 12.2_

- [~] 12.3 Build AssignCleanerModal component
  - `src/components/assignments/AssignCleanerModal.tsx`:
    - Triggered by "Assign Cleaner" button on report detail page
    - Fetches `GET /api/v1/cleaners/` to populate dropdown of active cleaners in area
    - Optional notes textarea
    - On submit: `POST /api/v1/assignments/` with `{ report, cleaner, notes }`
    - On success: closes modal and updates report status to `assigned` in UI
  - _Requirements: 12.3_

- [~] 12.4 Build AfterPhotoUpload component
  - `src/components/reports/AfterPhotoUpload.tsx`:
    - Rendered on report detail when status is `in_progress`
    - File input with image preview
    - On submit: `PATCH /api/v1/reports/{id}/after-photo/` as multipart
    - On success: show uploaded photo and trigger status refresh
  - _Requirements: 12.4_

- [~] 12.5 Build Supervisor Report Detail page
  - `src/app/(supervisor)/reports/[id]/page.tsx`:
    - Fetch report detail, display all info + `ReportMapView`
    - Status update dropdown (enforcing valid transitions: assigned → in_progress → resolved, any → rejected)
    - "Assign Cleaner" button → `AssignCleanerModal` (shown when status is `pending`)
    - `AfterPhotoUpload` section (shown when status is `in_progress`)
    - Show assignment info if assigned
  - _Requirements: 12.5_

- [~] 12.6 Build Supervisor Cleaners pages
  - `src/app/(supervisor)/cleaners/page.tsx`: fetch `GET /api/v1/cleaners/`, display table with name, area, active status; "Add Cleaner" button
  - `src/app/(supervisor)/cleaners/[id]/page.tsx`: cleaner detail with edit form (name, is_active)
  - Add Cleaner form: create new User with role `user` then create `Cleaner` record, or expose dedicated endpoint
  - _Requirements: 12.6_


---

## Phase 13: Report Lifecycle Management

- [~] 13.1 Implement status transition validation (backend)
  - In `reports/views.py` `ReportStatusUpdateView`, validate transition is allowed per state machine (design section 10)
  - Valid transitions: PENDING→ASSIGNED (via assignment creation only), ASSIGNED→IN_PROGRESS, IN_PROGRESS→RESOLVED (requires after_photo), any→REJECTED
  - Return 400 with descriptive error on invalid transition attempt
  - Set `resolved_at = timezone.now()` when transitioning to RESOLVED
  - _Requirements: 13.1_

- [~] 13.2 Auto-assign area on report creation (backend)
  - In `ReportCreateSerializer.create()`, call `resolve_area(lat, lng)` and set `report.area`
  - If area is `None`, leave `area=null` — SuperAdmin handles unassigned reports
  - _Requirements: 13.2_

- [~] 13.3 Auto-transition to ASSIGNED on assignment creation
  - In `AssignmentCreateView.perform_create()`, after creating assignment, update linked report status to `assigned`
  - _Requirements: 13.3_

- [~] 13.4 Enforce after_photo required for RESOLVED transition
  - In status update view, if transitioning to RESOLVED and `report.after_photo` is empty, return 400 "After photo required before resolving"
  - _Requirements: 13.4_

- [~] 13.5 Implement REJECTED → PENDING re-open (SuperAdmin only)
  - Allow `IsSuperAdmin` to set status from `rejected` back to `pending`
  - This is the only case where a terminal status can be reversed
  - _Requirements: 13.5_


---

## Phase 14: API Client Modules (Next.js)

- [~] 14.1 Implement auth API module
  - `src/lib/api/auth.ts`: functions `register()`, `login()`, `logout()`, `refreshToken()`, `getMe()`, `updateMe()`, `changePassword()`
  - Each wraps the Axios client call, handles typing, returns typed responses
  - _Requirements: 14.1_

- [~] 14.2 Implement reports API module
  - `src/lib/api/reports.ts`: `getMyReports()`, `getReport(id)`, `createReport(payload: FormData)`, `updateReportStatus(id, status)`, `uploadAfterPhoto(id, file)`, `getAreaReports()`, `getAllReports()`
  - _Requirements: 14.2_

- [~] 14.3 Implement assignments API module
  - `src/lib/api/assignments.ts`: `createAssignment(payload)`, `getAssignment(id)`, `updateAssignment(id, patch)`
  - _Requirements: 14.3_

- [~] 14.4 Implement areas API module
  - `src/lib/api/areas.ts`: `getAreas()`, `getArea(id)`, `createArea(payload)`, `updateArea(id, patch)`, `deleteArea(id)`
  - _Requirements: 14.4_

- [~] 14.5 Implement cleaners API module
  - `src/lib/api/cleaners.ts`: `getCleaners()`, `getCleaner(id)`, `createCleaner(payload)`, `updateCleaner(id, patch)`, `deleteCleaner(id)`
  - _Requirements: 14.5_


---

## Phase 15: Celery Async Notifications (Phase 2)

- [~] 15.1 Set up Celery with Redis broker
  - In `config/celery.py`, configure `Celery` app pointing at Redis URL
  - In `config/__init__.py`, import Celery app so tasks auto-discover
  - Install `celery[redis]` and `redis` Python packages
  - _Requirements: 15.1_

- [~] 15.2 Implement notification tasks
  - In `reports/tasks.py`, implement `notify_supervisor_new_report(report_id)` and `notify_user_status_change(report_id, new_status)` (as per design section 11)
  - Call `notify_supervisor_new_report.delay(report.id)` at end of `ReportCreateSerializer.create()`
  - Call `notify_user_status_change.delay(report.id, new_status)` at end of status update view
  - _Requirements: 15.2_

- [~] 15.3 Configure email backend
  - In `development.py` use `EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"`
  - In `production.py` configure SMTP via env vars (`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, etc.)
  - _Requirements: 15.3_


---

## Phase 16: Testing & Quality

- [~] 16.1 Write backend unit tests
  - Test `resolve_area()` utility with polygon boundary fixtures
  - Test status transition validation (all valid and invalid transitions)
  - Test EXIF stripping function
  - Test image size/extension validators in serializers
  - Use `pytest-django` and factory_boy for test fixtures
  - _Requirements: 16.1_

- [~] 16.2 Write backend integration tests (API tests)
  - Auth flow: register → login → refresh → logout
  - Report flow: create report → supervisor assigns → in_progress → upload after-photo → resolved
  - Permission checks: verify non-supervisors cannot access `reports/area/`, non-admins cannot access `reports/all/`
  - Area routing: report coordinates inside area polygon → correct area assigned
  - _Requirements: 16.2_

- [~] 16.3 Write frontend component tests
  - `ReportStatusBadge` renders correct color for each status
  - `LocationPicker` calls `onChange` with correct coordinates on map click
  - `ReportForm` validation prevents submit without required fields or photo
  - `withRole` HOC redirects users with wrong role to `/login`
  - Use Jest + React Testing Library
  - _Requirements: 16.3_


---

## Phase 17: Production Readiness

- [~] 17.1 Harden Django security settings
  - In `production.py`: `DEBUG=False`, `SECURE_HSTS_SECONDS=31536000`, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`
  - Add rate limiting on `/api/v1/auth/login/` and `/api/v1/auth/register/` via `django-ratelimit` or Nginx
  - Restrict `CORS_ALLOWED_ORIGINS` to production frontend URL
  - _Requirements: 17.1_

- [~] 17.2 Add health check endpoint
  - In `config/urls.py`, add `GET /api/health/` returning `{ "status": "ok", "database": "ok" }` (check DB connection)
  - No authentication required
  - _Requirements: 17.2_

- [~] 17.3 Write production Dockerfile and Nginx config
  - `backend/Dockerfile`: multi-stage build, runs Gunicorn with gevent workers
  - `nginx/nginx.conf`: reverse proxy to Gunicorn, serve static files, SSL termination placeholders
  - Collect static: `python manage.py collectstatic --noinput` in Dockerfile CMD
  - _Requirements: 17.3_

- [~] 17.4 Configure Sentry error tracking
  - Install `sentry-sdk[django]` backend and `@sentry/nextjs` frontend
  - Initialize in `base.py` and `next.config.ts` using `SENTRY_DSN` env var
  - _Requirements: 17.4_

- [~] 17.5 Final production checklist verification
  - Verify all items in design section 9 production checklist are addressed
  - Run full test suite and confirm all tests pass
  - Smoke-test the full report lifecycle in a staging environment
  - _Requirements: 17.5_

---

## Checkpoint

- [~] 18. Final checkpoint — all systems verified
  - All Django migrations clean (`makemigrations --check` returns no changes)
  - All API endpoints return correct status codes and response shapes
  - All three dashboards functional (User, Supervisor, SuperAdmin/Jazzmin)
  - Full report lifecycle works end-to-end: submit → assign → in_progress → upload after-photo → resolved
  - Role-based access control verified (each role can only access permitted routes/endpoints)
  - Image upload, EXIF stripping, and media serving working in both dev and production config
  - Map location picker places pin correctly and coordinates saved to DB
  - Area routing correctly assigns reports to supervisor zones
  - All tests passing; no console errors in frontend
  - Ask the user if any questions arise before marking complete.
