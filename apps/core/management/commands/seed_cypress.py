"""
Management command to seed the database with CSV data for Cypress E2E testing.

Usage:
    python manage.py seed_cypress           # Clear all and seed fresh
    python manage.py seed_cypress --no-clear   # Append mode
    python manage.py seed_cypress --dry-run    # Validate only
"""

import csv
import json
import re
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.academic.models import Class, Subject
from apps.attempts.models import ExamAnswer, ExamAttempt
from apps.exams.models import Exam, ExamQuestion
from apps.institution.models import Institution
from apps.questions.models import Question, QuestionOption

User = get_user_model()

# Base directory for seed data
SEED_DIR = Path(settings.BASE_DIR) / "seed" / "data"
CYPRESS_FIXTURES_DIR = Path(settings.BASE_DIR) / "cypress" / "fixtures"


def parse_relative_time(time_str):
    """
    Parse relative time notation into absolute datetime.

    Formats:
        now          -> current time
        +2d          -> 2 days from now
        -1h          -> 1 hour ago
        +2d2h        -> 2 days and 2 hours from now
        +1d2h30m     -> 1 day, 2 hours, 30 minutes from now
    """
    if time_str == "now":
        return timezone.now()

    # Match relative time pattern
    pattern = r"^([+-])(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?$"
    match = re.match(pattern, time_str)

    if not match:
        raise ValueError(f"Invalid time format: {time_str}")

    sign, days, hours, minutes = match.groups()
    days = int(days) if days else 0
    hours = int(hours) if hours else 0
    minutes = int(minutes) if minutes else 0

    delta = timedelta(days=days, hours=hours, minutes=minutes)
    now = timezone.now()

    if sign == "+":
        return now + delta
    return now - delta


def parse_bool(value):
    """Parse boolean string to Python bool."""
    return value.lower() in ("true", "1", "yes")


