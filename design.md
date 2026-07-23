# Garbage Reporting & Management System — Design

## 1. System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Clients                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  User (PWA)  │  │  Supervisor  │  │   SuperAdmin     │  │
│  │  Next.js     │  │  Next.js     │  │  Django Jazzmin  │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
└─────────┼────────────────┼───────────────────┼─────────────┘
          │                │                   │
          ▼                ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Django REST Framework API (HTTPS)              │
│         JWT Authentication  │  Role-Based Permissions       │
├─────────────────────────────────────────────────────────────┤
│   Reports  │  Users  │  Areas  │  Assignments  │  Media     │
├─────────────────────────────────────────────────────────────┤
│              Django ORM  │  Jazzmin Admin UI                │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL Database  │  S3 / Local Media Storage           │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend framework | Django 5.x + DRF | REST API, ORM, admin |
| Admin UI | Jazzmin | Themed Django admin |
| Frontend | Next.js 14 (App Router) | User/Supervisor SPA |
| Auth | `djangorestframework-simplejwt` | JWT tokens |
| Maps | Leaflet.js (or Google Maps JS SDK) | Location picking/display |
| Media storage | AWS S3 via `django-storages` (local dev: MEDIA_ROOT) | Image uploads |
| Database | PostgreSQL 16 | Primary datastore |
| Cache/Queue | Redis + Celery | Async notifications, image processing |


---

## 2. Django Models & Database Schema

### Model Definitions

```python
# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Extended user with role assignment."""

    class Role(models.TextChoices):
        SUPERADMIN = "superadmin", "SuperAdmin"
        SUPERVISOR = "supervisor", "Supervisor"
        USER       = "user",       "User"

    role        = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    phone       = models.CharField(max_length=20, blank=True)
    avatar      = models.ImageField(upload_to="avatars/", null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_user_extended"
```

```python
# areas/models.py

class Area(models.Model):
    """Geographic zone managed by one supervisor."""
    name        = models.CharField(max_length=200)
    # Bounding polygon stored as JSON [[lat, lng], ...]
    boundary    = models.JSONField(default=list)
    supervisor  = models.OneToOneField(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="managed_area",
        limit_choices_to={"role": "supervisor"},
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
```

```python
# cleaners/models.py

class Cleaner(models.Model):
    """A field worker managed by a supervisor."""
    user        = models.OneToOneField(
        "accounts.User", on_delete=models.CASCADE, related_name="cleaner_profile"
    )
    area        = models.ForeignKey(
        "areas.Area", on_delete=models.SET_NULL, null=True, related_name="cleaners"
    )
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
```


```python
# reports/models.py

class Report(models.Model):
    """A garbage complaint submitted by a regular user."""

    class Status(models.TextChoices):
        PENDING    = "pending",    "Pending"
        ASSIGNED   = "assigned",   "Assigned"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED   = "resolved",   "Resolved"
        REJECTED   = "rejected",   "Rejected"

    reporter        = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="reports"
    )
    area            = models.ForeignKey(
        "areas.Area", on_delete=models.SET_NULL, null=True, related_name="reports"
    )
    title           = models.CharField(max_length=255)
    description     = models.TextField(blank=True)
    latitude        = models.DecimalField(max_digits=9, decimal_places=6)
    longitude       = models.DecimalField(max_digits=9, decimal_places=6)
    before_photo    = models.ImageField(upload_to="reports/before/")
    after_photo     = models.ImageField(upload_to="reports/after/", null=True, blank=True)
    status          = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    resolved_at     = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes  = [
            models.Index(fields=["status"]),
            models.Index(fields=["area", "status"]),
        ]
```

```python
class Assignment(models.Model):
    """Links a report to a cleaner, created by a supervisor."""
    report      = models.OneToOneField(Report, on_delete=models.CASCADE, related_name="assignment")
    cleaner     = models.ForeignKey(
        "cleaners.Cleaner", on_delete=models.SET_NULL, null=True, related_name="assignments"
    )
    assigned_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, related_name="assignments_made"
    )
    notes       = models.TextField(blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
```

