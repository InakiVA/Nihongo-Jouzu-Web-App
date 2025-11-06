from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import CreateView, TemplateView
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .forms import CustomPasswordChangeForm, CustomUsernameChangeForm


class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("inicio")
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("inicio")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("inicio")
        return super().dispatch(request, *args, **kwargs)


class WelcomeView(TemplateView):
    template_name = "accounts/welcome.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["usuario"] = self.request.user
        context["login_url"] = reverse("login")
        context["signup_url"] = reverse("signup")
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("inicio")
        return super().dispatch(request, *args, **kwargs)


class UserView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/user.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["usuario"] = self.request.user
        context["logout_url"] = reverse("logout")
        context["username_form"] = CustomUsernameChangeForm(instance=self.request.user)
        context["password_form"] = CustomPasswordChangeForm(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        """Handle both username and password change submissions."""
        username_form = CustomUsernameChangeForm(
            instance=request.user, data=request.POST
        )
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if "username_submit" in request.POST:
            if username_form.is_valid() and username_form.has_changed():
                username_form.save()
                messages.success(
                    request, "Nombre de usuario actualizado correctamente."
                )
                return redirect(request.META.get("HTTP_REFERER", "/"))
            elif not username_form.has_changed():
                messages.info(
                    request, "No se realizaron cambios en el nombre de usuario."
                )
            else:
                messages.error(
                    request,
                    "Ya existe un usuario con ese nombre. Favor de elegir otro.",
                )
                return redirect(request.META.get("HTTP_REFERER", "/"))

        elif "password_submit" in request.POST:
            if password_form.is_valid():
                print("Password form is valid")
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keeps user logged in
                messages.success(request, "Se cambió tu contraseña exitosamente.")
                return redirect(request.META.get("HTTP_REFERER", "/"))
            else:
                print("Password form is invalid")
                messages.error(
                    request,
                    "No se pudo cambiar la contraseña. Favor de corregir errores.",
                )

        # Pass the submitted forms (with errors) back to the template
        context = super().get_context_data()
        context["usuario"] = request.user
        context["logout_url"] = reverse("logout")
        context["username_form"] = username_form
        context["password_form"] = password_form
        return self.render_to_response(context)
