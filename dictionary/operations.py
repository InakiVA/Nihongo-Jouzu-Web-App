from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

from dictionary.models import Palabra, Significado, Lectura, Nota
from progress.models import UsuarioPalabra
from groups.models import Grupo


# && debe tener por lo menos 1 lectura y 1 significado
@require_POST
@login_required
def crear_palabra(request):
    ajustes_palabras = request.session.get("ajustes_palabras")
    palabra_value = request.POST.get("palabra_nueva")
    significado_value = request.POST.get("significado_nuevo")
    lectura_value = request.POST.get("lectura_nueva")
    if not all([palabra_value, significado_value, lectura_value]):
        for key, value in zip(
            ["palabra_valida", "significado_valido", "lectura_valida"],
            [palabra_value, significado_value, lectura_value],
        ):
            ajustes_palabras[key] = value
        request.session["ajustes_palabras"] = ajustes_palabras
        if not palabra_value:
            messages.error(request, "Favor de ingresar palabra")
        if not significado_value:
            messages.error(request, "Favor de ingresar significado")
        if not lectura_value:
            messages.error(request, "Favor de ingresar lectura")
        return redirect(request.META.get("HTTP_REFERER", "/"))
    for key, value in zip(
        ["palabra_valida", "significado_valido", "lectura_valida"],
        ["", "", ""],
    ):
        ajustes_palabras[key] = value
    user = request.user
    palabra_obj = Palabra.objects.create(usuario=user, palabra=palabra_value)
    UsuarioPalabra.objects.create(usuario=user, palabra=palabra_obj)
    Significado.objects.create(
        significado=significado_value, palabra=palabra_obj, usuario=user
    )
    Lectura.objects.create(lectura=lectura_value, palabra=palabra_obj, usuario=user)
    request.session["palabra_actual"] = palabra_obj.id
    request.session["ajustes_palabras"] = ajustes_palabras
    messages.success(request, "Palabra creada exitosamente")
    return redirect("editar")


# -- etiquetas están en checkbox operations
# && solo se puede editar lo que es del usuario
@require_POST
@login_required
def editar_palabra_atributos(request, atributo):
    palabra_id = request.session.get("palabra_actual", None)
    palabra_obj = get_object_or_404(Palabra, id=palabra_id)
    user = request.user
    if not palabra_obj or palabra_obj.usuario != user:
        return redirect(request.META.get("HTTP_REFERER", "/"))
    if atributo == "palabra":
        value = request.POST.get("update_palabra")
        if value:
            palabra_obj.update_palabra(value)
            messages.success(request, "Palabra actualizada exitosamente")
        else:
            messages.warning(
                request, "No se ingresó información de palabra para actualizar"
            )
    else:
        value = request.POST.get("input_id")
        if value:
            object_id = request.POST.get("input_button_id")
            if atributo == "significado":
                obj = get_object_or_404(Significado, id=object_id)
                obj.update_significado(value)
                messages.success(request, "Significado actualizado exitosamente")
            elif atributo == "lectura":
                obj = get_object_or_404(Lectura, id=object_id)
                obj.update_lectura(value)
                messages.success(request, "Lectura actualizada exitosamente")
            elif atributo == "nota":
                obj = get_object_or_404(Nota, id=object_id)
                obj.update_nota(value)
                messages.success(request, "Nota actualizada exitosamente")
        else:
            messages.warning(
                request, f"No se ingresó información de {atributo} para actualizar"
            )

    return redirect(request.META.get("HTTP_REFERER", "/"))


# -- etiquetas están en checkbox operations
# && solo se puede eliminar lo que es del usuario
# && no puede haber 0 significados ni 0 lecturas
@require_POST
@login_required
def eliminar_palabra_atributos(request, atributo):
    print("borrando", atributo)
    palabra_id = request.session.get("palabra_actual", None)
    palabra_obj = get_object_or_404(Palabra, id=palabra_id)
    user = request.user
    if not palabra_obj or palabra_obj.usuario != user:
        return redirect(request.META.get("HTTP_REFERER", "/"))
    if atributo == "palabra":
        palabra_obj.delete()
        messages.success(request, "Palabra eliminada exitosamente")
        return redirect("palabras")
    elif atributo == "significado":
        # !! check de que haya al menos uno
        significados = palabra_obj.significados_objetos(user)
        if len(significados) <= 1:
            messages.error(request, "Debe haber mínimo un significado en la palabra")
        else:
            object_id = request.POST.get("delete_id")
            obj = get_object_or_404(Significado, id=object_id)
            obj.delete()
            messages.success(request, "Significado eliminado exitosamente")
    elif atributo == "lectura":
        # !! check de que haya al menos uno
        lecturas = palabra_obj.lecturas_objetos(user)
        if len(lecturas) <= 1:
            messages.error(request, "Debe haber mínimo una lectura en la palabra")
        else:
            object_id = request.POST.get("delete_id")
            obj = get_object_or_404(Lectura, id=object_id)
            obj.delete()
            messages.success(request, "Lectura eliminada exitosamente")
    elif atributo == "nota":
        object_id = request.POST.get("delete_id")
        obj = get_object_or_404(Nota, id=object_id)
        obj.delete()
        messages.success(request, "Nota eliminada exitosamente")
    return redirect(request.META.get("HTTP_REFERER", "/"))
