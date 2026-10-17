# CareOS — Healthcare Records Controller

![CareOS Badge](https://img.shields.io/badge/CareOS-Healthcare_Backend-10b981?style=for-the-badge)
![Django 5](https://img.shields.io/badge/Django-5.0+-092e20?style=for-the-badge&logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql)
![JWT](https://img.shields.io/badge/SimpleJWT-Bearer_Auth-black?style=for-the-badge)
![Tests](https://img.shields.io/badge/Tests-29%2F29_Passing-brightgreen?style=for-the-badge)

CareOS is a high-assurance, production-quality **Healthcare Records Controller** designed to securely govern patient data, manage physician directories, and establish verified clinical assignments. Built on **Django 5**, **Django REST Framework (DRF)**, **PostgreSQL (via psycopg2-binary)**, and **SimpleJWT**, CareOS features a modern, ultra-clean fintech user interface inspired by the Kuber-OS design language (with instant light/dark mode support, responsive KPI metric surfaces, and interactive modal workflows).

---

## Architecture & Security Highlights

1. **Zero Data Leakage (IsOwner Policy)**:
   - Patient records are strictly isolated. Users can only read, update, or delete patients they personally created.
   - Doctor directory is discoverable by all authenticated practitioners, but records can only be mutated or deleted by their original creator.
2. **Compound Constraint Mapping**:
   - `PatientDoctorMapping` enforces database-level uniqueness across `(patient, doctor)` pairs. Duplicate assignments are rejected with standard `400/409` errors.
   - Practitioners can only assign doctors to patients they own.
3. **Pure Django ORM on PostgreSQL**:
   - 100% parameter-bound queries through `psycopg2-binary`.
   - Foreign key indexing and `select_related` query optimizations eliminate N+1 latency.
4. **Transparent Token Rotation**:
   - JWT Access tokens (default 60 min) with refresh tokens (default 7 days).
   - Frontend API client automatically catches 401s, rotates the session, and seamlessly retries requests without user interruption.
5. **Standardized Error Formatting**:
   - All errors are formatted into `{ "success": false, "message": "...", "errors": {...} }`.

---

## Project Structure

```
healthcare_backend/
├── manage.py                   # Django CLI management
├── requirements.txt            # Project dependencies
├── .env.example                # Example environment configuration
├── .env                        # Local active environment variables (ignored by git)
├── .gitignore                  # Git ignore rules
├── README.md                   # Complete architectural and setup guide
├── postman_collection.json     # Ready-to-import Postman API collection
├── config/                     # Django core (settings.py, urls.py, wsgi.py, asgi.py)
├── accounts/                   # Registration, login, JWT token serializers & views
├── patients/                   # Patient model, serializers, views, IsOwner permissions
├── doctors/                    # Doctor model, serializers, views, IsCreator permissions
├── mappings/                   # PatientDoctorMapping model, validation, and views
├── core/                       # Custom exception handler, pagination, template views, commands
├── templates/                  # base.html, landing.html, console.html, login.html, register.html
└── static/                     # theme.css, landing.css, console.css, auth.css, api.js, console.js, auth.js
```

---

## Prerequisites & Installation

### 1. Python Environment
- Python 3.11, 3.12, or 3.13
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### 2. PostgreSQL Database Setup
Ensure PostgreSQL is running on port 5432. Connect to PostgreSQL and create the database:
```sql
CREATE DATABASE healthcare_db;
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and configure your credentials:
```bash
cp .env.example .env
```

Contents of `.env`:
```ini
SECRET_KEY=careos-django-insecure-prod-key-kuber-os-healthcare-controller-2026
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# PostgreSQL Database Configuration
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=127.0.0.1
DB_PORT=5432

# SimpleJWT Authentication
JWT_ACCESS_MINUTES=60
JWT_REFRESH_DAYS=7
```

### 4. Database Migrations
Apply all schema migrations against PostgreSQL:
```bash
python manage.py migrate
```

### 5. Seed Demonstration Dataset (Optional)
CareOS includes a built-in demo dataset command:
```bash
python manage.py seed_demo
```
This provisions:
- **Provider Account**: `doctor@careos.health` (Password: `CareOS2026!`)
- 3 Patient records with demographics and medical history
- 3 Verified physicians across Diagnostic Medicine, Oncology, and Endocrinology
- 2 Active Patient-Doctor mappings

### 6. Run the Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## Running the Automated Test Suite

CareOS comes with a comprehensive test suite (`APITestCase`) covering user registration, JWT logins, invalid credential handling, patient CRUD ownership isolation, doctor directory mutations, duplicate mapping rejections, and cascade deletions.

Run the test suite:
```bash
python manage.py test
```

Expected output:
```
Creating test database for alias 'default'...
.............................
----------------------------------------------------------------------
Ran 29 tests in 29.420s

OK
Destroying test database for alias 'default'...
```

---

## API Endpoints Reference

All endpoints return standardized JSON structures.

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Public | Register new provider account |
| `POST` | `/api/auth/login/` | Public | Authenticate and obtain JWT access & refresh |
| `POST` | `/api/auth/token/refresh/` | Public | Exchange refresh token for new access token |
| `GET` | `/api/patients/` | Bearer JWT | List paginated patients created by authenticated user |
| `POST` | `/api/patients/` | Bearer JWT | Create new patient (auto-binds `created_by`) |
| `GET` | `/api/patients/<id>/` | Bearer JWT | Retrieve patient details (`IsOwner` protected) |
| `PUT` | `/api/patients/<id>/` | Bearer JWT | Full update of patient (`IsOwner` protected) |
| `DELETE` | `/api/patients/<id>/` | Bearer JWT | Delete patient record (`IsOwner` protected) |
| `GET` | `/api/doctors/` | Bearer JWT | List all doctors in directory (`select_related`) |
| `POST` | `/api/doctors/` | Bearer JWT | Enroll physician into directory |
| `GET` | `/api/doctors/<id>/` | Bearer JWT | Retrieve physician details |
| `PUT` | `/api/doctors/<id>/` | Bearer JWT | Update physician details (creator only) |
| `DELETE` | `/api/doctors/<id>/` | Bearer JWT | Delete physician profile (creator only) |
| `GET` | `/api/mappings/` | Bearer JWT | List all active patient-doctor mappings |
| `POST` | `/api/mappings/` | Bearer JWT | Assign doctor to patient (rejects duplicates & foreign patients) |
| `GET` | `/api/mappings/<patient_id>/` | Bearer JWT | List all doctors assigned to specific patient |
| `DELETE` | `/api/mappings/<id>/` | Bearer JWT | Remove doctor mapping (by mapping ID) |
| `GET` | `/api/stats/` | Public | High-level KPI metrics summary |

---

## Sample API Requests & Responses

### 1. Register Provider
`POST /api/auth/register/`
```json
{
  "name": "Dr. Sarah Connor",
  "email": "sarah@careos.health",
  "password": "CareOS2026!",
  "confirm_password": "CareOS2026!"
}
```
**Response (`201 Created`):**
```json
{
  "success": true,
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "name": "Dr. Sarah Connor",
    "email": "sarah@careos.health"
  },
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 2. Login
`POST /api/auth/login/`
```json
{
  "email": "sarah@careos.health",
  "password": "CareOS2026!"
}
```
**Response (`200 OK`):**
```json
{
  "success": true,
  "message": "Login successful.",
  "user": {
    "id": 1,
    "name": "Dr. Sarah Connor",
    "email": "sarah@careos.health"
  },
  "access": "eyJhbGciOiJIUzI1Ni...",
  "refresh": "eyJhbGciOiJIUzI1Ni...",
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1Ni...",
    "access": "eyJhbGciOiJIUzI1Ni..."
  }
}
```

### 3. Create Patient
`POST /api/patients/`
`Authorization: Bearer <access>`
```json
{
  "name": "Eleanor Vance",
  "age": 42,
  "gender": "Female",
  "phone": "+1-555-019-4820",
  "address": "742 Evergreen Terrace, Springfield",
  "medical_history": "Type II Diabetes, regular glycemic monitoring."
}
```
**Response (`201 Created`):**
```json
{
  "success": true,
  "message": "Patient record created successfully.",
  "data": {
    "id": 1,
    "created_by": 1,
    "created_by_name": "Dr. Sarah Connor",
    "created_by_email": "sarah@careos.health",
    "name": "Eleanor Vance",
    "age": 42,
    "gender": "Female",
    "phone": "+1-555-019-4820",
    "address": "742 Evergreen Terrace, Springfield",
    "medical_history": "Type II Diabetes, regular glycemic monitoring.",
    "created_at": "2026-10-17T16:30:00Z",
    "updated_at": "2026-10-17T16:30:00Z"
  }
}
```

### 4. Duplicate Mapping Error Handling
`POST /api/mappings/`
`Authorization: Bearer <access>`
```json
{
  "patient": 1,
  "doctor": 1
}
```
**Response (`400 Bad Request`):**
```json
{
  "success": false,
  "message": "duplicate: This doctor is already assigned to this patient.",
  "errors": {
    "duplicate": "This doctor is already assigned to this patient."
  }
}
```

---

## Postman Collection

Import `postman_collection.json` directly into Postman or Insomnia.
- Contains all authentication, patient CRUD, doctor directory, and clinical mapping requests.
- Automatic Post-Request script on `/api/auth/login/` extracts and populates the `{{token}}` collection variable automatically for subsequent requests.

---

## UI Guide (CareOS Controller)

1. **Landing Page (`/`)**:
   - Hero with live execution pipeline animation.
   - Architectural comparison (Traditional Record Keeping vs CareOS Secure Backend).
   - Real-time stats strip.
   - 6-step lifecycle cards with verified status badges.
   - Dual-surface preview tabs (Patient Hub & Doctor Radar).
   - Light/Dark theme switcher with system preference detection.
2. **Clinical Console (`/console/`)**:
   - Requires login.
   - Top KPI metric row (Total Patients, Active Doctors, Configured Mappings, System Integrity).
   - Interactive search and filter.
   - Instant modals for adding/editing records.
   - Live validation error alerts under inputs.
   - Toast notifications for every mutation.
3. **Auth (`/login/`, `/register/`)**:
   - Clean fintech styled authentication forms with automated credential verification.
