from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from tags.models import Etiqueta
from groups.models import Grupo, UsuarioGrupo
from dictionary.models import Palabra
from progress.models import UsuarioPalabra


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "study/home.html"

    def crear_grupos_nuevos_del_admin(self):
        usuario = self.request.user
        ids_objetivo = set(
            Grupo.objects.filter(
                Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
            ).values_list("id", flat=True)
        )  # que registro sea de admin o de usuario
        ids_existentes = set(
            UsuarioGrupo.objects.filter(usuario=usuario).values_list(
                "grupo_id", flat=True
            )
        )  # registros ya en tabla relacional
        ids_nuevos = ids_objetivo - ids_existentes

        if ids_nuevos:

            grupos_nuevos = Grupo.objects.filter(id__in=ids_nuevos).order_by("id")

            for grupo in grupos_nuevos:
                UsuarioGrupo.objects.create(
                    usuario=usuario,
                    grupo=grupo,
                    estudiando=False,
                    estrella=False,
                )

    def crear_palabras_nuevas_del_admin(self):
        usuario = self.request.user
        ids_objetivo = set(
            Palabra.objects.filter(
                Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
            ).values_list("id", flat=True)
        )  # que registro sea de admin o de usuario
        ids_existentes = set(
            UsuarioPalabra.objects.filter(usuario=usuario).values_list(
                "palabra_id", flat=True
            )
        )  # registros ya en tabla relacional
        ids_nuevos = ids_objetivo - ids_existentes

        if ids_nuevos:

            palabras_nuevas = Palabra.objects.filter(id__in=ids_nuevos).order_by("id")

            for palabra in palabras_nuevas:
                UsuarioPalabra.objects.create(
                    usuario=usuario,
                    palabra=palabra,
                    progreso=0,
                    estrella=False,
                )

    def get_context_data(self, **kwargs):
        usuario = self.request.user
        self.crear_palabras_nuevas_del_admin()
        self.crear_grupos_nuevos_del_admin()
        context = super().get_context_data(**kwargs)
        context["href_estudio"] = reverse_lazy("estudio")
        context["preguntas"] = ("Original", "Traducción", "Cualquiera")
        context["orden"] = ("Nombre", "Progreso")
        context["tags"] = Etiqueta.objects.filter(
            Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
        ).order_by("etiqueta")
        usuario_grupos = UsuarioGrupo.objects.filter(
            Q(usuario=usuario) | Q(usuario__perfil__rol="admin")
        ).order_by("id")
        grupos = []
        for ug in usuario_grupos:
            temp = {
                "text": ug.grupo.grupo,
                "progreso": int(ug.progreso),
                "estrella": ug.estrella,
                "estudiando": ug.estudiando,
            }
            grupos.append(temp)
        context["grupos"] = grupos
        return context

    def is_mobile(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        return any(m in user_agent for m in ["mobile", "android", "iphone", "ipad"])
