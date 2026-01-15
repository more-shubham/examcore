<p align="center">
  <img src="static/logo-icon.svg" alt="ExamCore Logo" width="80">
</p>

<h1 align="center">ExamCore</h1>

<h3 align="center">Streamline Your Examination Process</h3>

<p align="center">
  The complete examination management system for schools, colleges, and universities.
  <br />
  <a href="#features"><strong>Explore Features</strong></a>
  &nbsp;&middot;&nbsp;
  <a href="#installation"><strong>Get Started</strong></a>
  &nbsp;&middot;&nbsp;
  <a href="#documentation"><strong>Documentation</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/python-3.11%2B-blue.svg" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/django-5.0-green.svg" alt="Django 5.0">
  <img src="https://img.shields.io/badge/status-alpha-orange.svg" alt="Status">
</p>

---

## Overview

**ExamCore** is an enterprise-grade, open-source examination management system built with Django. It provides a complete solution for educational institutions to create, manage, and conduct examinations with built-in anti-cheat features, role-based access control, and instant result generation.

### Why ExamCore?

- **Open Source** - Free to use, modify, and distribute
- **Self-Hosted** - Full control over your data and infrastructure
- **Modern Stack** - Built with Django 5.0 and Tailwind CSS
- **Scalable** - Designed to handle institutions of any size

---

## Features

<table>
<tr>
<td width="50%">

### Question Bank Management
Create, organize, and reuse questions across multiple exams. Support for multiple question types with rich text formatting.

- Multiple choice questions (MCQ)
- Categorize by subject and difficulty
- Import/Export questions
- Question versioning

</td>
<td width="50%">

### Anti-Cheat Protection
Built-in measures to ensure exam integrity and prevent cheating.

- Randomized question order per student
- Randomized option order for MCQs
- Time-limited exam sessions
- Single device enforcement

</td>
</tr>
<tr>
<td width="50%">

### Role-Based Access Control
Separate dashboards and permissions for different user types.

- **Admin** - Full system control
- **Examiner** - Create and manage exams
- **Teacher** - Manage questions and view results
- **Student** - Take exams and view scores

</td>
<td width="50%">

### Instant Results & Analytics
Automatic grading with detailed performance insights.

- Real-time score calculation
- Performance analytics
- Question-wise analysis
- Exportable reports

</td>
</tr>
</table>

---

## Tech Stack

| Category | Technology |
|----------|------------|
| **Backend** | Django 5.0, Python 3.11+ |
| **Database** | PostgreSQL |
| **Frontend** | Tailwind CSS, Alpine.js |
| **Authentication** | Django Auth + OTP Verification |
| **Task Queue** | Celery (optional) |
| **Deployment** | Docker, Gunicorn, Nginx |

---

## Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 14 or higher
- Node.js 18+ (for Tailwind CSS)
- Docker & Docker Compose (optional)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/your-username/examcore.git
cd examcore

# Copy environment file
cp .env.example .env

# Start with Docker Compose
docker-compose up -d

# Access the application
open http://localhost:8000
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/your-username/examcore.git
cd examcore

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Tailwind CSS Setup

```bash
# Install Tailwind dependencies
python manage.py tailwind install

# Start Tailwind in watch mode (development)
python manage.py tailwind start

# Build for production
python manage.py tailwind build
```

---

## Project Structure

```
examcore/
├── apps/                    # Django applications
│   ├── academic/           # Classes and subjects management
│   ├── attempts/           # Student exam attempts
│   ├── auth/               # Authentication (login, register, OTP)
│   ├── core/               # Core utilities and base models
│   ├── dashboards/         # Role-based dashboards
│   ├── exams/              # Exam management
│   ├── institution/        # Institution settings
│   ├── invitations/        # User invitations
│   ├── questions/          # Question bank
│   └── users/              # User management
├── config/                  # Project configuration
│   ├── settings/           # Environment-specific settings
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI entry point
├── static/                  # Static files (CSS, JS, images)
├── templates/               # HTML templates
├── media/                   # User uploads
└── manage.py               # Django management script
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `False` |
| `SECRET_KEY` | Django secret key | Required |
| `POSTGRES_DB` | Database name | `examcore` |
| `POSTGRES_USER` | Database user | `examcore` |
| `POSTGRES_PASSWORD` | Database password | Required |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `EMAIL_HOST` | SMTP server | `localhost` |
| `EMAIL_PORT` | SMTP port | `1025` |

---

## Usage

### First-Time Setup

1. **Register as Admin** - The first user to register becomes the institution admin
2. **Verify Email** - Enter the OTP sent to your email
3. **Set Up Institution** - Configure your institution name and details
4. **Access Dashboard** - Start managing your examination system

### Creating an Exam

1. Navigate to **Questions** to create your question bank
2. Go to **Exams** and click **Create Exam**
3. Add questions from your question bank
4. Set duration, passing score, and availability window
5. Assign to classes/students
6. Publish the exam

### Student Flow

1. Students receive invitation email
2. Register and verify account
3. Access **My Exams** from dashboard
4. Take available exams
5. View results immediately after submission

---

## API Documentation

ExamCore provides a RESTful API for integration with other systems.

```bash
# API endpoints (coming soon)
GET  /api/v1/exams/          # List all exams
POST /api/v1/exams/          # Create new exam
GET  /api/v1/questions/      # List questions
POST /api/v1/attempts/       # Submit exam attempt
```

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
flake8
black --check .
isort --check-only .
```

### Code Style

- Follow PEP 8 guidelines
- Use Black for formatting (line length: 88)
- Use isort for import sorting
- Write tests for new features

---

## Roadmap

- [ ] REST API for third-party integrations
- [ ] Multiple question types (fill-in-blank, essay, matching)
- [ ] Proctoring integration
- [ ] Mobile application
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Bulk import/export
- [ ] LTI integration for LMS

---

## Security

If you discover a security vulnerability, please send an email to security@example.com instead of using the issue tracker.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

- **Documentation**: [docs.examcore.dev](https://docs.examcore.dev)
- **Issues**: [GitHub Issues](https://github.com/your-username/examcore/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/examcore/discussions)

---

<p align="center">
  <sub>Built with Django and lots of coffee</sub>
</p>

<p align="center">
  <a href="https://github.com/your-username/examcore">
    <img src="https://img.shields.io/badge/Star_on_GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="Star on GitHub">
  </a>
</p>
