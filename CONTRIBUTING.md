# Contributing to ExamCore

Thank you for your interest in contributing to ExamCore! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL (or SQLite for development)
- Node.js (for Tailwind CSS)
- Git

### Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/your-username/examcore.git
   cd examcore
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**

   ```bash
   pre-commit install
   ```

5. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

6. **Run migrations**

   ```bash
   python manage.py migrate
   ```

7. **Start the development server**

   ```bash
   python manage.py runserver
   ```

## Development Workflow

### Branch Naming

```
feature/<ticket-id>-<short-description>
bugfix/<ticket-id>-<short-description>
hotfix/<ticket-id>-<short-description>
```

Examples:
- `feature/EC-123-add-exam-scheduling`
- `bugfix/EC-456-fix-otp-expiry`

### Making Changes

1. Create a new branch from `main`
2. Make your changes
3. Write or update tests
4. Run the test suite: `pytest`
5. Commit your changes (pre-commit hooks will run automatically)
6. Push and create a pull request

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`

**Scopes**: `accounts`, `exams`, `questions`, `results`, `config`, `theme`, `deps`

**Example**:
```
feat(accounts): add password reset functionality

Implement password reset flow with email verification.
Users can request reset link valid for 24 hours.

Closes #45
```

## Code Style

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. The hooks run automatically on commit and include:

- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **bandit** - Security checks
- **djhtml** - Django template formatting

To run hooks manually:

```bash
pre-commit run --all-files
```

### Python Guidelines

- Follow PEP 8 (enforced by Black)
- Line length: 88 characters
- Use type hints where appropriate
- Write docstrings for classes and public methods

### Django Guidelines

- Use class-based views (CBV)
- Use `get_user_model()` instead of importing User directly
- Define `db_table` in model Meta classes
- Use `select_related`/`prefetch_related` to avoid N+1 queries

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps

# Run specific test file
pytest apps/accounts/tests.py

# Run in parallel
pytest -n auto
```

## Pull Request Guidelines

- Maximum 400 lines of code changes per PR
- One feature/fix per PR
- All CI checks must pass
- Include tests for new functionality
- Update documentation if needed

## Reporting Issues

When reporting issues, please include:

1. Description of the issue
2. Steps to reproduce
3. Expected vs actual behavior
4. Screenshots or logs if applicable

## Questions?

Feel free to open an issue with the `[QUESTION]` tag.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
