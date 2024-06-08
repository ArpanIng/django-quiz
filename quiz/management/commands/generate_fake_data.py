from django.core.management.base import BaseCommand
from quiz.factory import QuizFactory, QuestionFactory, AnswerFactory


class Command(BaseCommand):
    help = "Generate fake data for quizzes"

    def handle(self, *args, **kwargs):
        quiz_number = 100
        for _ in range(quiz_number):
            quiz = QuizFactory()
            for _ in range(quiz.number_of_questions):
                question = QuestionFactory(quiz=quiz)
                for _ in range(4):  # assuming each question has 4 answers
                    AnswerFactory(question=question)
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated {quiz_number} quizzes with questions and answers."
            )
        )