### Database Schema (ERD Summary)

```
User (id, username, email, password, role, phone, avatar)
  │
  ├─ 1:1 ──► Area (id, name, boundary JSON, supervisor_id)
  │               │
  │               └─ 1:N ──► Cleaner (id, user_id, area_id, is_active)
  │
  └─ 1:N ──► Report (id, reporter_id, area_id, title, description,
                      latitude, longitude, before_photo, after_photo,
                      status, created_at, resolved_at)
                  │
                  └─ 1:1 ──► Assignment (id, report_id, cleaner_id,
                                          assigned_by_id, notes, assigned_at)
```


---

## 3. REST API Endpoint Design

All endpoints are prefixed with `/api/v1/`. Authentication uses Bearer JWT tokens unless marked `[public]`.

### Authentication

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/auth/register/` | Register new user account | public |
| POST | `/auth/login/` | Obtain access + refresh tokens | public |
| POST | `/auth/token/refresh/` | Refresh access token | public |
| POST | `/auth/logout/` | Blacklist refresh token | authenticated |
| GET/PATCH | `/auth/me/` | Get / update own profile | authenticated |
| POST | `/auth/change-password/` | Change own password | authenticated |

### Reports

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/reports/` | List own reports | User |
| POST | `/reports/` | Submit new garbage report (multipart) | User |
| GET | `/reports/{id}/` | Get single report details | Owner / Supervisor / SuperAdmin |
| PATCH | `/reports/{id}/after-photo/` | Upload after-cleaning photo | Supervisor |
| GET | `/reports/area/` | List all reports in supervisor's area | Supervisor |
| GET | `/reports/all/` | List all reports across system | SuperAdmin |
| PATCH | `/reports/{id}/status/` | Update report status | Supervisor / SuperAdmin |

### Assignments

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/assignments/` | Assign cleaner to report | Supervisor |
| GET | `/assignments/{id}/` | Get assignment details | Supervisor / SuperAdmin |
| PATCH | `/assignments/{id}/` | Update notes or completion | Supervisor |

### Areas

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/areas/` | List all areas | SuperAdmin |
| POST | `/areas/` | Create area | SuperAdmin |
| GET | `/areas/{id}/` | Get area details + boundary | SuperAdmin / Supervisor |
| PATCH | `/areas/{id}/` | Update area (boundary, supervisor) | SuperAdmin |
| DELETE | `/areas/{id}/` | Delete area | SuperAdmin |

### Cleaners

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/cleaners/` | List cleaners in supervisor's area | Supervisor |
| POST | `/cleaners/` | Add cleaner | Supervisor / SuperAdmin |
| GET | `/cleaners/{id}/` | Cleaner details | Supervisor / SuperAdmin |
| PATCH | `/cleaners/{id}/` | Update cleaner | Supervisor / SuperAdmin |
| DELETE | `/cleaners/{id}/` | Deactivate cleaner | SuperAdmin |

### Users (SuperAdmin)

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/users/` | List all users | SuperAdmin |
| GET | `/users/{id}/` | User details | SuperAdmin |
| PATCH | `/users/{id}/` | Update user role/status | SuperAdmin |
| DELETE | `/users/{id}/` | Deactivate user | SuperAdmin |

### Dashboard Stats

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/stats/superadmin/` | System-wide counts & trends | SuperAdmin |
| GET | `/stats/supervisor/` | Area-scoped counts | Supervisor |
| GET | `/stats/user/` | Own report counts | User |


### API Response Conventions

```json
// Success (list)
{
  "count": 42,
  "next": "http://api/v1/reports/?page=2",
  "previous": null,
  "results": [ ... ]
}

// Success (single)
{
  "id": 1,
  "status": "pending",
  "reporter": { "id": 5, "name": "Alice" },
  "latitude": "23.810331",
  "longitude": "90.412521",
  "before_photo": "https://cdn.example.com/reports/before/abc.jpg",
  "created_at": "2025-07-23T10:30:00Z"
}

