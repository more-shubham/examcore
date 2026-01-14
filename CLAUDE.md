# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ExamCore** is an enterprise-grade examination management system built with Django 5.0. It provides role-based user management, multi-step registration with OTP verification, exam/question management, and result tracking for educational institutions.

- **Framework**: Django 5.0
- **Python**: 3.11+ (supports 3.11, 3.12, 3.13)
- **Database**: PostgreSQL (production), SQLite (testing)
- **Frontend**: Tailwind CSS via django-tailwind
- **Status**: Alpha v0.1.0

## Build & Development Commands

```bash
# Install dependencies (development)
pip install -e ".[dev]"

# Run development server
python manage.py runserver

# Run with Docker Compose (includes PostgreSQL + Mailpit)
docker-compose up -d

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Tailwind CSS (requires Node.js)
python manage.py tailwind install
python manage.py tailwind start    # Development with hot-reload
python manage.py tailwind build    # Production build

# Collect static files (production)
python manage.py collectstatic --noinput
```

## Testing Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps

# Run tests in parallel
pytest -n auto

# Run specific test file
pytest apps/accounts/tests.py

# Run specific test class/method
pytest apps/accounts/tests.py::TestUserModel::test_create_user

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

## Code Quality Commands

```bash
# Format code (Black)
black .

# Sort imports (isort)
isort .

# Lint (flake8)
flake8

# Type checking (mypy)
mypy .

# Security scan (Bandit)
bandit -r apps/

# Run all pre-commit hooks
pre-commit run --all-files

# Install pre-commit hooks
pre-commit install
```

## Architecture

### Directory Structure

```
examcore/
├── apps/                    # Django applications (modular features)
│   ├── accounts/           # User auth, registration, school setup
│   ├── exams/              # Exam management (to be implemented)
│   ├── questions/          # Question bank (to be implemented)
│   └── results/            # Result tracking (to be implemented)
├── config/                  # Project configuration
│   ├── settings/           # Environment-specific settings
│   │   ├── base.py        # Shared settings
│   │   ├── development.py # Debug=True, console email
│   │   ├── production.py  # Security hardened, HTTPS
│   │   └── test.py        # In-memory SQLite, fast hashers
│   ├── urls.py            # Root URL configuration
│   ├── wsgi.py            # WSGI entry point
│   └── asgi.py            # ASGI entry point
├── theme/                   # Tailwind CSS theme app
├── templates/               # Project-level templates
├── static/                  # Static files (CSS, JS, images)
└── media/                   # User uploaded files
```

### Key Design Patterns

1. **Singleton School Model**: Only one School record per installation (`apps/accounts/models.py:33-37`)
2. **Role-Based Access Control**: User model with Role enum (admin, examiner, teacher, student)
3. **Multi-Step Registration**: Session-based wizard pattern with OTP email verification
4. **Environment-Specific Settings**: Separate settings modules imported via `DJANGO_SETTINGS_MODULE`

### URL Structure

**Authentication:**
| URL | Purpose |
|-----|---------|
| `/` | Single-page auth (Login/Register/Verify OTP/School Setup - state-based) |
| `/logout/` | Logout (POST only) |
| `/resend-otp/` | Resend OTP (POST only) |

**Dashboard & Management:**
| URL | Purpose |
|-----|---------|
| `/dashboard/` | Main dashboard (protected) |
| `/examiners/` | Examiner management |
| `/teachers/` | Teacher management |
| `/classes/` | Class management with drag-drop reorder |
| `/classes/<id>/students/` | Students in a specific class |

**Future Modules:**
| URL | Purpose |
|-----|---------|
| `/exams/` | Exam management |
| `/questions/` | Question management |
| `/results/` | Result tracking |
| `/admin/` | Django admin interface

**URL Design Rules:**
- Use path parameters for resource identification: `/classes/1/students/` NOT `/students/?class=1`
- Use RESTful nested resources where appropriate
- Avoid query parameters except for filtering/pagination

### Custom User Model

