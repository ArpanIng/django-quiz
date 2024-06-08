from django import forms


class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop("questions", [])
        super(QuizForm, self).__init__(*args, **kwargs)
        for question in questions:
            choice_list = [(answer.id, answer.text) for answer in question.get_answers()]
            self.fields[f"question_{question.id}"] = forms.ChoiceField(
                label=question.text,
                choices=choice_list,
                widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
            )