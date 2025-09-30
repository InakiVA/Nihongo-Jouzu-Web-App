from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

from dictionary.models import Palabra, Significado, Lectura, Nota
from progress.models import UsuarioPalabra
from groups.models import Grupo
from tags.models import Etiqueta, PalabraEtiqueta


# && debe tener por lo menos 1 lectura y 1 significado
@require_POST
@login_required
def crear_palabra(request, tipo):
    ajustes_palabras = request.session.get("ajustes_palabras")
    breaker = False
    if tipo == "vocabulario":
        text_warning = "palabra"
        palabra_value = request.POST.get("palabra_nueva")
        significado_value = request.POST.get("significado_nuevo")
        lectura_value = request.POST.get("lectura_nueva")
    elif tipo == "kanji":
        text_warning = "kanji"
        palabra_value = request.POST.get("kanji_nuevo")
        significado_value = request.POST.get("ksignificado_nuevo")
        lectura_value = request.POST.get("klectura_nueva")

    if "<" in palabra_value or ">" in palabra_value:
        messages.warning(
            request, f"{text_warning.capitalize()} no puede contener '<' o '>'"
        )
        breaker = True
    if "<" in significado_value or ">" in significado_value:
        messages.warning(
            request, f"Significado de {text_warning} no puede contener '<' o '>'"
        )
        breaker = True
    if "<" in lectura_value or ">" in lectura_value:
        messages.warning(
            request, f"Lectura de {text_warning} no puede contener '<' o '>'"
        )
        breaker = True

    if not all([palabra_value, significado_value, lectura_value]) or (breaker):
        if tipo == "vocabulario":
            for key, value in zip(
                ["palabra_valida", "significado_valido", "lectura_valida"],
                [palabra_value, significado_value, lectura_value],
            ):
                ajustes_palabras[key] = value
        elif tipo == "kanji":
            for key, value in zip(
                ["kanji_valido", "ksignificado_valido", "klectura_valida"],
                [palabra_value, significado_value, lectura_value],
            ):
                ajustes_palabras[key] = value
        request.session["ajustes_palabras"] = ajustes_palabras
        if not palabra_value:
            messages.error(request, f"Favor de ingresar {text_warning}")
        if not significado_value:
            messages.error(request, f"Favor de ingresar significado de {text_warning}")
        if not lectura_value:
            messages.error(request, f"Favor de ingresar lectura de {text_warning}")
        return redirect(request.META.get("HTTP_REFERER", "/"))
    for key, value in zip(
        ["palabra_valida", "significado_valido", "lectura_valida"],
        ["", "", ""],
    ):
        ajustes_palabras[key] = value
    user = request.user

    existent = Palabra.objects.filter(
        Q(palabra=palabra_value)
        & (Q(usuario=request.user) | Q(usuario__perfil__rol="admin"))
    ).all()

    if tipo == "kanji":
        existent = existent.filter(palabra_etiquetas__etiqueta__etiqueta="Kanji")
    elif tipo == "vocabulario":
        existent = existent.exclude(palabra_etiquetas__etiqueta__etiqueta="Kanji")

    if existent.exists():
        existent_id = existent.first().id
        request.session["palabra_actual"] = existent_id
        messages.info(
            request, f"{text_warning.capitalize()} ya existe. Redirigiendo a editar..."
        )
        return redirect("editar_palabra")

    palabra_obj = Palabra.objects.create(usuario=user, palabra=palabra_value)
    UsuarioPalabra.objects.create(usuario=user, palabra=palabra_obj)
    Significado.objects.create(
        significado=significado_value, palabra=palabra_obj, usuario=user
    )
    Lectura.objects.create(lectura=lectura_value, palabra=palabra_obj, usuario=user)
    if tipo == "kanji":
        kanji_tag = Etiqueta.objects.filter(etiqueta="Kanji").first()
        PalabraEtiqueta.objects.create(
            palabra=palabra_obj, etiqueta=kanji_tag, usuario=user
        )
    request.session["palabra_actual"] = palabra_obj.id
    request.session["ajustes_palabras"] = ajustes_palabras
    messages.success(request, "Palabra creada exitosamente")
    return redirect("editar_palabra")


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
        if not value:
            messages.warning(
                request, "No se ingresó información de palabra para actualizar"
            )
            return redirect(request.META.get("HTTP_REFERER", "/"))
        if value == palabra_obj.palabra:
            messages.info(request, "La palabra es la misma")
            return redirect(request.META.get("HTTP_REFERER", "/"))
        if "<" in value or ">" in value:
            messages.warning(request, "Palabra no puede contener '<' o '>'")
            return redirect(request.META.get("HTTP_REFERER", "/"))
        if "Kanji" in palabra_obj.etiquetas_list(user):
            existing = Palabra.objects.filter(
                Q(palabra=value)
                & (Q(usuario=request.user) | Q(usuario__perfil__rol="admin"))
                & Q(palabra_etiquetas__etiqueta__etiqueta="Kanji")
            ).exists()
            if existing:
                messages.warning(request, "Este kanji ya existe. Debe ser único")
                return redirect(request.META.get("HTTP_REFERER", "/"))
        else:
            existing = (
                Palabra.objects.filter(
                    Q(palabra=value)
                    & (Q(usuario=request.user) | Q(usuario__perfil__rol="admin"))
                )
                .exclude(palabra_etiquetas__etiqueta__etiqueta="Kanji")
                .exists()
            )
            if existing:
                messages.warning(request, "Esta palabra ya existe. Debe ser única")
                return redirect(request.META.get("HTTP_REFERER", "/"))
        palabra_obj.update_palabra(value)
        messages.success(request, "Palabra actualizada exitosamente")
    else:
        value = request.POST.get("input_id")
        if not value:
            messages.warning(
                request, f"No se ingresó información de {atributo} para actualizar"
            )
            return redirect(request.META.get("HTTP_REFERER", "/"))
        if "<" in value or ">" in value:
            messages.warning(
                request, f"{atributo.capitalize()} no puede contener '<' o '>'"
            )
            return redirect(request.META.get("HTTP_REFERER", "/"))
        object_id = request.POST.get("input_button_id")
        if atributo == "significado":
            obj = get_object_or_404(Significado, id=object_id)
            if value == obj.significado:
                messages.info(request, "El significado es el mismo")
            else:
                obj.update_significado(value)
                messages.success(request, "Significado actualizado exitosamente")
        elif atributo == "lectura":
            obj = get_object_or_404(Lectura, id=object_id)
            if value == obj.lectura:
                messages.info(request, "La lectura es la misma")
            else:
                obj.update_lectura(value)
                messages.success(request, "Lectura actualizada exitosamente")
        elif atributo == "nota":
            obj = get_object_or_404(Nota, id=object_id)
            if value == obj.nota:
                messages.info(request, "La nota es la misma")
            else:
                obj.update_nota(value)
                messages.success(request, "Nota actualizada exitosamente")
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
