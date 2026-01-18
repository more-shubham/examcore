import json

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Min
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from apps.academic.models import Class
from apps.core.mixins import ResultsViewerRequiredMixin, StudentRequiredMixin
from apps.core.services.pdf import PDFService
from apps.exams.models import Exam
from apps.institution.models import Institution

from .models import ExamAnswer, ExamAttempt


class StudentExamListView(StudentRequiredMixin, View):
    """List available exams for student."""

    template_name = "attempts/exam_list.html"

    def get(self, request):
        user = request.user

        # Get official exams
        official_exams = Exam.objects.filter(
            subject__assigned_class=user.assigned_class,
            status=Exam.Status.PUBLISHED,
            is_active=True,
            exam_type=Exam.ExamType.OFFICIAL,
        ).select_related("subject", "subject__assigned_class")

        # Get practice exams
        practice_exams = Exam.objects.filter(
            subject__assigned_class=user.assigned_class,
            status=Exam.Status.PUBLISHED,
            is_active=True,
            exam_type=Exam.ExamType.PRACTICE,
        ).select_related("subject", "subject__assigned_class")

        # Get attempts for official exams (only latest)
        official_attempts = {
            a.exam_id: a
            for a in ExamAttempt.objects.filter(
                student=user, exam__in=official_exams
            ).order_by("-started_at")
        }

        # Get all attempts for practice exams
        practice_attempts = {}
        for attempt in ExamAttempt.objects.filter(
            student=user, exam__in=practice_exams
        ).order_by("-started_at"):
            if attempt.exam_id not in practice_attempts:
                practice_attempts[attempt.exam_id] = []
            practice_attempts[attempt.exam_id].append(attempt)

        # Categorize official exams
        upcoming_exams = []
        active_exams = []
        past_exams = []

        for exam in official_exams:
            exam_data = {
                "exam": exam,
                "attempt": official_attempts.get(exam.id),
            }
            if exam.is_upcoming:
                upcoming_exams.append(exam_data)
            elif exam.is_running:
                active_exams.append(exam_data)
            else:
                past_exams.append(exam_data)

        # Categorize practice exams
        practice_active = []
        practice_available = []

        for exam in practice_exams:
            attempts_list = practice_attempts.get(exam.id, [])
            # Get the latest attempt (if any)
            latest_attempt = attempts_list[0] if attempts_list else None
            # Check if there's an in-progress attempt
            in_progress_attempt = None
            for att in attempts_list:
                if att.status == ExamAttempt.Status.IN_PROGRESS:
                    in_progress_attempt = att
                    break

            exam_data = {
                "exam": exam,
                "attempt": in_progress_attempt or latest_attempt,
                "attempts": attempts_list,
                "attempt_count": len(attempts_list),
                "has_in_progress": in_progress_attempt is not None,
            }

            if exam.is_running:
                practice_active.append(exam_data)
            elif not exam.is_upcoming and attempts_list:
                # Past practice exams still available if they've been attempted
                practice_available.append(exam_data)

        return render(
            request,
            self.template_name,
            {
                "upcoming_exams": upcoming_exams,
                "active_exams": active_exams,
                "past_exams": past_exams,
                "practice_active": practice_active,
                "practice_available": practice_available,
            },
        )


