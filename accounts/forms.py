from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario


class SignupForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "w-full px-4 py-2 rounded bg-darkest text-white border border-light focus:outline-none focus:ring-2 focus:ring-main"
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "class": "w-full px-4 py-2 rounded bg-darkest text-white border border-light focus:outline-none focus:ring-2 focus:ring-main"
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "w-full px-4 py-2 rounded bg-darkest text-white border border-light focus:outline-none focus:ring-2 focus:ring-main"
            }
        )


class LoginForm(AuthenticationForm):
    class Meta:
        model = Usuario
        fields = ("username", "password")
