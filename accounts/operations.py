from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


# () password_number se refiere a si es el primero para input o segundo para verificar que sean iguales
def valid_password_messages(form):
    password = form.cleaned_data.get(f"new_password1")
    if password:
        try:
            validate_password(password, form.user)
        except ValidationError as e:
            messages = []
            for msg in e.messages:
                msg = msg.replace(
                    "Your password can’t be too similar to your other personal information.",
                    "Tu contraseña no puede ser demasiado parecida a tu información personal.",
                )
                msg = msg.replace(
                    "This password is too short.",
                    "Tu contraseña es demasiado corta.",
                )
                msg = msg.replace(
                    "This password is too common.",
                    "Tu contraseña es demasiado común.",
                )
                msg = msg.replace(
                    "This password is entirely numeric.",
                    "Tu contraseña no puede ser solo números.",
                )
                msg = msg.replace(
                    "It must contain at least 8 characters.",
                    "Debe tener al menos 8 caracteres.",
                )
                messages.append(msg)
            raise ValidationError(messages)
    return password


def valid_repeat_password_messages(form):
    password1 = form.cleaned_data.get("new_password1")
    password2 = form.cleaned_data.get("new_password2")
    if password1 and password2 and password1 != password2:
        raise ValidationError("Las contraseñas nuevas no coinciden.")
    return password2


@require_POST
@login_required
def cambiar_tema(request):
    nuevo_tema = request.POST.get("theme")
    request.user.perfil.tema = nuevo_tema
    request.user.perfil.save()
    return redirect(request.META.get("HTTP_REFERER", "/"))