class StudentStartExamView(StudentRequiredMixin, View):
    """Start exam confirmation page."""

    template_name = "attempts/exam_start.html"

    def get_exam(self, pk):
        return get_object_or_404(
            Exam.objects.select_related("subject", "subject__assigned_class"),
            pk=pk,
            status=Exam.Status.PUBLISHED,
            is_active=True,
        )

    def get(self, request, pk):
        exam = self.get_exam(pk)

        if exam.subject.assigned_class != request.user.assigned_class:
            messages.error(request, "You are not enrolled in this class.")
            return redirect("attempts:list")

        if not exam.is_running:
            if exam.is_upcoming:
                messages.info(request, "This exam has not started yet.")
            else:
                messages.warning(request, "This exam has ended.")
            return redirect("attempts:list")

        # Get all attempts for this exam
        attempts = ExamAttempt.objects.filter(exam=exam, student=request.user).order_by(
            "-started_at"
        )

        # Check for in-progress attempt
        in_progress = attempts.filter(status=ExamAttempt.Status.IN_PROGRESS).first()
        if in_progress:
            return redirect("attempts:take", pk=exam.pk)

        # For official exams, redirect to result if already completed
        if not exam.is_practice and attempts.exists():
            return redirect("attempts:result", pk=exam.pk)

        # For practice exams, show previous attempt count
        context = {
            "exam": exam,
            "previous_attempts": attempts.count(),
            "best_score": None,
        }

        # Calculate best score for practice exams
        if exam.is_practice and attempts.exists():
            completed = attempts.exclude(status=ExamAttempt.Status.IN_PROGRESS)
            if completed.exists():
                best = max(completed, key=lambda a: a.percentage_score)
                context["best_score"] = best.percentage_score

        return render(request, self.template_name, context)

    def post(self, request, pk):
        exam = self.get_exam(pk)

        if exam.subject.assigned_class != request.user.assigned_class:
            messages.error(request, "You are not enrolled in this class.")
            return redirect("attempts:list")

        if not exam.is_running:
            messages.error(request, "This exam is not available.")
            return redirect("attempts:list")

        # Check for existing in-progress attempt
        in_progress = ExamAttempt.objects.filter(
            exam=exam,
            student=request.user,
            status=ExamAttempt.Status.IN_PROGRESS,
        ).first()

        if in_progress:
            # Resume existing attempt
            return redirect("attempts:take", pk=exam.pk)

        # For official exams, check if already completed
        if not exam.is_practice:
            existing = ExamAttempt.objects.filter(
                exam=exam, student=request.user
            ).first()
            if existing:
                messages.info(request, "You have already completed this exam.")
                return redirect("attempts:result", pk=exam.pk)

        # Create new attempt
        ExamAttempt.create_attempt(exam, request.user)
        return redirect("attempts:take", pk=exam.pk)


class StudentExamView(StudentRequiredMixin, View):
    """Main exam-taking interface."""

    template_name = "attempts/exam_take.html"

    def get_in_progress_attempt(self, exam, user):
        """Get the in-progress attempt for an exam."""
        return (
            ExamAttempt.objects.filter(
                exam=exam,
                student=user,
                status=ExamAttempt.Status.IN_PROGRESS,
            )
            .select_related("exam")
            .first()
        )

    def get(self, request, pk):
        exam = get_object_or_404(
            Exam.objects.select_related("subject", "subject__assigned_class"),
            pk=pk,
            status=Exam.Status.PUBLISHED,
        )

        # Get in-progress attempt (for both official and practice exams)
        attempt = self.get_in_progress_attempt(exam, request.user)

        if not attempt:
            return redirect("attempts:start", pk=pk)

        if attempt.is_time_expired:
            attempt.status = ExamAttempt.Status.TIMED_OUT
            attempt.submitted_at = exam.end_time
            attempt.save()
            attempt.calculate_score()
            messages.warning(
                request, "Time expired. Your exam has been auto-submitted."
            )
            return redirect("attempts:result", pk=pk)

        questions_data = attempt.get_all_questions_with_options()
        time_remaining = (exam.end_time - timezone.now()).total_seconds()

        return render(
            request,
            self.template_name,
            {
                "exam": exam,
                "attempt": attempt,
                "questions_data": questions_data,
                "time_remaining": max(0, int(time_remaining)),
            },
        )

    def post(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)
        attempt = self.get_in_progress_attempt(exam, request.user)
        if not attempt:
            return redirect("attempts:start", pk=pk)

        if attempt.status != ExamAttempt.Status.IN_PROGRESS:
            return redirect("attempts:result", pk=pk)

        # Save answers - value is now the option ID (integer)
        for key, value in request.POST.items():
            if key.startswith("question_") and value:
                question_id = key.replace("question_", "")
                try:
                    option_id = int(value)
                    ExamAnswer.objects.update_or_create(
                        attempt=attempt,
                        question_id=question_id,
                        defaults={"selected_option_id": option_id},
                    )
                except (ValueError, TypeError):
                    continue

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(request, self.template_name, {"saved": True})

        return redirect("attempts:take", pk=pk)


