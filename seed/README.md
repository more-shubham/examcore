# ExamCore Seed Data

This directory contains CSV seed data files for populating the ExamCore database with realistic test data for Cypress E2E testing.

## Overview

The seed data represents a fictional MSBTE (Maharashtra State Board of Technical Education) polytechnic college with:
- **Institution**: Model Polytechnic College, Mumbai
- **6 Semesters**: 3rd and 4th semester for CO, IF, and EJ branches
- **24 Subjects**: MSBTE diploma curriculum subjects
- **33 Users**: Admin, Examiners, Teachers, and Students
- **150+ Questions**: Technical diploma-level MCQs
- **12 Exams**: Various states (draft, upcoming, running, ended)

## Data Context

### MSBTE Polytechnic Context
- **Branches**: Computer Engineering (CO), Information Technology (IF), Electronics & Telecom (EJ)
- **Semesters**: 3rd and 4th semester focus
- **Subjects**: Based on MSBTE I-Scheme curriculum
- **Names**: Marathi surnames for authenticity (Patil, Kulkarni, Deshmukh, etc.)

## Data Files

Files are numbered to indicate the loading order (respecting foreign key constraints):

| File | Description | Records |
|------|-------------|---------|
| `01_institution.csv` | Model Polytechnic College details | 1 |
| `02_classes.csv` | 6 semesters (3 branches x 2 semesters) | 6 |
| `03_subjects.csv` | MSBTE diploma subjects | 24 |
| `04_users.csv` | Admin, Examiners, Teachers, Students | 33 |
| `05_questions.csv` | Technical MCQ questions | 150+ |
| `06_exams.csv` | Exams with various statuses | 12 |
| `07_exam_questions.csv` | Manual exam-question assignments | 20 |
| `08_exam_attempts.csv` | Completed student attempts | 14 |

## Semesters/Classes

| ID | Name | Branch |
|----|------|--------|
| co_sem3 | CO - 3rd Semester | Computer Engineering |
| co_sem4 | CO - 4th Semester | Computer Engineering |
| if_sem3 | IF - 3rd Semester | Information Technology |
| if_sem4 | IF - 4th Semester | Information Technology |
| ej_sem3 | EJ - 3rd Semester | Electronics & Telecom |
| ej_sem4 | EJ - 4th Semester | Electronics & Telecom |

## Subjects by Branch

### Computer Engineering (CO)
- **3rd Sem**: Data Structures (DSU), Digital Techniques (DTE), OOP with Java (OOJ), Computer Graphics (CGR)
- **4th Sem**: DBMS (DMS), Software Engineering (SEN), Operating System (OSY), Computer Networks (CNS)

### Information Technology (IF)
- **3rd Sem**: Data Structures (DSU), Python Programming (PPR), Web Development (WBD), DBMS (DMS)
- **4th Sem**: Advanced DBMS (ADB), Java Programming (JAV), Software Testing (STE), Mobile App Dev (MAD)

### Electronics & Telecom (EJ)
- **3rd Sem**: Digital Electronics (DEL), Microprocessor (MIC), Electronic Circuits (ECA), Network Analysis (NAL)
- **4th Sem**: Microcontroller (MCO), Digital Communication (DCO), Linear IC (LIC), Embedded Systems (EMS)

## User Credentials

### Test Accounts

| Role | Name | Email | Password |
|------|------|-------|----------|
| Admin | Rajesh Patil | `admin@modelpolytechnic.edu.in` | `Admin@123` |
| Examiner | Priya Kulkarni | `examiner@modelpolytechnic.edu.in` | `Examiner@123` |
| Examiner 2 | Vikram Deshmukh | `examiner2@modelpolytechnic.edu.in` | `Examiner@123` |
| Teacher (DBMS) | Santosh Jadhav | `dbms.teacher@modelpolytechnic.edu.in` | `Teacher@123` |
| Teacher (DSU) | Aarti Shinde | `dsu.teacher@modelpolytechnic.edu.in` | `Teacher@123` |
| Teacher (OOP) | Mahesh Pawar | `oop.teacher@modelpolytechnic.edu.in` | `Teacher@123` |
| Teacher (DTE) | Kavita Joshi | `digital.teacher@modelpolytechnic.edu.in` | `Teacher@123` |
| Student (CO Sem3) | Rahul Patil | `rahul.patil@modelpolytechnic.edu.in` | `Student@123` |

