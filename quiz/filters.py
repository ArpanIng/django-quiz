import django_filters
from django import forms

from .models import Quiz


class QuizFilter(django_filters.FilterSet):
    difficulty_level = django_filters.ChoiceFilter(
        choices=Quiz.DifficultyLevel.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Quiz
        fields = ["difficulty_level"]