class StudentSubmitExamView(StudentRequiredMixin, View):
    """Submit exam and finalize score."""

    def post(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk)

        # Get in-progress attempt
        attempt = ExamAttempt.objects.filter(
            exam=exam,
            student=request.user,
            status=ExamAttempt.Status.IN_PROGRESS,
        ).first()

        if not attempt:
            messages.error(request, "No active exam attempt found.")
            return redirect("attempts:list")

        # Save answers - value is now the option ID (integer)
        for key, value in request.POST.items():
            if key.startswith("question_") and value:
                question_id = key.replace("question_", "")
                try:
                    option_id = int(value)
                    ExamAnswer.objects.update_or_create(
                        attempt=attempt,
                        question_id=question_id,
                        defaults={"selected_option_id": option_id},
                    )
                except (ValueError, TypeError):
                    continue

        attempt.status = ExamAttempt.Status.SUBMITTED
        attempt.submitted_at = timezone.now()
        attempt.save()
        attempt.calculate_score()

        messages.success(request, "Exam submitted successfully!")
        # For practice exams, redirect to the specific attempt result
        if exam.is_practice:
            return redirect("attempts:result", pk=pk)
        return redirect("attempts:result", pk=pk)


class StudentResultView(StudentRequiredMixin, View):
    """Display exam results."""

    template_name = "attempts/exam_result.html"

    def get(self, request, pk):
        exam = get_object_or_404(
            Exam.objects.select_related("subject", "subject__assigned_class"),
            pk=pk,
        )

        # Get all completed attempts for this exam
        attempts = (
            ExamAttempt.objects.filter(
                exam=exam,
                student=request.user,
                status__in=[ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.TIMED_OUT],
            )
            .prefetch_related(
                "answers", "answers__question", "answers__selected_option"
            )
            .order_by("-submitted_at")
        )

        if not attempts.exists():
            messages.error(request, "No completed attempt found for this exam.")
            return redirect("attempts:list")

        # Get the most recent attempt by default
        attempt = attempts.first()

        # For practice exams, also get all attempts for display
        all_attempts = list(attempts) if exam.is_practice else []

        return render(
            request,
            self.template_name,
            {
                "exam": exam,
                "attempt": attempt,
                "all_attempts": all_attempts,
                "is_practice": exam.is_practice,
            },
        )


class StudentAnswerReviewView(StudentRequiredMixin, View):
    """Review answers after exam submission."""

    template_name = "attempts/exam_review.html"

    def get(self, request, pk):
        exam = get_object_or_404(
            Exam.objects.select_related("subject", "subject__assigned_class"),
            pk=pk,
        )
        attempt = get_object_or_404(
            ExamAttempt.objects.select_related("exam").prefetch_related(
                "answers",
                "answers__question",
                "answers__question__options",
                "answers__selected_option",
            ),
            exam=exam,
            student=request.user,
            status__in=[ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.TIMED_OUT],
        )

        # Build answers data in the student's question order
        answers_dict = {a.question_id: a for a in attempt.answers.all()}
        questions_data = []

        for idx, q_id in enumerate(attempt.question_order):
            answer = answers_dict.get(q_id)
            if answer:
                question = answer.question
                questions_data.append(
                    {
                        "index": idx + 1,
                        "question": question,
                        "selected_option": answer.selected_option,
                        "correct_option": question.correct_option,
                        "is_correct": answer.is_correct,
                        "options": list(question.options.all()),
                    }
                )

        return render(
            request,
            self.template_name,
            {
                "exam": exam,
                "attempt": attempt,
                "questions_data": questions_data,
            },
        )