Located at `apps/accounts/models.py`. Extends `AbstractUser` with:
- `role` field (admin/examiner/teacher/student)
- `phone` and `avatar` fields
- Role check properties: `is_admin`, `is_examiner`, `is_teacher`, `is_student`

### Authentication Flow

Single-page auth at `/` with automatic routing:

```
User visits /
    ↓
AuthView checks: Does admin exist?
    │
    ├─ NO admin → Show Register Form (Step 1)
    │      ↓
    │   Submit → Send OTP → /verify/ (Step 2)
    │      ↓
    │   Verify OTP → /school/ (Step 3)
    │      ↓
    │   Setup School → Create Admin → Auto-login → /dashboard/
    │
    └─ YES admin → Show Login Form
           ↓
       Login → /dashboard/
```

**Session State Handling:**
- If registration started but OTP not verified → redirects to `/verify/`
- If OTP verified but school not created → redirects to `/school/`
- First registered user becomes admin with `is_staff=True`

## Environment Configuration

Required environment variables (`.env`):

```
DEBUG=True
SECRET_KEY=your-secret-key
POSTGRES_DB=examcore
POSTGRES_USER=examcore
POSTGRES_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST=localhost
EMAIL_PORT=1025
```

## Docker Services

- **db**: PostgreSQL 16 (port 5432)
- **web**: Django dev server (port 8000)
- **mailpit**: Email testing UI (port 8025) + SMTP (port 1025)

## Code Style Requirements

### Python

- **Line length**: 88 characters (Black default)
- **Formatter**: Black with target Python 3.11+
- **Import order**: isort with black profile
  - Sections: FUTURE, STDLIB, DJANGO, THIRDPARTY, FIRSTPARTY, LOCALFOLDER
  - Known first-party: `apps`, `config`
- **Linter**: flake8 with bugbear, comprehensions, simplify plugins
- **Type hints**: Optional but encouraged (mypy configured)

### Django Conventions

- Use class-based views (CBV) over function-based views
- Use `get_user_model()` instead of importing User directly
- Use `reverse()` or `redirect('namespace:name')` for URL resolution
- Form fields should include widget attrs with `class: 'input'` for Tailwind
- Models must define `__str__`, `class Meta` with `db_table`, `verbose_name`

### Template Conventions

- Use 2-space indentation (djhtml formatter)
- Extend `base.html` for all pages
- Use Tailwind CSS utility classes
- Template location: `templates/<app_name>/<template>.html`

## Git Workflow Rules

### Branch Naming

```
feature/<ticket-id>-<short-description>
bugfix/<ticket-id>-<short-description>
hotfix/<ticket-id>-<short-description>
release/<version>
```

Examples:
- `feature/EC-123-add-exam-scheduling`
- `bugfix/EC-456-fix-otp-expiry`
- `hotfix/EC-789-security-patch`

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`

**Scopes**: `accounts`, `exams`, `questions`, `results`, `config`, `theme`, `deps`

**Rules**:
- Subject line max 50 characters, imperative mood, no period
- Body wrapped at 72 characters, explain what and why
- Footer for issue references: `Closes #123`, `Fixes #456`

**Examples**:
```
feat(accounts): add password reset functionality

Implement password reset flow with email verification.
Users can request reset link valid for 24 hours.

Closes #45
```

```
fix(exams): prevent duplicate exam submissions

Add database constraint and view-level validation
to prevent students from submitting same exam twice.

Fixes #89
```

### Pull Request Guidelines

**Title Format**: `[<TYPE>] <Short Description>`

Examples:
- `[FEATURE] Add exam scheduling module`
- `[BUGFIX] Fix OTP verification timeout`
- `[REFACTOR] Restructure accounts app views`

**PR Description Template**:
```markdown
## Summary
Brief description of changes (2-3 sentences max)

## Changes
- Bullet point list of specific changes
- One change per line

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] Pre-commit hooks pass

## Related Issues
Closes #<issue-number>
```

**PR Rules**:
- Maximum 400 lines of code changes per PR
- One feature/fix per PR
- All CI checks must pass
- Requires at least one approval
- Squash merge to main branch

### Issue Guidelines

