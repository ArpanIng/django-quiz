from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """
    A custom user creation form extending Django's UserCreationForm.
    """

    class Meta:
        model = User
        fields = ("email", "username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for field in ["username", "password1"]:
            self.fields[field].help_text = None