// Error
{
  "error": "permission_denied",
  "detail": "You do not have permission to perform this action."
}
```

---

## 4. Next.js Frontend Structure

### App Router Directory Layout

```
src/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   │
│   ├── (user)/
│   │   ├── layout.tsx           # User shell + bottom nav
│   │   ├── dashboard/
│   │   │   └── page.tsx         # My reports summary
│   │   ├── reports/
│   │   │   ├── page.tsx         # List my reports
│   │   │   ├── new/
│   │   │   │   └── page.tsx     # Submit new report (photo + map)
│   │   │   └── [id]/
│   │   │       └── page.tsx     # Report detail + status
│   │   └── profile/
│   │       └── page.tsx
│   │
│   ├── (supervisor)/
│   │   ├── layout.tsx           # Supervisor shell + sidebar
│   │   ├── dashboard/
│   │   │   └── page.tsx         # Area stats, pending count
│   │   ├── reports/
│   │   │   ├── page.tsx         # All reports in area
│   │   │   └── [id]/
│   │   │       └── page.tsx     # Report detail, assign cleaner, upload after-photo
│   │   └── cleaners/
│   │       ├── page.tsx         # Manage cleaners
│   │       └── [id]/page.tsx
│   │
│   └── layout.tsx               # Root layout (fonts, providers)
│
├── components/
│   ├── ui/                      # Headless/Shadcn primitive wrappers
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Badge.tsx
│   │   └── Modal.tsx
│   ├── map/
│   │   ├── LocationPicker.tsx   # Leaflet map for selecting a pin
│   │   └── ReportMapView.tsx    # Read-only pin display
│   ├── reports/
│   │   ├── ReportCard.tsx
│   │   ├── ReportStatusBadge.tsx
│   │   ├── ReportForm.tsx       # New report form (photo + map)
│   │   └── AfterPhotoUpload.tsx
│   ├── assignments/
│   │   └── AssignCleanerModal.tsx
│   └── layout/
│       ├── Navbar.tsx
│       ├── Sidebar.tsx
│       └── BottomNav.tsx        # Mobile user nav
│
├── lib/
│   ├── api/
│   │   ├── client.ts            # Axios instance with JWT interceptors
│   │   ├── auth.ts
│   │   ├── reports.ts
│   │   ├── assignments.ts
│   │   └── areas.ts
│   ├── auth/
│   │   ├── useAuth.ts           # Auth context hook
│   │   └── withRole.tsx         # HOC for role-gating routes
│   └── utils/
│       ├── formatDate.ts
│       └── statusColor.ts
│
├── store/
│   └── authStore.ts             # Zustand store for user/token state
│
└── types/
    ├── user.ts
    ├── report.ts
    ├── area.ts
    └── assignment.ts