**Title Format**: `[<TYPE>] <Short Description>`

Types: `BUG`, `FEATURE`, `ENHANCEMENT`, `DOCS`, `QUESTION`

**Issue Template**:
```markdown
## Description
Clear description of the issue or feature request

## Steps to Reproduce (for bugs)
1. Step one
2. Step two
3. Expected vs actual behavior

## Acceptance Criteria (for features)
- [ ] Criterion 1
- [ ] Criterion 2

## Additional Context
Screenshots, logs, or related issues
```

## Restrictions & Rules

### Code Restrictions

1. **Never commit**:
   - `.env` files or any secrets/credentials
   - `db.sqlite3` or database dumps
   - `node_modules/`, `venv/`, `__pycache__/`
   - IDE configuration (`.idea/`, `.vscode/`)
   - Media uploads or user data

2. **Never modify without understanding**:
   - Migration files after they're committed
   - `config/settings/base.py` security settings
   - Custom User model after initial migration

3. **Always require**:
   - Tests for new features (minimum 80% coverage)
   - Type hints for public API functions
   - Docstrings for classes and public methods
   - Pre-commit hooks pass before committing

### Database Rules

1. **Migrations**:
   - Never edit migrations manually after commit
   - Always run `makemigrations` before `migrate`
   - Review migration SQL with `sqlmigrate` for production
   - Use `--name` flag for descriptive migration names

2. **Models**:
   - Always define `db_table` in Meta class
   - Use `BigAutoField` for primary keys (project default)
   - Add database indexes for frequently queried fields
   - Use `select_related`/`prefetch_related` to avoid N+1

### Security Requirements

1. **Authentication**:
   - Minimum 8 character passwords
   - OTP expires in 10 minutes
   - Session timeout after inactivity
   - CSRF protection on all forms

2. **Production**:
   - HTTPS required (`SECURE_SSL_REDIRECT=True`)
   - HSTS enabled (1 year)
   - Secure cookies (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`)
   - `DEBUG=False` always

3. **Input Validation**:
   - Use Django forms for all user input
   - Validate file uploads (type, size)
   - Sanitize search queries
   - Use parameterized queries (Django ORM handles this)

### Testing Requirements

1. **Test Organization**:
   - Place tests in `apps/<app>/tests/` directory or `tests.py`
   - Use `pytest` fixtures from `conftest.py`
   - Use `factory_boy` for model factories
   - Use `faker` for realistic test data

2. **Test Naming**:
   ```python
   class Test<ModelOrView>:
       def test_<action>_<expected_result>(self):
           pass
   ```

3. **Coverage**:
   - Minimum 80% coverage for new code
   - Critical paths (auth, payments) require 100%
   - Run `pytest --cov=apps --cov-report=html` for reports

## Django Management Commands

```bash
# Development
python manage.py shell_plus          # Enhanced shell (django-extensions)
python manage.py show_urls           # List all URL patterns
python manage.py graph_models -a     # Generate model diagrams

# Database
python manage.py dbshell             # Database CLI
python manage.py dumpdata <app>      # Export app data
python manage.py loaddata <fixture>  # Import fixture data
python manage.py flush               # Clear database (DANGER)

# Production
python manage.py check --deploy      # Security checklist
python manage.py clearsessions       # Remove expired sessions
```

## Debugging

```bash
# Django Debug Toolbar (development only)
# Access at: /__debug__/

# View SQL queries
python manage.py shell_plus --print-sql

# Check for issues
python manage.py check
python manage.py check --deploy  # Production security check

# Email testing with Mailpit
# Web UI: http://localhost:8025
# SMTP: localhost:1025
```

## Production Deployment Checklist

```bash
# 1. Set environment variables
export DJANGO_SETTINGS_MODULE=config.settings.production
export SECRET_KEY=<strong-random-key>
export DEBUG=False
export ALLOWED_HOSTS=your-domain.com

# 2. Collect static files
python manage.py collectstatic --noinput

# 3. Run migrations
python manage.py migrate --noinput

# 4. Security check
python manage.py check --deploy

# 5. Start with gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```
