import random

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Quiz(models.Model):
    class DifficultyLevel(models.TextChoices):
        EASY = "EASY", "Easy"
        MEDIUM = "MEDIUM", "Medium"
        HARD = "HARD", "Hard"

    name = models.CharField(max_length=255)
    number_of_questions = models.PositiveIntegerField(
        validators=[MinValueValidator(2), MaxValueValidator(60)]
    )
    duration_in_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(60)],
        help_text="Duration of the quiz in minutes.",
    )
    pass_percentage = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(40), MaxValueValidator(90)],
        help_text="Required pass score in percentage.",
    )
    popularity = models.PositiveIntegerField(default=0)
    difficulty_level = models.CharField(max_length=6, choices=DifficultyLevel.choices)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="quizzes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"
        indexes = [
            models.Index(fields=["popularity"]),
        ]

    def clean(self):
        hard = self.DifficultyLevel.HARD
        medium = self.DifficultyLevel.MEDIUM
        easy = self.DifficultyLevel.EASY

        hard_level_message = "For hard quizzes, the pass percentage cannot be less than 75."
        medium_level_message = "For medium quizzes, the pass percentage cannot be less than 50 and greater than 70."
        easy_level_message = "For easy quizzes, the pass percentage cannot be greater than 60."

        pass_per = self.pass_percentage

        if self.difficulty_level == hard and pass_per < 75:
            raise ValidationError({"pass_percentage": hard_level_message})
        if self.difficulty_level == medium and (pass_per < 50 or pass_per > 70):
            raise ValidationError({"pass_percentage": medium_level_message})
        if self.difficulty_level == easy and pass_per > 60:
            raise ValidationError({"pass_percentage": easy_level_message})

    def save(self, *args, **kwargs):
        # call the clean method
        # With this wherever you create your object (form, view, shell, test) the validation will be called.
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_assessment_url(self):
        return reverse("quiz:quiz_assessment", kwargs={"pk": self.id})

    def get_assessment_attempt_url(self):
        return reverse("quiz:quiz_assessment_attempt", kwargs={"pk": self.id})

    def get_questions(self):
        questions = list(self.questions.prefetch_related("answers"))
        random.shuffle(questions)
        return questions[:self.number_of_questions]

    def get_questions_count(self):
        return self.questions.count()


class Question(models.Model):
    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = "MC", "Multiple Choice"  # radio (single answer)
        MULTI_SELECT_MULTIPLE_CHOICE = "MSMC", "Multi select Multiple Choice"  # checkbox

    text = models.CharField(max_length=255)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_type = models.CharField(
        max_length=4,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text

    def get_answers(self):
        return self.answers.all()


class Answer(models.Model):
    text = models.CharField(max_length=255)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensure the same answer isn't added multiple times
        unique_together = ("question", "text")

    def __str__(self):
        return self.text


class Result(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="results")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.FloatField()
    submitted_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User: {self.user}, score: {self.score}"
