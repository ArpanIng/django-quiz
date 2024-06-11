from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.views.generic import View, TemplateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from django_filters.views import FilterView

from .filters import QuizFilter
from .forms import QuizForm, QuizSearchForm
from .models import Category, Quiz, Answer, Result

User = get_user_model()


class CategoryListView(ListView):
    model = Category
    context_object_name = "categories"
    template_name = "quiz/category_list.html"


class QuizListView(FilterView):
    """
    Display a list of quizzes.
    Optionally can be filtered by search query, difficulty level or category.
    """

    model = Quiz
    context_object_name = "quizzes"
    paginate_by = 50
    filterset_class = QuizFilter
    template_name = "quiz/index.html"

    def get_queryset(self):
        queryset = Quiz.objects.all().select_related("category").order_by("id")

        # filter quiz based on search params
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(name__icontains=query)

        # filter quiz based on category
        category_id = self.kwargs.get("category_id")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = QuizSearchForm()
        return context


class QuizAssessmentResultView(DetailView):
    model = Quiz
    context_object_name = "quiz"
    template_name = "quiz/quiz_assessment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.object
        user = self.request.user
        result = Result.objects.filter(quiz=quiz, user=user).last()
        context["quiz_score"] = result.score if result else None
        return context


class QuizAssessmentAttemptView(DetailView):
    model = Quiz
    context_object_name = "quiz"
    template_name = "quiz/quiz_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.object
        questions = quiz.get_questions()
        context["form"] = QuizForm(questions=questions)
        context["questions"] = questions
        context["total_questions"] = quiz.get_questions_count()
        return context


class QuizAssessmentFormView(SingleObjectMixin, FormView):
    form_class = QuizForm
    model = Quiz
    template_name = "quiz/quiz_detail.html"

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        quiz = self.object
        return quiz.get_assessment_attempt_url()


class QuizView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        view = QuizAssessmentAttemptView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = QuizAssessmentFormView.as_view()
        return view(request, *args, **kwargs)


def submit_quiz(request, pk):
    if request.method == "POST":
        quiz = get_object_or_404(Quiz, id=pk)
        score = 0
        submitted_answer_ids = []

        for question in quiz.get_questions():
            submitted_answer_id = request.POST.get(f"question_{question.id}")
            if submitted_answer_id:
                submitted_answer = get_object_or_404(Answer, id=submitted_answer_id)
                submitted_answer_ids.append(int(submitted_answer_id))
                if submitted_answer.is_correct:
                    score += 1

        total_questions = quiz.get_questions_count()
        score_percentage = round((score / total_questions) * 100, 2)
        passed = score_percentage >= quiz.pass_percentage

        context = {
            "quiz": quiz,
            "percentage_score": score_percentage,
            "total_questions": total_questions,
            "score": score,
            "passed": passed,
            "submitted_answer_ids": submitted_answer_ids,
        }
        return render(request, "quiz/quiz_result.html", context)


def test_submit_view(request, pk):
    quiz = get_object_or_404(Quiz, id=pk)
    context = {
        "quiz": quiz,
        "percentage_score": 80,
        "passed": False,
    }
    return render(request, "quiz/quiz_result.html", context)
