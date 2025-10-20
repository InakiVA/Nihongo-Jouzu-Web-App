from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import SignupView, UserView, CustomLoginView, WelcomeView

urlpatterns = [
    path("", WelcomeView.as_view(), name="welcome"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("usuario/", UserView.as_view(), name="usuario"),
]
