# Migration to convert ExamAnswer.selected_option from CharField to FK

import django.db.models.deletion
from django.db import migrations, models


def migrate_answers_forward(apps, schema_editor):
    """
    Convert old "A", "B", "C", "D" selected_option values to QuestionOption FKs.
    This is a best-effort migration - answers that can't be converted will be set to NULL.
    """
    ExamAnswer = apps.get_model("attempts", "ExamAnswer")
    QuestionOption = apps.get_model("questions", "QuestionOption")

    for answer in ExamAnswer.objects.all():
        # Get the old selected_option value (was "A", "B", "C", "D")
        old_value = answer.selected_option_old
        if not old_value:
            continue

        # Get the question's options in order
        options = list(
            QuestionOption.objects.filter(question_id=answer.question_id).order_by("id")
        )

        # Map old key to option index: A=0, B=1, C=2, D=3
        key_to_index = {"A": 0, "B": 1, "C": 2, "D": 3}
        index = key_to_index.get(old_value)

        if index is not None and index < len(options):
            answer.selected_option_new = options[index]
            answer.save(update_fields=["selected_option_new"])


def migrate_answers_backward(apps, schema_editor):
    """Reverse migration - convert FK back to letter."""
    ExamAnswer = apps.get_model("attempts", "ExamAnswer")
    QuestionOption = apps.get_model("questions", "QuestionOption")

    for answer in ExamAnswer.objects.all():
        if not answer.selected_option_new_id:
            continue

        # Get all options for this question in order
        options = list(
            QuestionOption.objects.filter(question_id=answer.question_id).order_by("id")
        )

        # Find the index of the selected option
        index_to_key = {0: "A", 1: "B", 2: "C", 3: "D"}
        for i, opt in enumerate(options):
            if opt.id == answer.selected_option_new_id:
                answer.selected_option_old = index_to_key.get(i, "A")
                answer.save(update_fields=["selected_option_old"])
                break


class Migration(migrations.Migration):

    dependencies = [
        ("attempts", "0003_initial"),
        ("questions", "0005_remove_old_option_fields"),
    ]

    operations = [
        # Rename old field to selected_option_old
        migrations.RenameField(
            model_name="examanswer",
            old_name="selected_option",
            new_name="selected_option_old",
        ),
        # Add new FK field
        migrations.AddField(
            model_name="examanswer",
            name="selected_option_new",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="questions.questionoption",
            ),
        ),
        # Migrate data
        migrations.RunPython(migrate_answers_forward, migrate_answers_backward),
        # Remove old field
        migrations.RemoveField(
            model_name="examanswer",
            name="selected_option_old",
        ),
        # Rename new field
        migrations.RenameField(
            model_name="examanswer",
            old_name="selected_option_new",
            new_name="selected_option",
        ),
    ]