```


### Key Page Behaviors

**New Report Page (`/user/reports/new`)**
1. User grants geolocation permission → map auto-centers on current position.
2. User drags pin or taps map to set exact coordinates.
3. User uploads/takes a photo (accepts `image/*`).
4. Form submits as `multipart/form-data` to `POST /api/v1/reports/`.
5. On success, redirect to report detail page.

**Supervisor Report Detail (`/supervisor/reports/[id]`)**
1. Shows report info, before-photo, map pin, current status.
2. "Assign Cleaner" button opens `AssignCleanerModal` with a dropdown of available cleaners in the area.
3. "Upload After Photo" section appears once status is `in_progress`.
4. Supervisor can change status (assigned → in_progress → resolved).

---

## 5. Authentication & Authorization Design

### JWT Flow

```
Client                        Django API
  │                               │
  │── POST /auth/login/ ─────────►│
  │   { username, password }      │  Validate credentials
  │                               │  Issue access_token (15 min TTL)
  │◄─ { access, refresh } ───────│       + refresh_token (7 day TTL)
  │                               │
  │── GET /api/v1/reports/ ──────►│
  │   Authorization: Bearer <access> │  Verify signature + expiry
  │◄─ 200 OK { results: [...] } ─│
  │                               │
  │── POST /auth/token/refresh/ ─►│
  │   { refresh: <token> }        │  Rotate refresh token
  │◄─ { access: <new_token> } ───│
```

### Permission Classes (DRF)

```python
# permissions.py

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.SUPERADMIN

class IsSupervisor(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.SUPERVISOR

class IsReporter(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.USER

class IsOwnerOrSupervisorOrAdmin(BasePermission):
    """Report owner, the area supervisor, or superadmin can access."""
    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.SUPERADMIN:
            return True
        if request.user.role == User.Role.SUPERVISOR:
            return obj.area == request.user.managed_area
        return obj.reporter == request.user
```

### Area Routing Logic

When a user submits a report with coordinates, the backend automatically resolves which `Area` the pin falls within:

```python
# reports/utils.py

from shapely.geometry import Point, Polygon
from areas.models import Area

def resolve_area(lat: float, lng: float) -> Area | None:
    point = Point(lng, lat)
    for area in Area.objects.exclude(boundary=[]):
        polygon = Polygon([(p[1], p[0]) for p in area.boundary])
        if polygon.contains(point):
            return area
    return None  # Unassigned — SuperAdmin handles manually
```

### Frontend Route Guards

```typescript
// lib/auth/withRole.tsx
export function withRole(allowedRoles: Role[]) {
  return function <P extends object>(Component: React.ComponentType<P>) {
    return function ProtectedRoute(props: P) {
      const { user, loading } = useAuth();
      if (loading) return <Spinner />;
      if (!user || !allowedRoles.includes(user.role)) {
        redirect("/login");
      }
      return <Component {...props} />;
    };
  };
}
```


---

## 6. Maps / Location Integration

### Approach: Leaflet.js (recommended) or Google Maps

Leaflet is recommended for cost-free deployment; Google Maps can be substituted with an API key.

### LocationPicker Component

```tsx
// components/map/LocationPicker.tsx
"use client";
import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import { useState } from "react";

interface Props {
  onChange: (lat: number, lng: number) => void;
  initialPosition?: [number, number];
}

function DraggableMarker({ onChange }: { onChange: Props["onChange"] }) {
  const [position, setPosition] = useState<[number, number] | null>(null);

  useMapEvents({
    click(e) {
      setPosition([e.latlng.lat, e.latlng.lng]);
      onChange(e.latlng.lat, e.latlng.lng);
    },
  });

  return position ? <Marker position={position} draggable
    eventHandlers={{ dragend: (e) => {
      const m = e.target;
      const p = m.getLatLng();
      setPosition([p.lat, p.lng]);
      onChange(p.lat, p.lng);
    }}} /> : null;
}

export default function LocationPicker({ onChange, initialPosition }: Props) {
  const defaultCenter: [number, number] = initialPosition ?? [23.8103, 90.4125];
  return (
    <MapContainer center={defaultCenter} zoom={13} style={{ height: 300, width: "100%" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <DraggableMarker onChange={onChange} />
    </MapContainer>
  );
}
```

### GPS Auto-Detection (Report Submission)

```typescript
// In ReportForm.tsx
useEffect(() => {
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      setCoords({ lat: pos.coords.latitude, lng: pos.coords.longitude });
    },
    () => { /* User denied — manual pin only */ }
  );
}, []);
```

### Coordinates Storage

- Stored as `DecimalField(max_digits=9, decimal_places=6)` in PostgreSQL.
- Precision of 6 decimal places gives ~0.1 m accuracy — sufficient for garbage location pinning.
- Area boundaries stored as GeoJSON-compatible `JSONField` polygon array.

---

## 7. Media / Image Storage Design

### Storage Backends

| Environment | Backend | Config |
|------------|---------|--------|
| Development | Django `MEDIA_ROOT` (local filesystem) | `DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"` |
| Production | AWS S3 via `django-storages` | `DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"` |

### Django Settings (Production)

