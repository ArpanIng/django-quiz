from django.contrib import admin

from .models import Category, Quiz, Question, Answer, Result


admin.site.register(Category)


@admin.register(Quiz)
class QuizModelAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_display = [
        "name",
        "number_of_questions",
        "pass_percentage",
        "duration_in_minutes",
        "popularity",
        "difficulty_level",
        "category",
    ]
    list_filter = ["difficulty_level"]
    search_fields = ["name"]
    ordering = ["id"]


class AnswerInline(admin.TabularInline):
    model = Answer


@admin.register(Question)
class QuestionModelAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    search_fields = ["text"]
    ordering = ["-id"]


@admin.register(Answer)
class AnswerModelAdmin(admin.ModelAdmin):
    list_display = ["text", "question", "is_correct"]


@admin.register(Result)
class ResultModelAdmin(admin.ModelAdmin):
    list_display = ["quiz", "user", "score", "submitted_date"]
