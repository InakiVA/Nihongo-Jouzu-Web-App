from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

from tags.models import Etiqueta


@require_POST
@login_required
def crear_etiqueta(request):
    etiqueta_value = request.POST.get("etiqueta_nueva")
    if not etiqueta_value:
        messages.error(request, "Favor de ingresar nombre de etiqueta")
        return redirect(request.META.get("HTTP_REFERER", "/"))
    if "<" in etiqueta_value or ">" in etiqueta_value:
        messages.warning(request, "Etiqueta no puede contener '<' o '>'")
        return redirect(request.META.get("HTTP_REFERER", "/"))
    user = request.user
    existent = Etiqueta.objects.filter(
        Q(usuario=user) | Q(usuario__perfil__rol="admin"), etiqueta=etiqueta_value
    ).exists()
    if existent:
        messages.warning(request, "Ya existe una etiqueta con este nombre")
        return redirect(request.META.get("HTTP_REFERER", "/"))
    color_value = request.POST.get("color_nuevo")
    Etiqueta.objects.create(usuario=user, etiqueta=etiqueta_value, color=color_value)
    messages.success(request, "Etiqueta creada exitosamente")
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@login_required
def editar_etiqueta(request, atributo):
    etiqueta_id = request.POST.get("etiqueta_id")
    etiqueta_obj = get_object_or_404(Etiqueta, id=etiqueta_id)
    user = request.user
    if not etiqueta_obj or etiqueta_obj.usuario != user:
        return redirect(request.META.get("HTTP_REFERER", "/"))
    if atributo == "etiqueta":
        value = request.POST.get("update_etiqueta")
        if not value:
            messages.warning(
                request, "No se ingresó el nombre de etiqueta para actualizar"
            )
            return redirect(request.META.get("HTTP_REFERER", "/"))
        existent = Etiqueta.objects.filter(usuario=user, etiqueta=value).exists()
        if existent:
            if value == etiqueta_obj.etiqueta:
                messages.info(request, "El nombre de la etiqueta es el mismo")
            else:
                messages.warning(request, "Ya creaste una etiqueta con este nombre")
            return redirect(request.META.get("HTTP_REFERER", "/"))
        if "<" in value or ">" in value:
            messages.warning(request, "Etiqueta no puede contener '<' o '>'")
            return redirect(request.META.get("HTTP_REFERER", "/"))
        etiqueta_obj.update_etiqueta(value)
        messages.success(request, "Nombre de la etiqueta actualizado exitosamente")
    elif atributo == "color":
        value = request.POST.get("update_color")
        etiqueta_obj.update_color(value)
        messages.success(request, "Color de la etiqueta actualizado exitosamente")
    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
@login_required
def eliminar_etiqueta(request):
    etiqueta_id = request.POST.get("delete_tag")
    etiqueta_obj = get_object_or_404(Etiqueta, id=etiqueta_id)
    user = request.user
    if not etiqueta_obj or etiqueta_obj.usuario != user:
        return redirect(request.META.get("HTTP_REFERER", "/"))
    etiqueta_obj.delete()
    messages.success(request, "Etiqueta eliminada exitosamente")
    return redirect("etiquetas")