class StudentPerformanceView(StudentRequiredMixin, View):
    """Student performance dashboard with analytics."""

    template_name = "attempts/performance.html"

    def get(self, request):
        user = request.user

        # Get all completed attempts for this student
        attempts = ExamAttempt.objects.filter(
            student=user,
            status__in=[ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.TIMED_OUT],
        ).select_related("exam", "exam__subject")

        # Overall statistics
        stats = attempts.aggregate(
            total_exams=Count("id"),
            avg_score=Avg("score"),
            max_score=Max("score"),
            min_score=Min("score"),
            total_questions=Avg("total_questions"),
        )

        total_exams = stats["total_exams"] or 0
        avg_score_raw = stats["avg_score"] or 0
        avg_total_questions = stats["total_questions"] or 0

        # Calculate average percentage
        if total_exams > 0 and avg_total_questions > 0:
            avg_percentage = round((avg_score_raw / avg_total_questions) * 100, 1)
        else:
            avg_percentage = 0

        # Calculate pass rate (>=50%)
        passed_count = 0
        for attempt in attempts:
            if attempt.percentage_score >= 50:
                passed_count += 1
        pass_rate = (
            round((passed_count / total_exams) * 100, 1) if total_exams > 0 else 0
        )

        # Find highest and lowest scoring exams
        highest_exam = None
        lowest_exam = None
        highest_percentage = 0
        lowest_percentage = 100

        for attempt in attempts:
            if attempt.percentage_score >= highest_percentage:
                highest_percentage = attempt.percentage_score
                highest_exam = attempt
            if attempt.percentage_score <= lowest_percentage:
                lowest_percentage = attempt.percentage_score
                lowest_exam = attempt

        # Subject-wise breakdown
        subject_stats = {}
        for attempt in attempts:
            subject_name = attempt.exam.subject.name
            if subject_name not in subject_stats:
                subject_stats[subject_name] = {
                    "name": subject_name,
                    "total_exams": 0,
                    "total_score": 0,
                    "total_questions": 0,
                    "scores": [],
                }
            subject_stats[subject_name]["total_exams"] += 1
            subject_stats[subject_name]["total_score"] += attempt.score or 0
            subject_stats[subject_name]["total_questions"] += attempt.total_questions
            subject_stats[subject_name]["scores"].append(attempt.percentage_score)

        # Calculate averages for each subject
        subject_data = []
        for name, data in subject_stats.items():
            if data["total_questions"] > 0:
                avg_pct = round(
                    (data["total_score"] / data["total_questions"]) * 100, 1
                )
            else:
                avg_pct = 0
            subject_data.append(
                {
                    "name": name,
                    "total_exams": data["total_exams"],
                    "avg_percentage": avg_pct,
                }
            )

        # Sort by average percentage descending
        subject_data.sort(key=lambda x: x["avg_percentage"], reverse=True)

        # Recent exam history (last 10)
        recent_attempts = attempts.order_by("-submitted_at")[:10]

        # Data for charts (JSON)
        # Score trend chart data
        trend_data = []
        for attempt in attempts.order_by("submitted_at"):
            trend_data.append(
                {
                    "date": attempt.submitted_at.strftime("%Y-%m-%d"),
                    "score": attempt.percentage_score,
                    "exam": attempt.exam.title[:20],
                }
            )

        # Subject comparison chart data
        chart_subjects = [s["name"] for s in subject_data]
        chart_scores = [s["avg_percentage"] for s in subject_data]

        context = {
            "total_exams": total_exams,
            "avg_percentage": avg_percentage,
            "pass_rate": pass_rate,
            "passed_count": passed_count,
            "highest_exam": highest_exam,
            "lowest_exam": lowest_exam,
            "subject_data": subject_data,
            "recent_attempts": recent_attempts,
            "trend_data_json": json.dumps(trend_data),
            "chart_subjects_json": json.dumps(chart_subjects),
            "chart_scores_json": json.dumps(chart_scores),
        }

        return render(request, self.template_name, context)


