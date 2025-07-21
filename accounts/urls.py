from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import SignupView, UserView, CustomLoginView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", UserView.as_view(), name="usuario"),
]
