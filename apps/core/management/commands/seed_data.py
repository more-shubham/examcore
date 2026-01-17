"""
Management command to seed the database with sample data.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.academic.models import Class, Subject
from apps.questions.models import Question, QuestionOption

User = get_user_model()


def create_question_with_options(
    question_text, options_texts, correct_index, subject, creator
):
    """
    Create a question with options.

    Args:
        question_text: The question text
        options_texts: List of option texts ["opt1", "opt2", ...]
        correct_index: Index of correct option (0-based)
        subject: Subject instance
        creator: User who creates the question
    """
    question = Question.objects.create(
        question_text=question_text,
        subject=subject,
        created_by=creator,
    )

    correct_option = None
    for i, text in enumerate(options_texts):
        option = QuestionOption.objects.create(
            question=question,
            text=text,
        )
        if i == correct_index:
            correct_option = option

    question.correct_option = correct_option
    question.save()
    return question


class Command(BaseCommand):
    help = "Seed the database with sample data for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            QuestionOption.objects.all().delete()
            Question.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Existing questions cleared."))

        # Get or create admin user
        admin_user = User.objects.filter(role="admin").first()
        if not admin_user:
            self.stdout.write(
                self.style.WARNING("No admin user found. Please create one first.")
            )
            return

        # Get or create classes and subjects
        class_10, _ = Class.objects.get_or_create(
            name="Class 10", defaults={"description": "10th Grade"}
        )

        math_subject, _ = Subject.objects.get_or_create(
            name="Mathematics",
            assigned_class=class_10,
            defaults={"description": "Mathematics for Class 10"},
        )

        science_subject, _ = Subject.objects.get_or_create(
            name="Science",
            assigned_class=class_10,
            defaults={"description": "Science for Class 10"},
        )

        english_subject, _ = Subject.objects.get_or_create(
            name="English",
            assigned_class=class_10,
            defaults={"description": "English for Class 10"},
        )

        # Sample questions for Mathematics
        math_questions = [
            {
                "text": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "correct": 1,
            },
            {
                "text": "What is the square root of 144?",
                "options": ["10", "11", "12", "13"],
                "correct": 2,
            },
            {
                "text": "What is 15 x 3?",
                "options": ["30", "35", "45", "50"],
                "correct": 2,
            },
            {
                "text": "Solve: 2x + 5 = 11. What is x?",
                "options": ["2", "3", "4", "5"],
                "correct": 1,
            },
            {
                "text": "What is the value of pi (approximately)?",
                "options": ["2.14", "3.14", "4.14", "5.14"],
                "correct": 1,
            },
            {
                "text": "What is 25% of 80?",
                "options": ["15", "20", "25", "30"],
                "correct": 1,
            },
        ]

        # Sample questions for Science
        science_questions = [
            {
                "text": "What is the chemical symbol for water?",
                "options": ["H2O", "CO2", "NaCl", "O2"],
                "correct": 0,
            },
            {
                "text": "Which planet is known as the Red Planet?",
                "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                "correct": 1,
            },
            {
                "text": "What is the basic unit of life?",
                "options": ["Atom", "Cell", "Molecule", "Organ"],
                "correct": 1,
            },
            {
                "text": "What gas do plants absorb from the atmosphere?",
                "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"],
                "correct": 2,
            },
            {
                "text": "What is the speed of light?",
                "options": ["300,000 m/s", "300,000 km/s", "3,000 km/s", "30,000 km/s"],
                "correct": 1,
            },
        ]

        # Sample questions for English
        english_questions = [
            {
                "text": "Which of the following is a noun?",
                "options": ["Run", "Quickly", "Beautiful", "Book"],
                "correct": 3,
            },
            {
                "text": "What is the past tense of 'go'?",
                "options": ["Goes", "Going", "Went", "Gone"],
                "correct": 2,
            },
            {
                "text": "Choose the correct spelling:",
                "options": ["Recieve", "Receive", "Receve", "Receeve"],
                "correct": 1,
            },
            {
                "text": "What is a synonym for 'happy'?",
                "options": ["Sad", "Angry", "Joyful", "Tired"],
                "correct": 2,
            },
        ]

        # Create questions
        self.stdout.write("Creating sample questions...")

        for q_data in math_questions:
            create_question_with_options(
                question_text=q_data["text"],
                options_texts=q_data["options"],
                correct_index=q_data["correct"],
                subject=math_subject,
                creator=admin_user,
            )

        for q_data in science_questions:
            create_question_with_options(
                question_text=q_data["text"],
                options_texts=q_data["options"],
                correct_index=q_data["correct"],
                subject=science_subject,
                creator=admin_user,
            )

        for q_data in english_questions:
            create_question_with_options(
                question_text=q_data["text"],
                options_texts=q_data["options"],
                correct_index=q_data["correct"],
                subject=english_subject,
                creator=admin_user,
            )

        total_questions = (
            len(math_questions) + len(science_questions) + len(english_questions)
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {total_questions} sample questions!"
            )
        )
