# Data migration to convert old option fields to QuestionOption model

from django.db import migrations


def migrate_options_forward(apps, schema_editor):
    """Create QuestionOption records from old option fields and set correct_option FK."""
    Question = apps.get_model("questions", "Question")
    QuestionOption = apps.get_model("questions", "QuestionOption")

    for question in Question.objects.all():
        # Get the old option texts
        old_options = [
            ("A", question.option_a),
            ("B", question.option_b),
            ("C", question.option_c),
            ("D", question.option_d),
        ]

        # Create QuestionOption for each non-empty old option
        created_options = {}
        for key, text in old_options:
            if text:  # Only create if there's text
                option = QuestionOption.objects.create(
                    question=question,
                    text=text,
                )
                created_options[key] = option

        # Set correct_option FK based on correct_option_old
        if (
            question.correct_option_old
            and question.correct_option_old in created_options
        ):
            question.correct_option = created_options[question.correct_option_old]
            question.save(update_fields=["correct_option"])


def migrate_options_backward(apps, schema_editor):
    """Reverse: Restore old option fields from QuestionOption records."""
    Question = apps.get_model("questions", "Question")
    QuestionOption = apps.get_model("questions", "QuestionOption")

    for question in Question.objects.all():
        options = list(QuestionOption.objects.filter(question=question).order_by("id"))

        # Map options back to option_a, option_b, option_c, option_d
        labels = ["A", "B", "C", "D"]
        for i, option in enumerate(options[:4]):
            setattr(question, f"option_{labels[i].lower()}", option.text)
            if question.correct_option_id == option.id:
                question.correct_option_old = labels[i]

        question.save()

    # Delete all QuestionOption records
    QuestionOption.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("questions", "0003_add_question_options_model"),
    ]

    operations = [
        migrations.RunPython(migrate_options_forward, migrate_options_backward),
    ]
