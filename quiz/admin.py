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
        "difficulty_level",
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
    ordering = ["id"]


admin.site.register(Result)
admin.site.register(Answer)