class StudentExamHistoryView(StudentRequiredMixin, View):
    """Complete exam history with filtering and sorting."""

    template_name = "attempts/exam_history.html"
    paginate_by = 10

    def get(self, request):
        user = request.user

        # Get all completed attempts for this student
        attempts = ExamAttempt.objects.filter(
            student=user,
            status__in=[ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.TIMED_OUT],
        ).select_related("exam", "exam__subject")

        # Get unique subjects for filter dropdown
        subjects = (
            attempts.values_list("exam__subject__id", "exam__subject__name")
            .distinct()
            .order_by("exam__subject__name")
        )
        subjects = [{"id": s[0], "name": s[1]} for s in subjects]

        # Apply filters
        subject_filter = request.GET.get("subject")
        if subject_filter:
            attempts = attempts.filter(exam__subject_id=subject_filter)

        date_from = request.GET.get("date_from")
        if date_from:
            attempts = attempts.filter(submitted_at__date__gte=date_from)

        date_to = request.GET.get("date_to")
        if date_to:
            attempts = attempts.filter(submitted_at__date__lte=date_to)

        status_filter = request.GET.get("status")
        if status_filter == "pass":
            # Filter for passed exams (>=50%)
            attempt_ids = [a.id for a in attempts if a.percentage_score >= 50]
            attempts = attempts.filter(id__in=attempt_ids)
        elif status_filter == "fail":
            # Filter for failed exams (<50%)
            attempt_ids = [a.id for a in attempts if a.percentage_score < 50]
            attempts = attempts.filter(id__in=attempt_ids)

        # Apply sorting
        sort_by = request.GET.get("sort", "-submitted_at")
        if sort_by == "date_asc":
            attempts = attempts.order_by("submitted_at")
        elif sort_by == "date_desc":
            attempts = attempts.order_by("-submitted_at")
        elif sort_by == "score_asc":
            # Sort by percentage score (need to calculate)
            attempts = sorted(attempts, key=lambda a: a.percentage_score)
        elif sort_by == "score_desc":
            attempts = sorted(attempts, key=lambda a: a.percentage_score, reverse=True)
        else:
            attempts = attempts.order_by("-submitted_at")

        # Handle sorted list vs queryset for pagination
        if isinstance(attempts, list):
            total_count = len(attempts)
            page = int(request.GET.get("page", 1))
            start = (page - 1) * self.paginate_by
            end = start + self.paginate_by
            page_attempts = attempts[start:end]
            has_previous = page > 1
            has_next = end < total_count
            total_pages = (total_count + self.paginate_by - 1) // self.paginate_by
        else:
            total_count = attempts.count()
            paginator = Paginator(attempts, self.paginate_by)
            page = request.GET.get("page", 1)
            page_obj = paginator.get_page(page)
            page_attempts = page_obj.object_list
            has_previous = page_obj.has_previous()
            has_next = page_obj.has_next()
            page = page_obj.number
            total_pages = paginator.num_pages

        context = {
            "attempts": page_attempts,
            "subjects": subjects,
            "total_count": total_count,
            "current_page": int(page),
            "total_pages": total_pages,
            "has_previous": has_previous,
            "has_next": has_next,
            "selected_subject": subject_filter,
            "selected_status": status_filter,
            "selected_sort": sort_by if sort_by else "-submitted_at",
            "date_from": date_from,
            "date_to": date_to,
        }

        return render(request, self.template_name, context)