```python
# settings/production.py
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_ACCESS_KEY_ID     = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_S3_BUCKET")
AWS_S3_REGION_NAME    = "us-east-1"
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL       = "private"          # Signed URLs for access
AWS_S3_SIGNATURE_VERSION = "s3v4"
MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/"
```

### Upload Flow

```
Client
  │── POST /api/v1/reports/ (multipart/form-data)
  │   Content-Type: multipart/form-data
  │   Fields: title, description, latitude, longitude, before_photo (file)
  │
Django DRF (serializer validates file)
  │── Saves to S3 bucket path: reports/before/{uuid}.jpg
  │── Generates signed URL (expiry 1 hour) for response
  │
Client renders photo via signed URL
```

### Image Validation

```python
# serializers.py
from django.core.validators import FileExtensionValidator

class ReportSerializer(serializers.ModelSerializer):
    before_photo = serializers.ImageField(
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])]
    )

    def validate_before_photo(self, value):
        max_mb = 10
        if value.size > max_mb * 1024 * 1024:
            raise serializers.ValidationError(f"Image must be under {max_mb}MB.")
        return value
```

### Upload Size Limits

- `before_photo`: required, max 10 MB
- `after_photo`: required (by supervisor), max 10 MB
- `avatar`: optional, max 2 MB


---

## 8. Django Project Structure

```
backend/
├── config/
│   ├── settings/
│   │   ├── base.py          # Shared settings
│   │   ├── development.py   # Debug=True, local DB, local media
│   │   └── production.py    # S3, PostgreSQL, HTTPS
│   ├── urls.py              # Root URL conf
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                # Custom User model + auth views
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── permissions.py
│
├── areas/                   # Area model + CRUD
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── reports/                 # Report model + lifecycle
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── utils.py             # resolve_area()
│
├── cleaners/                # Cleaner model
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── assignments/             # Assignment model
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── stats/                   # Dashboard aggregation views
│   ├── views.py
│   └── urls.py
│
└── manage.py
```

### Jazzmin Configuration

```python
# config/settings/base.py

INSTALLED_APPS = [
    "jazzmin",              # MUST be before django.contrib.admin
    "django.contrib.admin",
    # ...
]

JAZZMIN_SETTINGS = {
    "site_title": "GarbageMS Admin",
    "site_header": "Garbage Management",
    "site_brand": "GarbageMS",
    "welcome_sign": "Welcome to Garbage Management System",
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "icons": {
        "accounts.User": "fas fa-users",
        "reports.Report": "fas fa-trash-alt",
        "areas.Area": "fas fa-map-marked-alt",
        "cleaners.Cleaner": "fas fa-hard-hat",
        "assignments.Assignment": "fas fa-tasks",
    },
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
}
```

---

## 9. Deployment Considerations

### Infrastructure Overview

```
                         ┌─────────────┐
                         │   Vercel    │  (Next.js frontend)
                         └──────┬──────┘
                                │ HTTPS
                         ┌──────▼──────┐
                         │  Nginx      │  (Reverse proxy)
                         └──────┬──────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
       ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
       │  Gunicorn   │  │   Celery    │  │   Redis     │
       │  (Django)   │  │  (Workers)  │  │  (Broker)   │
       └──────┬──────┘  └─────────────┘  └─────────────┘
              │
       ┌──────▼──────┐        ┌─────────────┐
       │ PostgreSQL  │        │   AWS S3    │
       └─────────────┘        └─────────────┘
```

### Environment Variables

```bash
# Django
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=api.example.com
DATABASE_URL=postgres://user:pass@host:5432/garbagems
REDIS_URL=redis://localhost:6379/0

# AWS
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=garbagems-media

# JWT
ACCESS_TOKEN_LIFETIME_MINUTES=15
REFRESH_TOKEN_LIFETIME_DAYS=7

# CORS
CORS_ALLOWED_ORIGINS=https://app.example.com
```

### Docker Compose (Development)

```yaml
version: "3.9"
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: garbagems
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  api:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
      - media_vol:/app/media
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.development

  frontend:
    build: ./frontend
    command: npm run dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app

volumes:
  pgdata:
  media_vol:
```

