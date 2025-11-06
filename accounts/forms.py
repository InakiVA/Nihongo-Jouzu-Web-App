from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
)
from django.contrib.auth.password_validation import validate_password
from .models import Usuario

import accounts.operations as op

from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model


class CustomUsernameChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()  # avoids global variable
        fields = ("username",)  # only allow changing username

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "w-full px-4 py-2 rounded bg-darkest text-white border border-light focus:outline-none focus:ring-2 focus:ring-main"
            }
        )
        for field_name, field in self.fields.items():
            field.error_messages["required"] = "Este campo es obligatorio."


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
        for field_name, field in self.fields.items():
            field.error_messages["required"] = "Este campo es obligatorio."


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.error_messages["required"] = "Este campo es obligatorio."

    class Meta:
        model = Usuario
        fields = ("username", "password")


class CustomPasswordChangeForm(PasswordChangeForm):
    error_messages = {
        "password_incorrect": ("La contraseña actual es incorrecta."),
        "password_mismatch": ("Las contraseñas nuevas no coinciden."),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.error_messages["required"] = "Este campo es obligatorio."

    def clean_new_password1(self):
        return op.valid_password_messages(self)

    def clean_new_password2(self):
        return op.valid_repeat_password_messages(self)
