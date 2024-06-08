from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic import View, TemplateView
from django.http import HttpResponseForbidden
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from django.contrib.auth import get_user_model
User = get_user_model()

from .models import Quiz, Answer, Result
from .forms import QuizForm



class CategoryView(TemplateView):
    template_name = "quiz/category_list.html"



class QuizListView(ListView):
    model = Quiz
    context_object_name = "quizzes"
    paginate_by = 50
    template_name = "quiz/index.html"

    def get_queryset(self):
        queryset = Quiz.objects.all().order_by('id')
        # filter quiz based on search params
        query = self.request.GET.get("name")
        if query:
            queryset = queryset.filter(name__icontains=query)

        return queryset


class QuizAssessmentResultView(LoginRequiredMixin, DetailView):
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


class QuizView(View):
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
