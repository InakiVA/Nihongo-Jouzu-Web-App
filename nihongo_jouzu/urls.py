"""
URL configuration for nihongo_jouzu project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

import core.views as core

urlpatterns = [
    path("admin/", admin.site.urls),
    path("core/", include("core.urls"), name="core"),
    path("inicio/", include("study.urls"), name="inicio"),
    path("palabras/", include("dictionary.urls"), name="palabras"),
    path("grupos/", include("groups.urls"), name="grupos"),
    path("etiquetas/", include("tags.urls"), name="etiquetas"),
    path("", include("accounts.urls"), name="usuario"),
    path("buscar/", core.SearchView.as_view(), name="buscar"),
]
