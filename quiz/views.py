from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from django_filters.views import FilterView

from .filters import QuizFilter
from .forms import QuizForm, QuizSearchForm
from .models import Category, Question, Quiz, Answer, Result

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


# def get_random_quiz(request):
# # quizzes = Quiz.objects.all()
# return render()


class QuizAssessmentResultView(DetailView):
    model = Quiz
    context_object_name = "quiz"
    template_name = "quiz/quiz_assessment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.object
        user = self.request.user
        # result = Result.objects.filter(quiz=quiz, user=user).last()
        # context["quiz_score"] = result.score if result else None
        return context


class QuizAssessmentAttemptView(DetailView):
    """Displays a quiz attempt form to the user."""
    
    model = Quiz
    context_object_name = "quiz"
    template_name = "quiz/quiz_attempt.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.object
        questions = quiz.get_questions()
        context["form"] = QuizForm(questions=questions)
        context["questions"] = questions
        context["total_questions"] = len(questions)
        return context


class QuizAssessmentSubmissionFormView(SingleObjectMixin, FormView):
    """Handles the submission of a quiz attempt."""

    form_class = QuizForm
    model = Quiz
    template_name = "quiz/quiz_attempt.html"

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Validate the form data and calculate the quiz score.
        """

        quiz = self.object
        questions = quiz.get_questions()
        score = 0
        submitted_answer_ids = []

        for question in questions:
            if question.question_type == Question.QuestionType.MULTI_SELECT_MULTIPLE_CHOICE:
                selected_answer_ids = form.cleaned_data[f"question_{question.id}"]
                selected_answers = [get_object_or_404(Answer, id=answer_id) for answer_id in selected_answer_ids]
                submitted_answer_ids.extend(map(int, selected_answer_ids))
                # only count score if all the submitted answers are correct without incorrect answer
                if all(answer.is_correct for answer in selected_answers):
                    score += 1
            else:  # both Multiple Choice and True/False question type
                selected_answer_id = form.cleaned_data[f"question_{question.id}"]
                selected_answer = get_object_or_404(Answer, id=selected_answer_id)
                # convert the datatype 'str' into 'int'
                submitted_answer_ids.append(int(selected_answer_id))
                if selected_answer.is_correct:
                    score += 1

        total_questions = len(questions)
        score_percentage = round((score / total_questions) * 100, 2)
        passed = score_percentage >= quiz.pass_percentage

        context = {
            "quiz": quiz,
            "score_percentage": score_percentage,
            "total_questions": total_questions,
            "score": score,
            "passed": passed,
            "submitted_answer_ids": submitted_answer_ids,
        }
        return render(self.request, "quiz/quiz_result.html", context)
    
    def get_form_kwargs(self):
        """
        Get keyword arguments for the form initialization.
        Fetch the quiz object and pass its questions as keyword argument to the form.
        """

        kwargs = super().get_form_kwargs()
        quiz = self.get_object()
        kwargs["questions"] = quiz.get_questions()
        return kwargs
     
    def get_success_url(self):
        quiz = self.object
        return quiz.get_assessment_attempt_url()


class QuizView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        view = QuizAssessmentAttemptView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = QuizAssessmentSubmissionFormView.as_view()
        return view(request, *args, **kwargs)
