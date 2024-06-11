from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import View

from .forms import CustomUserCreationForm


class CustomLoginView(LoginView):
    """Custom login view."""

    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    pass


class CustomSignupView(View):
    """
    Custom sign-up view based on Django's generic CreateView.
    It uses the CustomUserCreationForm for user registration.
    """

    form_class = CustomUserCreationForm
    success_url = reverse_lazy("accounts:login")
    template_name = "accounts/signup.html"

    def dispatch(self, request, *args, **kwargs):
        # If the user is already authenticated, redirects them to the index page.
        if request.user.is_authenticated:
            return redirect("blogs:quiz_list")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect(self.success_url)
        return render(request, self.template_name, {"form": form})