class TeacherResultsListView(ResultsViewerRequiredMixin, View):
    """List exam results for teacher's assigned subjects."""

    template_name = "attempts/teacher_results_list.html"
    paginate_by = 20

    def get(self, request):
        user = request.user

        # Get attempts based on user role
        attempts = ExamAttempt.objects.filter(
            status__in=[ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.TIMED_OUT]
        ).select_related(
            "exam",
            "exam__subject",
            "exam__subject__assigned_class",
            "student",
        )

        # Teachers only see results from their assigned subjects
        if user.is_teacher and not user.is_admin and not user.is_examiner:
            assigned_subjects = user.assigned_subjects.filter(is_active=True)
            attempts = attempts.filter(exam__subject__in=assigned_subjects)
            exams = Exam.objects.filter(subject__in=assigned_subjects, is_active=True)
            classes = Class.objects.filter(
                id__in=assigned_subjects.values_list("assigned_class_id", flat=True)
            )
        else:
            exams = Exam.objects.filter(is_active=True)
            classes = Class.objects.filter(is_active=True)

        # Filter by exam if provided
        exam_id = request.GET.get("exam")
        if exam_id:
            attempts = attempts.filter(exam_id=exam_id)

        # Filter by class if provided
        class_id = request.GET.get("class")
        if class_id:
            attempts = attempts.filter(exam__subject__assigned_class_id=class_id)

        # Order by most recent first
        attempts = attempts.order_by("-submitted_at")

        # Pagination
        paginator = Paginator(attempts, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "page_obj": page_obj,
            "exams": exams.select_related("subject"),
            "classes": classes,
            "selected_exam": exam_id,
            "selected_class": class_id,
            "total_results": attempts.count(),
        }
        return render(request, self.template_name, context)


class TeacherResultDetailView(ResultsViewerRequiredMixin, View):
    """View detailed result of a student's exam attempt."""

    template_name = "attempts/teacher_result_detail.html"

    def get(self, request, pk):
        user = request.user
        attempt = get_object_or_404(
            ExamAttempt.objects.select_related(
                "exam",
                "exam__subject",
                "exam__subject__assigned_class",
                "student",
            ).prefetch_related(
                "answers",
                "answers__question",
                "answers__question__options",
                "answers__selected_option",
            ),
            pk=pk,
            status__in=[ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.TIMED_OUT],
        )

        # Teachers can only view results from their assigned subjects
        if user.is_teacher and not user.is_admin and not user.is_examiner:
            assigned_subject_ids = user.assigned_subjects.values_list("id", flat=True)
            if attempt.exam.subject_id not in assigned_subject_ids:
                messages.error(request, "You don't have access to this result.")
                return redirect("attempts:teacher_results")

        # Get answers with question details
        answers_data = []
        for answer in attempt.answers.all():
            question = answer.question
            answers_data.append(
                {
                    "question": question,
                    "selected_option": answer.selected_option,
                    "correct_option": question.correct_option,
                    "is_correct": answer.is_correct,
                    "options": list(question.options.all()),
                }
            )

        context = {
            "attempt": attempt,
            "exam": attempt.exam,
            "student": attempt.student,
            "answers_data": answers_data,
        }
        return render(request, self.template_name, context)


class StudentResultPDFView(StudentRequiredMixin, View):
    """Download exam result as PDF."""

    def get(self, request, pk):
        exam = get_object_or_404(
            Exam.objects.select_related("subject", "subject__assigned_class"),
            pk=pk,
        )
        attempt = get_object_or_404(
            ExamAttempt.objects.select_related(
                "exam", "student", "student__assigned_class"
            ),
            exam=exam,
            student=request.user,
            status__in=[ExamAttempt.Status.SUBMITTED, ExamAttempt.Status.TIMED_OUT],
        )

        # Get institution for PDF header
        institution = Institution.get_instance()

        # Generate PDF
        pdf_buffer = PDFService.generate_exam_result_pdf(attempt, institution)

        # Create response
        response = HttpResponse(pdf_buffer.read(), content_type="application/pdf")
        filename = (
            f"result_{exam.title.replace(' ', '_')}_{attempt.student.username}.pdf"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response