class Command(BaseCommand):
    help = "Seed the database with CSV data for Cypress E2E testing"

    def __init__(self):
        super().__init__()
        # Reference maps for FK lookups
        self.class_map = {}  # id -> Class instance
        self.subject_map = {}  # id -> Subject instance
        self.user_map = {}  # id -> User instance
        self.question_map = {}  # id -> Question instance
        self.exam_map = {}  # id -> Exam instance
        self.credentials = {}  # role -> {email, password}

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-clear",
            action="store_true",
            help="Don't clear existing data before seeding",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate CSV files without making changes",
        )

    def read_csv(self, filename):
        """Read a CSV file and return list of dicts."""
        filepath = SEED_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")

        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def clear_all_data(self):
        """Clear all data in reverse order of dependencies."""
        self.stdout.write("Clearing existing data...")

        # Clear in reverse dependency order
        ExamAnswer.objects.all().delete()
        ExamAttempt.objects.all().delete()
        ExamQuestion.objects.all().delete()
        Exam.objects.all().delete()
        QuestionOption.objects.all().delete()
        Question.objects.all().delete()
        User.objects.all().delete()
        Subject.objects.all().delete()
        Class.objects.all().delete()
        Institution.objects.all().delete()

        # Clear caches
        Institution.clear_cache()

        self.stdout.write(self.style.SUCCESS("All data cleared."))

    def seed_institution(self, dry_run=False):
        """Seed institution from CSV."""
        self.stdout.write("Seeding institution...")
        rows = self.read_csv("01_institution.csv")

        if not rows:
            raise ValueError("01_institution.csv is empty")

        row = rows[0]  # Only one institution (singleton)

        if dry_run:
            self.stdout.write(f"  Would create institution: {row['name']}")
            return

        Institution.objects.create(
            name=row["name"],
            address=row.get("address", ""),
            phone=row.get("phone", ""),
            email=row.get("email", ""),
            website=row.get("website", ""),
            established_year=(
                int(row["established_year"]) if row.get("established_year") else None
            ),
            logo="institution/logo.png",  # Logo copied by Cypress seedDatabase task
        )
        self.stdout.write(self.style.SUCCESS(f"  Created: {row['name']}"))

    def seed_classes(self, dry_run=False):
        """Seed classes from CSV."""
        self.stdout.write("Seeding classes...")
        rows = self.read_csv("02_classes.csv")

        for row in rows:
            if dry_run:
                self.stdout.write(f"  Would create class: {row['name']}")
                self.class_map[row["id"]] = None
                continue

            cls = Class.objects.create(
                name=row["name"],
                description=row.get("description", ""),
                order=int(row.get("order", 0)),
                is_active=parse_bool(row.get("is_active", "true")),
            )
            self.class_map[row["id"]] = cls
            self.stdout.write(self.style.SUCCESS(f"  Created: {cls.name}"))

    def seed_subjects(self, dry_run=False):
        """Seed subjects from CSV."""
        self.stdout.write("Seeding subjects...")
        rows = self.read_csv("03_subjects.csv")

        for row in rows:
            class_ref = row["class_ref"]
            if class_ref not in self.class_map:
                raise ValueError(f"Unknown class reference: {class_ref}")

            if dry_run:
                self.stdout.write(
                    f"  Would create subject: {row['name']} ({class_ref})"
                )
                self.subject_map[row["id"]] = None
                continue

            subject = Subject.objects.create(
                name=row["name"],
                description=row.get("description", ""),
                assigned_class=self.class_map[class_ref],
                is_active=parse_bool(row.get("is_active", "true")),
            )
            self.subject_map[row["id"]] = subject
            self.stdout.write(
                self.style.SUCCESS(f"  Created: {subject.name} ({class_ref})")
            )

    def seed_users(self, dry_run=False):
        """Seed users from CSV with password hashing."""
        self.stdout.write("Seeding users...")
        rows = self.read_csv("04_users.csv")

        for row in rows:
            role = row["role"]
            class_ref = row.get("class_ref", "")
            assigned_class = None

            if class_ref and class_ref in self.class_map:
                assigned_class = self.class_map[class_ref]

            if dry_run:
                self.stdout.write(f"  Would create user: {row['email']} ({role})")
                self.user_map[row["id"]] = None
                continue

            user = User.objects.create(
                email=row["email"],
                username=row["username"],
                password=make_password(row["password"]),  # Hash the password
                first_name=row.get("first_name", ""),
                last_name=row.get("last_name", ""),
                role=role,
                phone=row.get("phone", ""),
                assigned_class=assigned_class,
                is_staff=parse_bool(row.get("is_staff", "false")),
                is_active=parse_bool(row.get("is_active", "true")),
            )
            self.user_map[row["id"]] = user

            # Store credentials for fixtures (plain password for testing)
            if role not in self.credentials:
                self.credentials[role] = {
                    "email": row["email"],
                    "password": row["password"],
                }

            self.stdout.write(self.style.SUCCESS(f"  Created: {user.email} ({role})"))

    def seed_questions(self, dry_run=False):
        """Seed questions and options from CSV."""
        self.stdout.write("Seeding questions...")
        rows = self.read_csv("05_questions.csv")

        for row in rows:
            subject_ref = row["subject_ref"]
            creator_ref = row["created_by_ref"]

            if subject_ref not in self.subject_map:
                raise ValueError(f"Unknown subject reference: {subject_ref}")
            if creator_ref not in self.user_map:
                raise ValueError(f"Unknown user reference: {creator_ref}")

            if dry_run:
                self.stdout.write(
                    f"  Would create question: {row['question_text'][:50]}..."
                )
                self.question_map[row["id"]] = None
                continue

            # Create question
            question = Question.objects.create(
                question_text=row["question_text"],
                subject=self.subject_map[subject_ref],
                created_by=self.user_map[creator_ref],
                is_active=parse_bool(row.get("is_active", "true")),
            )

            # Create options
            option_texts = [
                row["option_a"],
                row["option_b"],
                row["option_c"],
                row["option_d"],
            ]
            correct_letter = row["correct_option"].lower()
            correct_index = ord(correct_letter) - ord("a")

            correct_option = None
            for i, text in enumerate(option_texts):
                option = QuestionOption.objects.create(
                    question=question,
                    text=text,
                )
                if i == correct_index:
                    correct_option = option

            # Set correct option
            question.correct_option = correct_option
            question.save()

            self.question_map[row["id"]] = question

        self.stdout.write(self.style.SUCCESS(f"  Created {len(rows)} questions"))

    def seed_exams(self, dry_run=False):
        """Seed exams from CSV with relative time parsing."""
        self.stdout.write("Seeding exams...")
        rows = self.read_csv("06_exams.csv")

        for row in rows:
            subject_ref = row["subject_ref"]
            creator_ref = row["created_by_ref"]

            if subject_ref not in self.subject_map:
                raise ValueError(f"Unknown subject reference: {subject_ref}")
            if creator_ref not in self.user_map:
                raise ValueError(f"Unknown user reference: {creator_ref}")

            start_time = parse_relative_time(row["start_time"])
            end_time = parse_relative_time(row["end_time"])

            if dry_run:
                self.stdout.write(f"  Would create exam: {row['title']}")
                self.exam_map[row["id"]] = None
                continue

            random_count = row.get("random_question_count", "")
            exam = Exam.objects.create(
                title=row["title"],
                description=row.get("description", ""),
                subject=self.subject_map[subject_ref],
                start_time=start_time,
                end_time=end_time,
                use_random_questions=parse_bool(
                    row.get("use_random_questions", "true")
                ),
                random_question_count=int(random_count) if random_count else None,
                status=row.get("status", "draft"),
                created_by=self.user_map[creator_ref],
                is_active=parse_bool(row.get("is_active", "true")),
            )
            self.exam_map[row["id"]] = exam
            self.stdout.write(self.style.SUCCESS(f"  Created: {exam.title}"))

    def seed_exam_questions(self, dry_run=False):
        """Seed manual exam-question assignments from CSV."""
        self.stdout.write("Seeding exam questions...")
        rows = self.read_csv("07_exam_questions.csv")

        for row in rows:
            exam_ref = row["exam_ref"]
            question_ref = row["question_ref"]

            if exam_ref not in self.exam_map:
                raise ValueError(f"Unknown exam reference: {exam_ref}")
            if question_ref not in self.question_map:
                raise ValueError(f"Unknown question reference: {question_ref}")

            if dry_run:
                self.stdout.write(
                    f"  Would assign question {question_ref} to {exam_ref}"
                )
                continue

            ExamQuestion.objects.create(
                exam=self.exam_map[exam_ref],
                question=self.question_map[question_ref],
                order=int(row.get("order", 0)),
            )

        self.stdout.write(
            self.style.SUCCESS(f"  Created {len(rows)} exam-question assignments")
        )

    def seed_exam_attempts(self, dry_run=False):
        """Seed exam attempts from CSV."""
        self.stdout.write("Seeding exam attempts...")
        rows = self.read_csv("08_exam_attempts.csv")

        for row in rows:
            student_ref = row["student_ref"]
            exam_ref = row["exam_ref"]

            if student_ref not in self.user_map:
                raise ValueError(f"Unknown student reference: {student_ref}")
            if exam_ref not in self.exam_map:
                raise ValueError(f"Unknown exam reference: {exam_ref}")

            if dry_run:
                self.stdout.write(
                    f"  Would create attempt: {student_ref} -> {exam_ref}"
                )
                continue

            exam = self.exam_map[exam_ref]
            student = self.user_map[student_ref]

            ExamAttempt.objects.create(
                exam=exam,
                student=student,
                status=row.get("status", "submitted"),
                score=int(row.get("score", 0)),
                total_questions=int(row.get("total_questions", 0)),
                submitted_at=timezone.now() - timedelta(days=1),  # Submitted yesterday
            )

        self.stdout.write(self.style.SUCCESS(f"  Created {len(rows)} exam attempts"))

    def generate_credentials_fixture(self):
        """Generate cypress/fixtures/credentials.json."""
        self.stdout.write("Generating Cypress credentials fixture...")

        # Ensure directory exists
        CYPRESS_FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

        filepath = CYPRESS_FIXTURES_DIR / "credentials.json"
        with open(filepath, "w") as f:
            json.dump(self.credentials, f, indent=2)

        self.stdout.write(self.style.SUCCESS(f"  Generated: {filepath}"))

    @transaction.atomic
    def handle(self, *args, **options):
        no_clear = options.get("no_clear", False)
        dry_run = options.get("dry_run", False)

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made"))

        # Validate seed directory exists
        if not SEED_DIR.exists():
            self.stderr.write(self.style.ERROR(f"Seed directory not found: {SEED_DIR}"))
            return

        try:
            # Clear existing data unless --no-clear
            if not no_clear and not dry_run:
                self.clear_all_data()

            # Seed in order of dependencies
            self.seed_institution(dry_run)
            self.seed_classes(dry_run)
            self.seed_subjects(dry_run)
            self.seed_users(dry_run)
            self.seed_questions(dry_run)
            self.seed_exams(dry_run)
            self.seed_exam_questions(dry_run)
            self.seed_exam_attempts(dry_run)

            # Generate Cypress fixtures
            if not dry_run:
                self.generate_credentials_fixture()

            # Summary
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("=" * 50))
            self.stdout.write(self.style.SUCCESS("Seed completed successfully!"))
            self.stdout.write(self.style.SUCCESS("=" * 50))
            self.stdout.write("")
            self.stdout.write("Summary:")
            self.stdout.write(f"  Classes: {len(self.class_map)}")
            self.stdout.write(f"  Subjects: {len(self.subject_map)}")
            self.stdout.write(f"  Users: {len(self.user_map)}")
            self.stdout.write(f"  Questions: {len(self.question_map)}")
            self.stdout.write(f"  Exams: {len(self.exam_map)}")
            self.stdout.write("")
            self.stdout.write(
                "Test credentials saved to: cypress/fixtures/credentials.json"
            )

        except FileNotFoundError as e:
            self.stderr.write(self.style.ERROR(str(e)))
        except ValueError as e:
            self.stderr.write(self.style.ERROR(f"Validation error: {e}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {e}"))
            raise
