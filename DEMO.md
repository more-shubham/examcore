# ExamCore Demo Guide

This guide helps you quickly test ExamCore's features.

## Quick Start (Docker)

```bash
# Clone and start
git clone https://github.com/more-shubham/examcore.git
cd examcore
docker-compose up -d

# Wait for services to start (about 30 seconds)
# Then seed the demo data
docker-compose exec web python manage.py seed_cypress

# Open in browser
open http://localhost:8000
```

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@modelpolytechnic.edu.in | Admin@123 |
| Examiner | examiner@modelpolytechnic.edu.in | Examiner@123 |
| Teacher | dbms.teacher@modelpolytechnic.edu.in | Teacher@123 |
| Student | rahul.patil@modelpolytechnic.edu.in | Student@123 |

## Test Scenarios

### 1. Admin Flow

Login as **Admin** to:
- View system dashboard with statistics
- Manage examiners (add/remove)
- Manage teachers (add/remove, assign subjects)
- Manage classes and subjects
- View all students and results

**Try this:**
1. Login as admin
2. Go to "Examiners" - view/add examiner accounts
3. Go to "Teachers" - assign subjects to teachers
4. Go to "Classes" - view class structure

### 2. Examiner Flow

Login as **Examiner** to:
- Create and manage exams
- Add questions to question bank
- Assign exams to classes
- View exam results

**Try this:**
1. Login as examiner
2. Go to "Questions" - create a new MCQ question
3. Go to "Exams" - create a new exam
4. Add questions to the exam
5. Publish the exam

### 3. Teacher Flow

Login as **Teacher** to:
- View questions for assigned subjects
- View exams containing their subject questions
- View student results for their subjects

**Try this:**
1. Login as teacher
2. View "Questions" (read-only access)
3. View "Exams" (read-only access)
4. Check "Results" for your students

### 4. Student Flow

Login as **Student** to:
- View available exams
- Take exams with anti-cheat features
- View results and scores

**Try this:**
1. Login as student
2. Go to "My Exams"
3. Start an available exam
4. Answer questions and submit
5. View your result immediately

## Email Testing

ExamCore uses **Mailpit** for email testing in development.

- **Web UI**: http://localhost:8025
- View all OTP verification emails
- View password reset emails
- View invitation emails

## Anti-Cheat Features Demo

When taking an exam as a student:
- Questions are randomized per student
- Answer options are shuffled
- Timer enforces time limits
- Single session enforcement

## Services

| Service | URL | Purpose |
|---------|-----|---------|
| Web App | http://localhost:8000 | Main application |
| Mailpit UI | http://localhost:8025 | Email testing |
| PostgreSQL | localhost:5432 | Database |

## Stopping the Demo

```bash
docker-compose down
```

To remove all data:
```bash
docker-compose down -v
```

## Running Tests

```bash
# Run all 304 E2E tests
npm install
npx cypress run

# Run specific test suite
npx cypress run --spec "cypress/e2e/01-auth/*.cy.js"
```

## Troubleshooting

**Port already in use:**
```bash
docker-compose down
lsof -i :8000  # Check what's using port
docker-compose up -d
```

**Database issues:**
```bash
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py seed_cypress
```

**View logs:**
```bash
docker-compose logs -f web
```
