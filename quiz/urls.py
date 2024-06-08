from django.urls import path

from . import views

app_name = "quiz"
urlpatterns = [
    path("", views.QuizListView.as_view(), name="quiz_list"),
    path("category/", views.CategoryView.as_view(), name="category_list"),
    path(
        "<int:pk>/assessment/",
        views.QuizAssessmentResultView.as_view(),
        name="quiz_assessment",
    ),
    path(
        "<int:pk>/assessment/attempt/",
        views.QuizView.as_view(),
        name="quiz_assessment_attempt",
    ),
    path("<int:pk>/assessment/attempt/submit/", views.submit_quiz, name="quiz_submit"),
]