### Production Checklist

- [ ] `DEBUG=False` and `ALLOWED_HOSTS` set
- [ ] PostgreSQL with connection pooling (PgBouncer)
- [ ] S3 bucket with versioning + lifecycle policies for old media
- [ ] SSL certificates (Let's Encrypt via Certbot)
- [ ] Django `SECURE_HSTS_SECONDS`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`
- [ ] Rate limiting on auth endpoints (django-ratelimit or Nginx)
- [ ] Celery workers for async tasks (email notifications, image optimization)
- [ ] Sentry for error tracking (backend + frontend)
- [ ] Health check endpoint `GET /api/health/` returning `{ "status": "ok" }`
- [ ] Database backups automated (daily snapshots)
- [ ] `MEDIA_ROOT` backed up or fully migrated to S3


---

## 10. Report Lifecycle State Machine

```
                 User submits report
                        │
                        ▼
                   [ PENDING ]
                        │
              Supervisor assigns cleaner
                        │
                        ▼
                  [ ASSIGNED ]
                        │
              Cleaner starts cleaning
                        │
                        ▼
                [ IN_PROGRESS ]
                        │
              Supervisor uploads after-photo
                        │
                        ▼
                  [ RESOLVED ]  ◄── or ──►  [ REJECTED ]
                                            (SuperAdmin/Supervisor)
```

### Status Transition Rules

| From | To | Actor | Required Action |
|------|----|-------|----------------|
| PENDING | ASSIGNED | Supervisor | Create Assignment record |
| ASSIGNED | IN_PROGRESS | Supervisor | Mark cleaner has started |
| IN_PROGRESS | RESOLVED | Supervisor | Upload `after_photo` |
| Any | REJECTED | Supervisor / SuperAdmin | Provide rejection reason |
| REJECTED | PENDING | SuperAdmin | Re-open complaint |

---

## 11. Notifications Design (Optional Phase 2)

Using Celery + Redis for async email/push notifications:

```python
# tasks.py (Celery)

@shared_task
def notify_supervisor_new_report(report_id: int):
    """Email supervisor when a new report lands in their area."""
    report = Report.objects.select_related("area__supervisor").get(id=report_id)
    if report.area and report.area.supervisor:
        send_mail(
            subject=f"New garbage report in {report.area.name}",
            message=f"Report #{report.id} submitted at ({report.latitude}, {report.longitude})",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[report.area.supervisor.email],
        )

@shared_task
def notify_user_status_change(report_id: int, new_status: str):
    """Email the reporter when their report status changes."""
    report = Report.objects.select_related("reporter").get(id=report_id)
    send_mail(
        subject=f"Your report #{report.id} status: {new_status}",
        message=f"Your garbage report has been updated to '{new_status}'.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[report.reporter.email],
    )
```

---

## 12. Security Considerations

| Concern | Mitigation |
|---------|-----------|
| JWT token theft | Short access token TTL (15 min), HTTP-only refresh token cookie |
| Unauthorized area access | Supervisor views filtered by `request.user.managed_area` at queryset level |
| Insecure file upload | File extension + MIME type validation, max size enforcement, S3 private ACL |
| SQL injection | Django ORM parameterized queries throughout |
| CORS | Whitelist only known frontend origins in `CORS_ALLOWED_ORIGINS` |
| Mass assignment | DRF serializers with explicit `fields` or `read_only_fields` |
| Privilege escalation | Role stored server-side only; users cannot self-assign roles |
| Image metadata (EXIF) | Strip EXIF with Pillow before storing to protect user location privacy |

### EXIF Stripping Example

```python
from PIL import Image
import io

def strip_exif(image_file) -> bytes:
    img = Image.open(image_file)
    data = list(img.getdata())
    clean = Image.new(img.mode, img.size)
    clean.putdata(data)
    buf = io.BytesIO()
    clean.save(buf, format=img.format or "JPEG")
    return buf.getvalue()
```
