from django.urls import path

from . import views

app_name = "quiz"
urlpatterns = [
    path("", views.QuizListView.as_view(), name="quiz_list"),
    path('popular/', views.QuizListView.as_view(), {"popular": True}, name="quiz_list_by_popularity"),
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path(
        "category/<int:category_id>/",
        views.QuizListView.as_view(),
        name="quiz_list_by_category",
    ),
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
]
