import factory
from faker import Faker
from .models import Quiz, Question, Answer

fake = Faker()


class QuizFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Quiz

    name = factory.Faker("sentence", nb_words=3)
    topic = factory.Faker("word")
    number_of_questions = factory.Faker("random_int", min=5, max=20)
    duration_in_minutes = factory.Faker("random_int", min=10, max=60)
    pass_percentage = factory.Faker("random_int", min=40, max=90)
    difficulty_level = factory.Faker(
        "random_element", elements=[level.value for level in Quiz.DifficultyLevel]
    )

    @factory.lazy_attribute
    def pass_percentage(self):
        if self.difficulty_level == Quiz.DifficultyLevel.HARD:
            return fake.random_int(min=75, max=90)
        elif self.difficulty_level == Quiz.DifficultyLevel.MEDIUM:
            return fake.random_int(min=50, max=70)
        else:
            return fake.random_int(min=40, max=60)


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    text = factory.Faker("sentence", nb_words=10)
    quiz = factory.SubFactory(QuizFactory)


class AnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Answer

    text = factory.Faker("sentence", nb_words=5)
    question = factory.SubFactory(QuestionFactory)
    is_correct = factory.Faker("boolean")