All students use password: `Student@123`

## Usage

### Seed the Database

```bash
# Clear all data and seed fresh (recommended for testing)
python manage.py seed_cypress

# Append mode (don't clear existing data)
python manage.py seed_cypress --no-clear

# Dry run (validate CSV files only, no database changes)
python manage.py seed_cypress --dry-run

# Verbose output
python manage.py seed_cypress --verbosity 2
```

### Run Cypress Tests

After seeding:

```bash
# Start Django server
python manage.py runserver

# In another terminal, run Cypress tests
npx cypress run          # Headless mode
npx cypress open         # Interactive mode

# Run specific test suites
npx cypress run --spec "cypress/e2e/01-setup/**"     # Setup tests
npx cypress run --spec "cypress/e2e/02-admin/**"     # Admin tests
npx cypress run --spec "cypress/e2e/03-examiner/**"  # Examiner tests
npx cypress run --spec "cypress/e2e/04-teacher/**"   # Teacher tests
npx cypress run --spec "cypress/e2e/05-student/**"   # Student tests
```

## Test Coverage

### Test Suites

| Suite | Tests | Description |
|-------|-------|-------------|
| `01-setup/` | Registration, Login, Password Reset | Authentication flows |
| `02-admin/` | Dashboard, Classes, Subjects, Users | Admin management |
| `03-examiner/` | Dashboard, Questions, Exams | Examiner workflows |
| `04-teacher/` | Dashboard | Teacher placeholder |
| `05-student/` | Dashboard, Exam List, Take Exam, Results | Student exam flow |

### Features Tested
- Admin registration with OTP verification
- Institution setup with logo upload
- Class/semester CRUD operations
- Subject management per semester
- User invitations (examiners, teachers, students)
- Question bank management
- Exam creation and publishing
- Student exam-taking flow
- Result viewing

## CSV Schema Details

### Reference Fields

CSV files use reference IDs (e.g., `co_sem3`, `examiner_01`) to establish relationships:

- `class_ref` - References `id` in `02_classes.csv`
- `subject_ref` - References `id` in `03_subjects.csv`
- `created_by_ref` - References `id` in `04_users.csv`
- `exam_ref` - References `id` in `06_exams.csv`
- `question_ref` - References `id` in `05_questions.csv`
- `student_ref` - References `id` in `04_users.csv`

### Time Fields

Exam times in `06_exams.csv` support relative time notation:

| Format | Meaning |
|--------|---------|
| `now` | Current time |
| `+2d` | 2 days from now |
| `-1h` | 1 hour ago |
| `+2d2h` | 2 days and 2 hours from now |
| `-7d3h` | 7 days and 3 hours ago |
| `+1d2h30m` | 1 day, 2 hours, 30 minutes from now |

### Question Format

Questions use columns `option_a`, `option_b`, `option_c`, `option_d` for the four choices.
The `correct_option` field contains `a`, `b`, `c`, or `d` to indicate the correct answer.

## Exam States

The seed data includes exams in all possible states:

| Status | Count | Description |
|--------|-------|-------------|
| Draft | 2 | Not yet published, not visible to students |
| Upcoming | 3 | Published but start time is in the future |
| Running | 2 | Currently active, students can take the exam |
| Ended | 3 | Past the end time, results available |
| Manual Selection | 2 | Using manually assigned questions instead of random |

## Fixtures

The seed command also generates Cypress fixtures:

### `cypress/fixtures/credentials.json`
Contains login credentials for all roles for easy test access.

### `cypress/fixtures/test-data.json`
Contains comprehensive test data including institution info, class details, subjects, and sample questions.

### `cypress/fixtures/logo.svg` and `logo.png`
Institution logo files for upload testing.

## Data Validation

The management command validates:

1. All referenced IDs exist
2. Foreign key constraints are satisfied
3. Required fields are present
4. Time formats are valid
5. Role values match the User.Role choices

## Notes

- All `.edu.in` email domains are used for authenticity
- Phone numbers use the Indian format (+91-XX-XXXXXXXX)
- Questions are based on MSBTE I-Scheme curriculum
- Names use common Marathi surnames for realism
- Institution established in 1985 (historical context)
