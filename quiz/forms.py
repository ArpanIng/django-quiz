from django import forms

from .models import Question


class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop("questions", [])
        super(QuizForm, self).__init__(*args, **kwargs)
        for question in questions:
            if question.question_type == Question.QuestionType.MULTI_SELECT_MULTIPLE_CHOICE:
                choice_list = [(answer.id, answer.text) for answer in question.get_answers()]
                # checkbox for MSMC questions
                self.fields[f"question_{question.id}"] = forms.MultipleChoiceField(
                    label=question.text,
                    choices=choice_list,
                    widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
                )
            else:  # handles Multiple Choice question type
                choice_list = [(answer.id, answer.text) for answer in question.get_answers()]
                self.fields[f"question_{question.id}"] = forms.ChoiceField(
                    label=question.text,
                    choices=choice_list,
                    widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
                )


class QuizSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search quizzes"}
        ),
    )
